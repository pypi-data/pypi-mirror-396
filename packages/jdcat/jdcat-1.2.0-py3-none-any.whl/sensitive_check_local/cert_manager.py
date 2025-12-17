"""
Certificate management for mitmproxy HTTPS interception.

This module provides persistent certificate management by using the standard
~/.mitmproxy/ directory, ensuring certificates survive app reinstallation.
"""

import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import datetime


class CertificateManager:
    """
    Manages mitmproxy certificates with persistent storage and system trust.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mitmproxy_dir = Path.home() / '.mitmproxy'
        self.ca_cert_path = self.mitmproxy_dir / 'mitmproxy-ca-cert.pem'
        self.ca_key_path = self.mitmproxy_dir / 'mitmproxy-ca.pem'
        
    def ensure_mitmproxy_dir(self) -> None:
        """Ensure ~/.mitmproxy directory exists."""
        self.mitmproxy_dir.mkdir(exist_ok=True)
        self.logger.info(f"Ensured mitmproxy directory exists: {self.mitmproxy_dir}")
        
        # 创建证书安装引导文件
        self._create_certificate_guide_file()
    
    def _create_certificate_guide_file(self) -> None:
        """创建证书安装引导文件"""
        guide_file_path = self.mitmproxy_dir / "证书安装引导.txt"
        
        guide_content = """🔒 JDCat HTTPS证书安装指南
============================================================

📍 需要安装的证书文件:
   📄 mitmproxy-ca-cert.pem
   📂 完整路径: {cert_path}

⚠️  重要说明:
   证书目录中有多个文件，请只安装 mitmproxy-ca-cert.pem 文件！
   其他文件（.p12、.cer、dhparam等）无需手动安装。

🔧 安装步骤:
1. 在当前目录中，找到 "mitmproxy-ca-cert.pem" 文件
2. 双击该文件，或拖拽到 "钥匙串访问" 应用
3. 选择添加到 "系统" 钥匙串
4. 在钥匙串中找到 "mitmproxy" 证书，双击打开
5. 展开 "信任" 部分，将 "SSL" 设置为 "始终信任"
6. 输入管理员密码确认

💡 提示:
   • 只需安装一次，重装应用无需重复操作
   • 不信任证书将无法进行HTTPS流量拦截
   • 可在应用运行后随时通过状态栏菜单重新生成证书
   • 如需帮助，请查看应用内的详细说明

