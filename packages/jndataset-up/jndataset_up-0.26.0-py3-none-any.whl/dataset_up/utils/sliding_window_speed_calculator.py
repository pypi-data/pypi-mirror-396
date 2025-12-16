class SlidingWindowSpeedCalculator:
    """
    滑动窗口速度计算器
    用于计算基于滑动窗口的上传速度
    """
    
    def __init__(self, window_size=60):
        """
        初始化滑动窗口速度计算器
        
        Args:
            window_size: 窗口大小(秒),默认60秒
        """
        self.window_size = window_size
        self.history = []  # 存储 (时间, 已处理字节数) 的元组列表
    
    def add_record(self, timestamp, processed_bytes):
        """
        添加记录点
        
        Args:
            timestamp: 时间戳
            processed_bytes: 已处理的字节数
        """
        self.history.append((timestamp, processed_bytes))
        # 移除超出窗口大小的旧记录
        self._clean_old_records(timestamp)
    
    def _clean_old_records(self, current_time):
        """
        清理超出窗口大小的旧记录
        
        Args:
            current_time: 当前时间戳
        """
        # 保留窗口期内的数据
        cutoff_time = current_time - self.window_size
        while self.history and self.history[0][0] < cutoff_time:
            self.history.pop(0)
    
    def get_speed(self, current_time=None):
        """
        计算滑动窗口内的速度（字节/秒）
        
        Args:
            current_time: 当前时间戳,如果为None则使用最新的记录时间
            
        Returns:
            float: 速度（字节/秒),如果无法计算则返回0
        """
        if not self.history:
            return 0
            
        if current_time is None:
            current_time = self.history[-1][0]
            
        # 清理旧记录
        self._clean_old_records(current_time)
        
        # 至少需要两个点才能计算速度
        if len(self.history) < 2:
            return 0
            
        # 计算窗口期内的速度
        time_diff = self.history[-1][0] - self.history[0][0]
        bytes_diff = self.history[-1][1] - self.history[0][1]
        
        if time_diff <= 0 or bytes_diff <= 0:
            return 0
            
        return bytes_diff / time_diff
    
    def get_remaining_time(self, total_bytes, current_time=None):
        """
        计算剩余时间
        
        Args:
            total_bytes: 总字节数
            current_time: 当前时间戳
            
        Returns:
            float: 剩余时间(秒),如果无法计算则返回0
        """
        speed = self.get_speed(current_time)
        if speed <= 0:
            return 0
            
        processed_bytes = self.history[-1][1] if self.history else 0
        remaining_bytes = total_bytes - processed_bytes
        
        if remaining_bytes <= 0:
            return 0
            
        return remaining_bytes / speed