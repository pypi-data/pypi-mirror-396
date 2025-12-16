import os
import uuid
import hashlib
import shutil
from typing import Dict, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Path, HTTPException
from pydantic import BaseModel

app = FastAPI()

chunk_size = 16*1024*1024
chunks_dir_prefix = "chunks"
chunk_file_prefix = "chunk_"




def delete_all_in_directory_with_subdirs(directory_path):
    """删除目录下的所有文件和子目录"""
    if os.path.exists(directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # 删除文件或链接
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # 删除子目录及其内容
            except Exception as e:
                print(f"删除 {item_path} 失败: {e}")


def list_files_in_directory(directory_path):
    """列出目录下的所有文件（不包括子目录）"""
    files = []
    if os.path.exists(directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                files.append(item)
    return files



def split_file(size: int, chunk_size: int):
    parts = []
    chunk_num = size // chunk_size
    if  size % chunk_size > 0:
        chunk_num += 1
    
    for i in range(chunk_num):
        parts.append({
            "chunk_num": i,
            "start": i * chunk_size,
            "end": min(size, chunk_size * (i + 1))
        })
    return parts


def get_md5(file_path):
    """计算文件的MD5值"""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

class MultipartUpload:
    def __init__(self,bucket: str,key:str,size: int,md5:str,content_type: str):
        self.bucket = bucket
        self.key = key
        self.size = size
        self.md5 = md5
        self.content_type = content_type
        self.upload_id = str(uuid.uuid4())
        self.chunks = split_file(size, chunk_size)
        self.parts: Dict[int,dict] = {}
        self.completed = False
        
class CompleteMultipartUploadRequest(BaseModel):
    parts: List[dict]  # [{ "ETag": "...", "PartNumber": 1 }]

        
# 内存中的上传状态存储（生产环境应使用数据库）
uploads: Dict[str, MultipartUpload] = {}



@app.post("/buckets/{bucket}/objects/{key:path}/uploads")
async def create_multipart_upload(
    bucket: str = Path(...),
    key: str = Path(...),
    md5: str = Form(...),
    size: int = Form(...),
    content_type: str = Form(...),
    
):
    print("create_multipart_upload")
    if key.startswith("/"):
        key = key[1:]
    file_path = f"{bucket}/{key}"
    if os.path.exists(file_path):
        if os.path.getsize(file_path) != size or (md5 is not None and md5 != hashlib.md5(open(file_path, "rb").read()).hexdigest()):
            os.remove(file_path)
            chunks_dir = os.path.join(chunks_dir_prefix,file_path)
            delete_all_in_directory_with_subdirs(chunks_dir)
            del uploads[file_path]
    
    if os.path.exists(file_path):  # 文件已存在
        return {
            "bucket": bucket,
            "key": key,
            "exist": True,
            "resume": False
        }
        
    if file_path in uploads:
        upload = uploads[file_path]
        chunks_dir = os.path.join(chunks_dir_prefix,file_path)
        if upload.size != size or (not md5  and not upload.md5 and md5 != upload.md5):
            delete_all_in_directory_with_subdirs(chunks_dir)
            del uploads[file_path]
            upload = MultipartUpload(bucket, key,size=size,md5=md5,content_type=content_type)
            uploads[file_path] = upload     
            return {
                "uploadId": upload.upload_id,
                "bucket": bucket,
                "key": key,
                "exist": False,
                "resume": False,
                "chunks": upload.chunks
            }
        
        
        else:  # 文件已存在且大小和MD5一致
            chunk_paths = list_files_in_directory(chunks_dir)
            chunks_to_upload = [i for i in range(len(upload.chunks))]
            
            for chunk_path in chunk_paths:
                file_name = os.path.basename(chunk_path)
                chunk_num = int(file_name[len(chunk_file_prefix):])
                
                if os.path.getsize(chunk_path) != upload.chunks[chunk_num]["end"] - upload.chunks[chunk_num]["start"]  \
                        or (chunk_num not in upload.parts) \
                        or (chunk_num in upload.parts and upload.parts[chunk_num]["path"] != chunk_path) \
                        or (chunk_num in upload.parts and upload.parts[chunk_num]["eTag"] != get_md5(chunk_path)):# 分片大小不一致
                    os.remove(chunk_path)
                    del upload.parts[chunk_num]
                else:
                    chunks_to_upload.remove(chunk_num)
                    
            return {
                    "uploadId": upload.upload_id,
                    "bucket": bucket,
                    "key": key,
                    "exist": False,
                    "resume": True,
                    "chunks": [item for item in upload.chunks if item["chunk_num"] in chunks_to_upload ],
                }
    else:
        upload = MultipartUpload(bucket, key,size=size,md5=md5,content_type=content_type)
        uploads[file_path] = upload     
    
    return {
        "uploadId": upload.upload_id,
        "bucket": bucket,
        "key": key,
        "exist": False,
        "resume": False,
        "chunks": upload.chunks
    }
    
    
    
@app.put("/buckets/{bucket}/objects/{key:path}/uploads/{uploadId}/parts")
async def upload_part(
    bucket: str = Path(...),
    key: str = Path(...),
    uploadId: str = Path(...),
    partNumber: int = Form(...),
    file: UploadFile = File(...)
):
    
    """上传单个分片"""
    if key.startswith("/"):
        key = key[1:]
    file_path = f"{bucket}/{key}"
    
    
    if file_path not in uploads:
        raise HTTPException(status_code=404, detail=f"Upload file_path {file_path} not found")
    
    upload = uploads[file_path]
    if upload.completed:
        raise HTTPException(status_code=400, detail="Upload already completed")
    
    # 保存分片到本地文件系统
    part_filename = f"{chunk_file_prefix}{partNumber}"
    part_dir = os.path.join(chunks_dir_prefix, os.path.join(bucket, key))
    part_path = os.path.join(part_dir ,part_filename)
    
    # 确保目录存在
    os.makedirs(part_dir, exist_ok=True)
    
    content = await file.read()
    with open(part_path, "wb") as f:
        f.write(content)
    
    # 计算ETag (MD5)
    etag = hashlib.md5(content).hexdigest()
    
    upload.parts[partNumber] = {
        "etag": etag,
        "size": len(content),
        "path": part_path
    }
    
    return {"ETag": etag}


@app.post("/buckets/{bucket}/objects/{key:path}/uploads/{uploadId}/complete")
async def complete_multipart_upload(
    request: CompleteMultipartUploadRequest,
    bucket: str = Path(...),
    key: str = Path(...),
    uploadId: str = Path(...)
):
    print("complete_multipart_upload")
    
    """完成分片上传"""
    if uploadId not in uploads:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = uploads[uploadId]
    
    # 验证所有分片都已上传
    expected_parts = set(part["PartNumber"] for part in request.parts)
    actual_parts = set(upload.parts.keys())
    
    if expected_parts != actual_parts:
        raise HTTPException(status_code=400, detail="Parts mismatch")
    
    # 按照分片顺序合并文件
    os.makedirs(f"buckets/{bucket}", exist_ok=True)
    final_path = f"buckets/{bucket}/{key}"
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    
    
    with open(final_path, "wb") as final_file:
        # 按分片编号排序
        sorted_parts = sorted(upload.parts.items())
        for part_number, part_info in sorted_parts:
            with open(part_info["path"], "rb") as part_file:
                final_file.write(part_file.read())
            
            # 清理临时分片文件
            os.remove(part_info["path"])
    
    upload.completed = True
    
    return {
        "Location": f"http://localhost:8000/{bucket}/{key}",
        "Bucket": bucket,
        "Key": key,
        "ETag": '"' + hashlib.md5(open(final_path, "rb").read()).hexdigest() + '"'
    }
    

@app.delete("/buckets/{bucket}/objects/{key:path}/uploads/{uploadId}")
async def abort_multipart_upload(
    bucket: str = Path(...),
    key: str = Path(...),
    uploadId: str = Path(...)
):
    """取消分片上传"""
    if uploadId not in uploads:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = uploads[uploadId]
    
    # 删除所有分片文件
    for part_info in upload.parts.values():
        if os.path.exists(part_info["path"]):
            os.remove(part_info["path"])
    
    del uploads[uploadId]
    
    return {"message": "Upload aborted"}



@app.get("/buckets/{bucket}/objects/{key:path}/uploads/{uploadId}/parts")
async def list_parts(
    bucket: str = Path(...),
    key: str = Path(...),
    uploadId: str = Path(...)
):
    """列出已上传的分片"""
    if uploadId not in uploads:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = uploads[uploadId]
    
    parts_list = []
    for part_number, part_info in upload.parts.items():
        parts_list.append({
            "PartNumber": part_number,
            "ETag": part_info["etag"],
            "Size": part_info["size"]
        })
    
    return {
        "Parts": sorted(parts_list, key=lambda x: x["PartNumber"])
    }