============================================================
JDCat - 敏感信息检测工具
生成时间: {timestamp}
""".format(
            cert_path=str(self.ca_cert_path),
            timestamp=datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        )
        
        try:
            with open(guide_file_path, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            self.logger.info(f"Created certificate installation guide: {guide_file_path}")
        except Exception as e:
            self.logger.error(f"Failed to create certificate guide file: {e}")
    
    def get_ca_cert_path(self) -> Path:
        """Get the path to the CA certificate."""
        return self.ca_cert_path
    
    def get_ca_key_path(self) -> Path:
        """Get the path to the CA private key."""
        return self.ca_key_path
    
    def certificate_exists(self) -> bool:
        """Check if mitmproxy CA certificate exists."""
        return self.ca_cert_path.exists() and self.ca_key_path.exists()
    
    def setup_certificate_environment(self) -> Dict[str, str]:
        """
        Setup environment variables for mitmproxy certificate usage.
        
        Returns:
            Dict of environment variables to set.
        """
        env_vars = {}
        
        # Ensure directory exists
        self.ensure_mitmproxy_dir()
        
        # Set MITMPROXY_CONFDIR to use persistent directory
        env_vars['MITMPROXY_CONFDIR'] = str(self.mitmproxy_dir)
        
        # If certificate exists, set the CA cert path
        if self.certificate_exists():
            env_vars['MITMPROXY_CA_CERT'] = str(self.ca_cert_path)
            self.logger.info(f"Using existing certificate: {self.ca_cert_path}")
        else:
            self.logger.info("Certificate will be generated on first mitmproxy run")
        
        return env_vars
    
    def is_certificate_trusted_macos(self) -> bool:
        """
        Check if the certificate is trusted in macOS keychain.
        
        Returns:
            True if certificate is trusted, False otherwise.
        """
        if platform.system() != "Darwin":
            return False
            
        if not self.certificate_exists():
            return False
            
        try:
            # Use security command to check if certificate is trusted
            cmd = [
                'security', 'verify-cert', 
                '-c', str(self.ca_cert_path),
                '-p', 'ssl'  # SSL policy
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"Failed to check certificate trust: {e}")
            return False
    
    def trust_certificate_macos(self) -> bool:
        """
        Trust the mitmproxy certificate in macOS keychain.
        
        Returns:
            True if successful, False otherwise.
        """
        if platform.system() != "Darwin":
            self.logger.warning("Certificate trust is only supported on macOS")
            return False
            
        if not self.certificate_exists():
            self.logger.error("Certificate does not exist, cannot trust")
            return False
        
        try:
            # Add certificate to keychain
            add_cmd = [
                'security', 'add-trusted-cert',
                '-d',  # Add to admin cert store
                '-r', 'trustRoot',  # Trust for root
                '-k', '/Library/Keychains/System.keychain',
                str(self.ca_cert_path)
            ]
            
            self.logger.info("Adding certificate to system keychain (requires admin privileges)")
            result = subprocess.run(add_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Certificate successfully trusted in system keychain")
                return True
            else:
                self.logger.error(f"Failed to trust certificate: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception while trusting certificate: {e}")
            return False
    
    def get_certificate_info(self) -> Dict[str, Any]:
        """
        Get information about the current certificate status.
        
        Returns:
            Dictionary with certificate information.
        """
        info = {
            'mitmproxy_dir': str(self.mitmproxy_dir),
            'ca_cert_path': str(self.ca_cert_path),
            'ca_key_path': str(self.ca_key_path),
            'certificate_exists': self.certificate_exists(),
            'directory_exists': self.mitmproxy_dir.exists(),
            'platform': platform.system(),
        }
        
        if platform.system() == "Darwin":
            info['trusted_in_keychain'] = self.is_certificate_trusted_macos()
        
        return info
    
    def initialize_certificates(self) -> Dict[str, Any]:
        """
        Initialize certificate setup for the application.
        
        This method:
        1. Ensures mitmproxy directory exists
        2. Sets up environment variables
        3. Optionally prompts for certificate trust on macOS
        
        Returns:
            Dictionary with setup results and environment variables.
        """
        self.logger.info("Initializing certificate management")
        
        # Setup environment
        env_vars = self.setup_certificate_environment()
        
        # Get current status
        cert_info = self.get_certificate_info()
        
        result = {
            'success': True,
            'env_vars': env_vars,
            'certificate_info': cert_info,
            'messages': []
        }
        
        if not cert_info['certificate_exists']:
            result['messages'].append("Certificate will be generated automatically on first mitmproxy run")
            # Mark that trust will be needed after certificate generation
            if platform.system() == "Darwin":
                result['needs_trust'] = True
                result['messages'].append("Certificate will need to be trusted after generation")
        else:
            result['messages'].append(f"Using existing certificate: {self.ca_cert_path}")
            
            # Check trust status on macOS
            if platform.system() == "Darwin":
                if not cert_info.get('trusted_in_keychain', False):
                    result['messages'].append("Certificate exists but is not trusted in keychain")
                    result['needs_trust'] = True
                else:
                    result['messages'].append("Certificate is trusted in system keychain")
        
        return result
    
    def prompt_certificate_trust(self) -> bool:
        """
        Prompt user to trust certificate and attempt to install it.
        
        Returns:
            True if certificate was successfully trusted or already trusted.
        """
        if platform.system() != "Darwin":
            return True  # Not applicable on non-macOS
            
        if not self.certificate_exists():
            self.logger.info("Certificate doesn't exist yet, will be handled after mitmproxy generates it")
            return True
            
        if self.is_certificate_trusted_macos():
            self.logger.info("Certificate is already trusted")
            return True
        
        self.logger.info("Certificate needs to be trusted for HTTPS interception")
        
        # Attempt to trust the certificate
        return self.trust_certificate_macos()
    
    def regenerate_certificates(self) -> Dict[str, Any]:
        """
        重新生成mitmproxy证书。
        
        这会删除现有证书并强制mitmproxy生成新的证书。
        
        Returns:
            Dictionary with regeneration results.
        """
        result = {
            'success': False,
            'messages': [],
            'certificate_info': {},
            'needs_trust': False
        }
        
        try:
            self.logger.info("Starting certificate regeneration...")
            
            # 1. 备份现有证书（如果存在）
            if self.certificate_exists():
                backup_dir = self.mitmproxy_dir / 'backup'
                backup_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if self.ca_cert_path.exists():
                    backup_cert = backup_dir / f"mitmproxy-ca-cert_{timestamp}.pem"
                    shutil.copy2(self.ca_cert_path, backup_cert)
                    result['messages'].append(f"Backed up certificate to: {backup_cert}")
                
                if self.ca_key_path.exists():
                    backup_key = backup_dir / f"mitmproxy-ca_{timestamp}.pem"
                    shutil.copy2(self.ca_key_path, backup_key)
                    result['messages'].append(f"Backed up key to: {backup_key}")
            
            # 2. 删除现有证书文件
            cert_files_to_remove = [
                self.ca_cert_path,
                self.ca_key_path,
                self.mitmproxy_dir / 'mitmproxy-ca-cert.cer',
                self.mitmproxy_dir / 'mitmproxy-ca-cert.p12',
                self.mitmproxy_dir / 'mitmproxy-ca.p12',
                self.mitmproxy_dir / 'mitmproxy-dhparam.pem'
            ]
            
            removed_files = []
            for cert_file in cert_files_to_remove:
                if cert_file.exists():
                    cert_file.unlink()
                    removed_files.append(str(cert_file))
                    
            if removed_files:
                result['messages'].append(f"Removed {len(removed_files)} certificate files")
                self.logger.info(f"Removed certificate files: {removed_files}")
            
            # 3. 直接使用CertStore生成证书
            try:
                self.logger.info("Generating certificates using CertStore")
                
                # 设置环境变量
                env = os.environ.copy()
                env['MITMPROXY_CONFDIR'] = str(self.mitmproxy_dir)
                
                # 使用CertStore直接生成证书
                from mitmproxy.certs import CertStore
                
                # 创建CertStore并强制生成CA证书
                cert_store = CertStore.from_store(str(self.mitmproxy_dir), 'mitmproxy', 2048)
                ca_cert = cert_store.default_ca  # 这会触发证书生成
                
                result['messages'].append("Successfully generated certificates using CertStore")
                self.logger.info("Certificate generation via CertStore completed")
                    
            except Exception as cert_error:
                error_msg = f"Certificate generation failed: {cert_error}"
                result['messages'].append(error_msg)
                self.logger.error(error_msg)
            
            # 4. 验证新证书是否生成
            if self.certificate_exists():
                result['success'] = True
                result['messages'].append("New certificates generated successfully")
                
                # 检查是否需要信任
                if platform.system() == "Darwin":
                    if not self.is_certificate_trusted_macos():
                        result['needs_trust'] = True
                        result['messages'].append("New certificate needs to be trusted in keychain")
                    else:
                        result['messages'].append("New certificate is already trusted")
                        
            else:
                result['messages'].append("Certificate generation may have failed - files not found")
                
            # 5. 更新证书安装引导文件
            self._create_certificate_guide_file()
            
            # 6. 获取最新证书信息
            result['certificate_info'] = self.get_certificate_info()
            
        except Exception as e:
            result['messages'].append(f"Certificate regeneration failed: {str(e)}")
            self.logger.error(f"Certificate regeneration error: {e}")
            
        return result


# Global certificate manager instance
cert_manager = CertificateManager()


def get_certificate_manager() -> CertificateManager:
    """Get the global certificate manager instance."""
    return cert_manager


def setup_certificate_environment() -> Dict[str, str]:
    """
    Convenience function to setup certificate environment.
    
    Returns:
        Dictionary of environment variables to set.
    """
    return cert_manager.setup_certificate_environment()


def initialize_certificates() -> Dict[str, Any]:
    """
    Convenience function to initialize certificates.
    
    Returns:
        Dictionary with initialization results.
    """
    return cert_manager.initialize_certificates()