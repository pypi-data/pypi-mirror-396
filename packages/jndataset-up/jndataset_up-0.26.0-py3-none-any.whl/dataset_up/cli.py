import click

from dataset_up.config.constants import SERVER_URL,TASK_URL,VERSION
from dataset_up.client.Client import Client
from dataset_up.client.AuthClient import auth_client
from dataset_up.uploader.uploader import Uploader
from dataset_up.update.update_check import update_check
from dataset_up.utils.interrupt_utils import register_signal_handler
from dataset_up.utils.output_format import print_file_list
from dataset_up.utils.system_utils import stop_dataset_up_process

def validate_input(ctx, param, value):
    if not value or value.strip() == "":
        raise click.BadParameter("input can not be blank")
    return value


@click.group()
def cli():
    pass


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def cli(ctx, version):
    if version:
        click.echo(f"{VERSION}")
        ctx.exit()


@cli.command()
@click.option("--dataset-id", required=True, help="dataset ID",callback=validate_input)
@click.option("--source-path", required=True, help="local path",callback=validate_input)
@click.option("--target-path", default="/", help="target path",callback=validate_input)
@click.option("--version", default="master", help="version ",callback=validate_input)
@click.option("--enable-calc-sha256", is_flag=True, default=False, help="whether to calculate the sha256 value of the file,True yes,False no,default is False")
@click.option("--enable-inner-network", is_flag=True, default=False, help="whether to use the inner network to upload,True yes,False no,default is False")
def upload_file(dataset_id, source_path, target_path, version,enable_calc_sha256,enable_inner_network):
    """upload a file"""
    try:
        register_signal_handler()
        update_check()
        client = Client(host=SERVER_URL,task_host=TASK_URL)
        uploader = Uploader(client, dataset_id, version,calc_sha256=enable_calc_sha256,enable_inner_network=enable_inner_network)
        uploader.upload_file(source_path, target_path)
    except Exception as e:
        click.echo(f"upload file failed: {e}")


@cli.command()
@click.option("--dataset-id", required=True, help="dataset ID",callback=validate_input)
@click.option("--source-path", required=True, help="local folder path",callback=validate_input)
@click.option("--target-path", default="/",  required = True,help="target path",callback=validate_input)
@click.option("--version", default="master", help="version",callback=validate_input)
@click.option("--enable-calc-sha256", is_flag=True, default=False, help="whether to calculate the sha256 value of the file,True yes,False no,default is False")
@click.option("--enable-inner-network", is_flag=True, default=False, help="whether to use the inner network to upload,True yes,False no,default is False")
def upload_folder(dataset_id, source_path, target_path, version,enable_calc_sha256,enable_inner_network):
    """upload a folder"""
    try:
        register_signal_handler()
        update_check()
        client = Client(host=SERVER_URL,task_host=TASK_URL)
        uploader = Uploader(client, dataset_id, version,calc_sha256=enable_calc_sha256,enable_inner_network=enable_inner_network)
        uploader.upload_folder(source_path, target_path)
    except Exception as e:
        click.echo(f"upload folder failed: {e}")
        
@cli.command()
@click.option("--dataset-id", required=True, help="dataset ID",callback=validate_input)
@click.option("--version", default="master" ,help="version",callback=validate_input)
@click.option("--dir", required = True, help="target path",callback=validate_input)
def mkdir(dataset_id, version, dir):
    """create a directory"""
    try:
        register_signal_handler()
        update_check()
        client = Client(host=SERVER_URL,task_host=TASK_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.mkdir(dir)
        click.echo(f"create directory {dir} success")
    except Exception as e:
        click.echo(f"create directory {dir} failed: {e}")

@cli.command()
@click.option("--dataset-id", required=True, help="dataset ID",callback=validate_input)
@click.option("--version", default="master" ,help="version",callback=validate_input)
@click.option("--dir", required = True, help="target path",callback=validate_input)
def rmdir(dataset_id, version, dir):
    """delete a directory"""
    try:
        register_signal_handler()
        update_check()
        client = Client(host=SERVER_URL,task_host= TASK_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.deleteDir(dir)
        click.echo(f"delete directory {dir} success")
    except Exception as e:
        click.echo(f"delete directory {dir} failed: {e}")
        

@cli.command()
@click.option("--dataset-id", required=True, help="dataset ID",callback=validate_input)
@click.option("--version", default="master" ,help="version",callback=validate_input)
@click.option("--file", required = True, help="target path",callback=validate_input)
def delete_file(dataset_id, version, file):
    """delete a file"""
    try:
        register_signal_handler()
        update_check()
        client = Client(host=SERVER_URL,task_host= TASK_URL)
        uploader = Uploader(client, dataset_id, version)
        uploader.deleteFile(file)
        click.echo(f"delete file {file} success")
    except Exception as e:
        click.echo(f"delete file {file} failed: {e}")


@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--version", default="master", help="版本",callback=validate_input)
@click.option("--dir", default="/", help="目标路径",callback=validate_input)
def list(dataset_id: str, version: str, dir: str):
    """list content of a directory recursively"""
    try:
        register_signal_handler()
        update_check()
        client = Client(host=SERVER_URL,task_host= TASK_URL)
        uploader = Uploader(client, dataset_id, version)
        files = uploader.list(dir)
        print_file_list(files)
    except Exception as e:
        click.echo(f"list {dir} failed: {e}")


@cli.command()
@click.option("--ak", required=True, help="Access Key")
@click.option("--sk", required=True, help="Secret Key")
def login(ak: str, sk: str):
    """login"""
    try:
        auth_client.login(ak, sk)
        update_check()
        click.echo("login success")
    except Exception as e:
        click.echo(f"login failed,please check AK/SK! msg: {e}")



@cli.command()
def stop_running_uploading_process():
    """stop the running uploading process"""
    stop_dataset_up_process()


def main():
    cli()


if __name__ == "__main__":
    main()