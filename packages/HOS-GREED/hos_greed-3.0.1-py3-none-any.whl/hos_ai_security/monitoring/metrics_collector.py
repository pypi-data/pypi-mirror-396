from typing import Dict, Any, List
import logging
import time
import psutil
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class MetricsCollector:
    """监控数据收集器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.total_response_time = 0
        self.avg_response_time = 0
        self.active_requests = 0
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统级指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024 * 1024 * 1024)  # 转换为 GB
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024 * 1024 * 1024)  # 转换为 GB
            
            # 网络 I/O
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent / (1024 * 1024)  # 转换为 MB
            bytes_recv = net_io.bytes_recv / (1024 * 1024)  # 转换为 MB
            
            # 进程数
            process_count = len(psutil.pids())
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used_gb": round(memory_used, 2),
                "disk_percent": disk_percent,
                "disk_used_gb": round(disk_used, 2),
                "network_bytes_sent_mb": round(bytes_sent, 2),
                "network_bytes_recv_mb": round(bytes_recv, 2),
                "process_count": process_count
            }
        except Exception as e:
            logger.error(f"系统指标收集失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def collect_service_metrics(self) -> Dict[str, Any]:
        """收集服务级指标"""
        try:
            # 计算正常运行时间
            uptime = time.time() - self.start_time
            
            # 计算平均响应时间
            if self.request_count > 0:
                avg_response_time = self.total_response_time / self.request_count
            else:
                avg_response_time = 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": round(uptime, 2),
                "request_count": self.request_count,
                "success_count": self.success_count,
                "error_count": self.error_count,
                "success_rate": round(self.success_count / self.request_count * 100, 2) if self.request_count > 0 else 0,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "active_requests": self.active_requests
            }
        except Exception as e:
            logger.error(f"服务指标收集失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def collect_api_metrics(self, endpoint: str, method: str, status_code: int, response_time: float) -> Dict[str, Any]:
        """收集API级指标"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": round(response_time * 1000, 2)
            }
        except Exception as e:
            logger.error(f"API指标收集失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def record_request(self, success: bool, response_time: float) -> None:
        """记录请求信息"""
        self.request_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        self.total_response_time += response_time
    
    def increment_active_requests(self) -> None:
        """增加活跃请求数"""
        self.active_requests += 1
    
    def decrement_active_requests(self) -> None:
        """减少活跃请求数"""
        if self.active_requests > 0:
            self.active_requests -= 1
    
    def reset_metrics(self) -> None:
        """重置指标"""
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.total_response_time = 0
        self.avg_response_time = 0
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有监控指标"""
        return {
            "system": self.collect_system_metrics(),
            "service": self.collect_service_metrics(),
            "timestamp": datetime.now().isoformat()
        }

# 创建全局监控数据收集器实例
metrics_collector = MetricsCollector()
