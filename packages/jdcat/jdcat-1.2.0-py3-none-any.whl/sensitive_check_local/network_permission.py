"""
macOS本地网络权限检查和申请模块

该模块负责在需要时触发macOS的本地网络权限申请对话框。
主要用于在用户首次启用代理功能时申请权限，而不是在应用启动时。
"""

import socket
import threading
import time
import logging
from typing import Optional

_logger = logging.getLogger("sensitive_check_local.network_permission")


def _trigger_local_network_permission() -> bool:
    """
    触发macOS本地网络权限申请对话框。
    
    通过尝试绑定到多个网络接口来触发权限申请。
    这会让macOS显示"本地网络"权限申请对话框。
    
    Returns:
        bool: 是否成功触发权限申请（不代表用户是否授权）
    """
    try:
        _logger.info("正在触发本地网络权限申请...")
        
        # 方法1: 尝试绑定到0.0.0.0来触发权限申请
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # 尝试绑定到所有接口的临时端口
                sock.bind(('0.0.0.0', 0))
                actual_port = sock.getsockname()[1]
                _logger.info(f"成功绑定到0.0.0.0:{actual_port}，这应该触发本地网络权限申请")
                time.sleep(0.5)  # 给系统一点时间来显示权限对话框
        except Exception as e:
            _logger.debug(f"绑定0.0.0.0失败: {e}")
        
        # 方法2: 尝试UDP广播来触发权限申请
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.settimeout(1.0)
                # 尝试发送广播包（这通常会触发本地网络权限申请）
                sock.sendto(b'JDCat-network-permission-test', ('255.255.255.255', 17867))
                _logger.info("发送了UDP广播包，这应该触发本地网络权限申请")
        except Exception as e:
            _logger.debug(f"UDP广播失败: {e}")
        
        # 方法3: 尝试多播来触发权限申请
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
                # 发送到本地多播地址
                sock.sendto(b'JDCat-multicast-test', ('224.0.0.1', 17868))
                _logger.info("发送了多播包，这应该触发本地网络权限申请")
        except Exception as e:
            _logger.debug(f"多播失败: {e}")
        
        _logger.info("本地网络权限触发操作完成")
        return True
        
    except Exception as e:
        _logger.error(f"触发本地网络权限申请失败: {e}")
        return False


def request_local_network_permission() -> bool:
    """
    请求本地网络权限。
    
    这个函数应该在用户首次尝试启用代理功能时调用。
    它会尝试触发macOS的本地网络权限申请对话框。
    
    Returns:
        bool: 是否成功请求权限（不代表用户是否授权）
    """
    _logger.info("开始请求本地网络权限...")
    
    # 在后台线程中触发权限申请，避免阻塞主线程
    def trigger_permission():
        _trigger_local_network_permission()
    
    permission_thread = threading.Thread(target=trigger_permission, daemon=True)
    permission_thread.start()
    
    # 等待一小段时间让权限申请对话框显示
    permission_thread.join(timeout=2.0)
    
    return True


def check_local_network_permission() -> Optional[bool]:
    """
    检查本地网络权限状态。
    
    注意：macOS没有直接的API来检查本地网络权限状态，
    所以这个函数主要是尝试执行网络操作来间接判断。
    
    Returns:
        Optional[bool]: 
            True - 可能有权限
            False - 可能没有权限  
            None - 无法确定
    """
    try:
        # 尝试简单的网络操作来检查权限
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            # 尝试连接到本地服务（如果存在）
            try:
                sock.connect(('127.0.0.1', 17866))
                return True
            except (ConnectionRefusedError, socket.timeout):
                # 连接被拒绝或超时是正常的，说明网络功能可用
                return True
            except Exception:
                # 其他错误可能表示权限问题
                return False
    except Exception as e:
        _logger.debug(f"权限检查失败: {e}")
        return None