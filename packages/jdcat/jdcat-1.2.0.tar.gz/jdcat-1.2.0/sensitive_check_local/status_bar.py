#!/usr/bin/env python3
"""
Mac状态栏管理器
使用rumps库创建Mac状态栏图标和菜单，解决启动台跳动问题
"""

import rumps
import threading
import webbrowser
import sys
import os
from typing import Optional, Callable
import logging


class SensitiveCheckStatusBar:
    """
    Mac状态栏应用类
    
    提供状态栏图标、菜单和服务状态监控功能
    """
    
    def __init__(self, launcher_instance=None):
        """
        初始化状态栏应用
        
        Args:
            launcher_instance: SensitiveCheckLocalLauncher实例，用于控制服务
        """
        self.launcher = launcher_instance
        self.logger = logging.getLogger(__name__)
        
        # 创建rumps应用
        # 获取状态栏图标路径
        icon_path = self._get_status_bar_icon_path()
        
        self.app = rumps.App(
            name="JDCat",
            title=None,  # 使用图标而不是文字
            icon=icon_path,  # 使用自定义状态栏图标
            template=True,  # 使用模板模式，适应系统主题
            menu=None,
            quit_button=None  # 禁用默认退出按钮
        )
        
        # 服务配置
        self.host = "aq.jdtest.net"
        self.port = 8007
        self.service_url = f"http://{self.host}:{self.port}/"
        
        # 设置菜单
        self._setup_menu()
        
    def _setup_menu(self):
        """设置状态栏菜单"""
        # 服务状态显示
        self.status_item = rumps.MenuItem("🔴 服务未启动")
        
        # 服务地址显示
        self.url_item = rumps.MenuItem(f"📍 服务地址: {self.service_url}")
        
        # 功能菜单项
        self.open_web_item = rumps.MenuItem("🌐 打开Web界面", callback=self.open_web_interface)
        self.open_docs_item = rumps.MenuItem("📖 查看API文档", callback=self.open_api_docs)
        
        # 分隔符
        separator1 = rumps.separator
        
        # 证书管理菜单
        self.cert_status_item = rumps.MenuItem("🔒 证书状态: 检查中...")
        self.regenerate_cert_item = rumps.MenuItem("🔄 重新生成证书", callback=self.regenerate_certificate)
        self.open_cert_dir_item = rumps.MenuItem("📂 打开证书目录", callback=self.open_certificate_directory)
        
        # 分隔符
        separator2 = rumps.separator
        
        # 应用信息
        self.version_item = rumps.MenuItem("ℹ️ 版本: 1.0.0")
        
        # 分隔符
        separator3 = rumps.separator
        
        # 退出按钮
        self.quit_item = rumps.MenuItem("❌ 退出应用", callback=self.quit_application)
        
        # 组装菜单
        self.app.menu = [
            self.status_item,
            self.url_item,
            separator1,
            self.open_web_item,
            self.open_docs_item,
            separator2,
            self.cert_status_item,
            self.regenerate_cert_item,
            self.open_cert_dir_item,
            separator3,
            self.version_item,
            separator3,
            self.quit_item
        ]
        
        # 初始化证书状态
        self._update_certificate_status()
        
    def update_status(self, is_running: bool):
        """
        更新服务状态显示
        
        Args:
            is_running: 服务是否正在运行
        """
        if is_running:
            self.status_item.title = "🟢 服务运行中"
            # 不设置title，只使用图标文件
            self.open_web_item.set_callback(self.open_web_interface)
            self.open_docs_item.set_callback(self.open_api_docs)
        else:
            self.status_item.title = "🔴 服务未启动"
            # 不设置title，只使用图标文件
            self.open_web_item.set_callback(None)  # 禁用菜单项
            self.open_docs_item.set_callback(None)
            
    def open_web_interface(self, sender=None):
        """打开Web界面"""
        try:
            webbrowser.open(self.service_url)
            self.logger.info(f"Opened web interface: {self.service_url}")
        except Exception as e:
            self.logger.error(f"Failed to open web interface: {e}")
            self._show_notification("错误", f"无法打开Web界面: {e}")
            
    def open_api_docs(self, sender=None):
        """打开API文档"""
        try:
            docs_url = f"{self.service_url}/docs"
            webbrowser.open(docs_url)
            self.logger.info(f"Opened API docs: {docs_url}")
        except Exception as e:
            self.logger.error(f"Failed to open API docs: {e}")
            self._show_notification("错误", f"无法打开API文档: {e}")
    
    def regenerate_certificate(self, sender=None):
        """重新生成MITM证书"""
        try:
            self.logger.info("User requested certificate regeneration")
            
            # 显示开始通知
            self._show_notification("证书重新生成", "正在重新生成MITM证书，请稍候...")
            
            # 导入证书管理器
            from .cert_manager import get_certificate_manager
            cert_manager = get_certificate_manager()
            
            # 在后台线程中执行证书重新生成
            def regenerate_in_background():
                try:
                    result = cert_manager.regenerate_certificates()
                    
                    if result['success']:
                        self.logger.info("Certificate regeneration successful")
                        
                        # 更新证书状态
                        self._update_certificate_status()
                        
                        # 显示成功通知
                        self._show_notification(
                            "证书重新生成成功",
                            "新的MITM证书已生成，请按提示重新信任证书"
                        )
                        
                        # 如果需要信任证书，显示安装指导并自动打开证书目录
                        if result.get('needs_trust', False):
                            self._show_certificate_trust_guide(result['certificate_info'])
                            # 用户主动重新生成证书时，自动打开证书目录
                            self.open_certificate_directory()
                            
                    else:
                        error_messages = "; ".join(result['messages'])
                        self.logger.error(f"Certificate regeneration failed: {error_messages}")
                        self._show_notification(
                            "证书重新生成失败",
                            f"生成失败: {error_messages[:100]}..."
                        )
                        
                except Exception as e:
                    self.logger.error(f"Certificate regeneration error: {e}")
                    self._show_notification("证书重新生成失败", f"发生错误: {str(e)}")
            
            # 在后台线程中执行
            import threading
            thread = threading.Thread(target=regenerate_in_background, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to regenerate certificate: {e}")
            self._show_notification("错误", f"无法重新生成证书: {e}")
    
    def open_certificate_directory(self, sender=None):
        """打开证书目录"""
        try:
            from .cert_manager import get_certificate_manager
            cert_manager = get_certificate_manager()
            
            cert_dir = str(cert_manager.mitmproxy_dir)
            
            # 确保目录存在
            cert_manager.ensure_mitmproxy_dir()
            
            # 打开目录
            import subprocess
            import platform
            if platform.system() == "Darwin":
                subprocess.run(['open', cert_dir], check=False)
                self.logger.info(f"Opened certificate directory: {cert_dir}")
                self._show_notification("证书目录", f"已打开证书目录")
            else:
                self.logger.warning("Opening directory only supported on macOS")
                self._show_notification("不支持", "仅在macOS上支持打开目录")
                
        except Exception as e:
            self.logger.error(f"Failed to open certificate directory: {e}")
            self._show_notification("错误", f"无法打开证书目录: {e}")
    
    def _update_certificate_status(self):
        """更新证书状态显示"""
        try:
            from .cert_manager import get_certificate_manager
            cert_manager = get_certificate_manager()
            
            cert_info = cert_manager.get_certificate_info()
            
            if cert_info['certificate_exists']:
                if cert_info.get('trusted_in_keychain', False):
                    self.cert_status_item.title = "🔒 证书状态: ✅ 已信任"
                else:
                    self.cert_status_item.title = "🔒 证书状态: ⚠️ 未信任"
            else:
                self.cert_status_item.title = "🔒 证书状态: ❌ 不存在"
                
        except Exception as e:
            self.logger.error(f"Failed to update certificate status: {e}")
            self.cert_status_item.title = "🔒 证书状态: ❓ 未知"
    
    def _show_certificate_trust_guide(self, cert_info):
        """显示证书信任指导"""
        try:
            # 通过系统通知显示简要指导
            self._show_notification(
                "需要信任新证书",
                "请查看证书目录中的'证书安装引导.txt'文件"
            )
            
            # 如果launcher实例存在，使用其显示详细指导
            if self.launcher and hasattr(self.launcher, 'display_certificate_trust_reminder'):
                # 在后台线程中显示详细指导，避免阻塞状态栏
                def show_guide():
                    try:
                        self.launcher.display_certificate_trust_reminder(cert_info)
                    except Exception as e:
                        self.logger.error(f"Failed to show certificate guide: {e}")
                
                import threading
                thread = threading.Thread(target=show_guide, daemon=True)
                thread.start()
                
        except Exception as e:
            self.logger.error(f"Failed to show certificate trust guide: {e}")
            
    def quit_application(self, sender=None):
        """退出应用"""
        self.logger.info("User requested application quit")
        
        # 显示退出确认通知
        self._show_notification("退出应用", "JDCat 正在关闭...")
        
        # 停止服务
        if self.launcher:
            self.launcher.shutdown()
            
        # 退出状态栏应用
        rumps.quit_application()
        
        # 强制退出进程
        sys.exit(0)
        
    def _get_status_bar_icon_path(self) -> Optional[str]:
        """
        获取状态栏图标路径
        
        Returns:
            状态栏图标的文件路径，如果找不到则返回None
        """
        import sys
        
        # 检测是否在PyInstaller打包环境中
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 在打包的应用中，资源文件位于 _MEIPASS/resources/ 目录
            base_dir = sys._MEIPASS
            resources_dir = os.path.join(base_dir, "resources")
        else:
            # 在开发环境中
            current_dir = os.path.dirname(os.path.abspath(__file__))
            resources_dir = os.path.join(os.path.dirname(current_dir), "resources")
        
        # 状态栏图标候选路径（按优先级排序）
        icon_candidates = [
            os.path.join(resources_dir, "icon-32.png"),  # 32x32适合状态栏
            os.path.join(resources_dir, "icon-64.png"),  # 备选
            os.path.join(resources_dir, "icon-128.png"), # 备选
        ]
        
        # 查找存在的图标文件
        for icon_path in icon_candidates:
            if os.path.exists(icon_path):
                logging.info(f"使用状态栏图标: {icon_path}")
                return icon_path
        
        logging.warning("未找到状态栏图标文件")
        logging.info(f"搜索的资源目录: {resources_dir}")
        logging.info(f"候选图标路径: {icon_candidates}")
        return None

    def _show_notification(self, title: str, message: str):
        """显示系统通知"""
        try:
            rumps.notification(
                title=title,
                subtitle="JDCat",
                message=message,
                sound=False
            )
            self.logger.info(f"Notification sent: {title} - {message}")
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
            
    def show_service_error(self, error_message: str):
        """显示服务错误通知"""
        self._show_notification(
            title="服务启动失败",
            message=f"JDCat服务无法启动: {error_message}"
        )
            
    def run_in_background(self):
        """准备状态栏应用运行（rumps必须在主线程运行）"""
        try:
            self.logger.info("Status bar application prepared for main thread execution")
            # rumps应用必须在主线程运行，这里只是准备工作
            return True
        except Exception as e:
            self.logger.error(f"Status bar preparation error: {e}")
            return False
        
    def start_monitoring(self, check_interval: int = 5):
        """
        开始监控服务状态
        
        Args:
            check_interval: 检查间隔（秒）
        """
        def monitor_service():
            import time
            import socket
            
            while True:
                try:
                    # 检查端口是否可访问
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        result = sock.connect_ex((self.host, self.port))
                        is_running = (result == 0)
                        
                    # 更新服务状态
                    self.update_status(is_running)
                    
                    # 定期更新证书状态
                    self._update_certificate_status()
                    
                except Exception as e:
                    self.logger.error(f"Service monitoring error: {e}")
                    self.update_status(False)
                    
                time.sleep(check_interval)
                
        # 在后台线程中监控服务
        monitor_thread = threading.Thread(target=monitor_service, daemon=True)
        monitor_thread.start()
        
        return monitor_thread


def create_status_bar_app(launcher_instance=None) -> SensitiveCheckStatusBar:
    """
    创建状态栏应用实例
    
    Args:
        launcher_instance: 启动器实例
        
    Returns:
        SensitiveCheckStatusBar: 状态栏应用实例
    """
    return SensitiveCheckStatusBar(launcher_instance)


# 用于测试的主函数
if __name__ == "__main__":
    # 只在直接运行此文件时才执行测试代码
    # 在PyInstaller打包环境中避免意外执行
    import sys
    if not getattr(sys, 'frozen', False):
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        print("🧪 测试模式：直接运行status_bar.py")
        print("⚠️ 注意：这将创建一个独立的状态栏应用用于测试")
        
        # 创建并运行状态栏应用
        status_bar = create_status_bar_app()
        
        # 启动监控
        status_bar.start_monitoring()
        
        # 运行状态栏应用
        status_bar.app.run()
    else:
        print("⚠️ 检测到PyInstaller打包环境，跳过测试代码执行")