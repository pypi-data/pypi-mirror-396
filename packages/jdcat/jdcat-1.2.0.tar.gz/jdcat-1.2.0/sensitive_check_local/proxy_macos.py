"""
macOS system proxy control for sensitive-check-local.

Implements:
- detect_services(): enumerate active network services (exclude lines starting with '*')
- snapshot_proxy_state(services): capture HTTP/HTTPS proxy and bypass list per service
- enable_system_proxy(services, port, bypass_domains): set proxies to 127.0.0.1:port and merge/set bypass list
- restore_proxy_state(snapshot): restore previous state

Non-Darwin platforms: raise RuntimeError to signal upper layer for graceful degrade.
"""
from __future__ import annotations

import platform
import subprocess
from typing import Any, Dict, List, Tuple

from . import config as _config


def _ensure_darwin() -> None:
    if platform.system() != "Darwin":
        raise RuntimeError("System proxy operations are only supported on macOS (Darwin).")


def _run(args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(args, capture_output=True, text=True)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    return p.returncode, out, err

def run_cmd(args: List[str]) -> Tuple[int, str, str]:
    """
    Unified command runner. Returns (code, stdout, stderr).
    """
    return _run(args)

# added: logger and admin-run helper for macOS privileged operations
import os
import shlex
import logging
import time
from urllib import request as _urlreq, error as _urlerr
_logger = logging.getLogger("sensitive_check_local.proxy")
# 使用父级 logger 的配置，避免重复添加处理器

# 全局标记，用于跟踪是否已经申请过本地网络权限
_network_permission_requested = False

# 单轮 /start 防抖：仅允许一次 Helper 安装尝试
_helper_install_attempted_once = False

# 本轮是否已实际启用过系统代理（仅在 enable 成功后置 True）
_proxy_applied_this_round = False

def _run_admin(args: List[str], prompt: str = None, title: str = None) -> Tuple[int, str, str]:
    """
    Execute command with admin privileges via AppleScript to trigger macOS auth prompt.
    Only use for commands that change system proxy settings.
    
    Args:
        args: Command arguments to execute
        prompt: Custom authorization prompt message (optional)
        title: Custom authorization dialog title (optional)
    """
    # Build a properly quoted shell command
    cmd = " ".join(shlex.quote(a) for a in args)
    
    # Get custom prompt from config if not provided
    config = _config.load_config()
    if prompt is None:
        prompt = config.get("auth_prompt", _config.DEFAULT_AUTH_PROMPT)
    
    # Note: macOS system auth dialog doesn't support custom titles
    # The title parameter is kept for API compatibility but not used
    # Only the prompt message can be customized in the system auth dialog
    
    # Escape special characters for AppleScript
    escaped_prompt = prompt.replace('"', '\\"').replace('\\', '\\\\')
    
    # Use the system auth dialog with custom prompt (single dialog)
    script = f'do shell script "{cmd}" with administrator privileges with prompt "{escaped_prompt}"'
    
    p = subprocess.run(["/usr/bin/osascript", "-e", script], capture_output=True, text=True)
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    code = int(p.returncode or 0)
    _logger.info("[proxy-admin] cmd=%s code=%s out=%s err=%s", cmd, code, out[:200], err[:200])
    return code, out, err

def _run_admin_batch(commands: List[List[str]], prompt: str = None, title: str = None) -> List[Tuple[int, str, str]]:
    """
    Execute multiple commands in a single admin privileges request to reduce popup frequency.
    
    Args:
        commands: List of command argument lists to execute
        prompt: Custom authorization prompt message (optional)
        title: Custom authorization dialog title (optional)
    """
    if not commands:
        return []
    
    # Combine all commands into a single shell script
    cmd_strings = []
    for args in commands:
        cmd = " ".join(shlex.quote(a) for a in args)
        cmd_strings.append(cmd)
    
    # Join commands with && to stop on first failure
    combined_cmd = " && ".join(cmd_strings)
    
    # Get custom prompt from config if not provided
    config = _config.load_config()
    if prompt is None:
        prompt = config.get("auth_prompt", _config.DEFAULT_AUTH_PROMPT)
    
    # Note: macOS system auth dialog doesn't support custom titles
    # The title parameter is kept for API compatibility but not used
    # Only the prompt message can be customized in the system auth dialog
    
    # Escape special characters for AppleScript
    escaped_prompt = prompt.replace('"', '\\"').replace('\\', '\\\\')
    
    _logger.info("[proxy-admin-batch] Executing %d commands in single admin request", len(commands))
    
    # Use the system auth dialog with custom prompt (single dialog)
    script = f'do shell script "{combined_cmd}" with administrator privileges with prompt "{escaped_prompt}"'
    
    _logger.debug("[proxy-admin-batch] Script: %s", script[:500])
    
    try:
        p = subprocess.run(["/usr/bin/osascript", "-e", script], capture_output=True, text=True)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        code = int(p.returncode or 0)
        
        if code == 0:
            _logger.info("[proxy-admin-batch] 成功执行，返回码: %s", code)
        else:
            _logger.warning("[proxy-admin-batch] 执行失败，返回码: %s", code)
            if "User canceled" in err or "cancelled" in err.lower():
                _logger.info("[proxy-admin-batch] 用户取消了管理员权限验证")
            elif "Authentication failed" in err:
                _logger.info("[proxy-admin-batch] 管理员权限验证失败")
            else:
                _logger.warning("[proxy-admin-batch] 其他错误: %s", err[:200])
        
        _logger.info("[proxy-admin-batch] Combined result: code=%s out=%s err=%s", code, out[:200], err[:200])
        
        # Return the same result for all commands (simplified)
        return [(code, out, err)] * len(commands)
        
    except Exception as e:
        _logger.error("[proxy-admin-batch] 执行异常: %s", e)
        # Return error for all commands
        return [(1, "", str(e))] * len(commands)


def _helper_plist_path() -> str:
    return "/Library/LaunchDaemons/com.jdcat.proxy.helper.plist"

def _detect_python_interpreter() -> str:
    """
    检测可用的Python3解释器路径，按优先级顺序返回第一个可用的路径。
    优先级：系统默认 > Homebrew > 其他常见位置
    """
    python_candidates = [
        "/usr/bin/python3",           # macOS系统默认
        "/opt/homebrew/bin/python3",  # Apple Silicon Homebrew
        "/usr/local/bin/python3",     # Intel Homebrew
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",  # Python.org安装
        "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3",
    ]
    
    for python_path in python_candidates:
        if not os.path.exists(python_path):
            continue
        try:
            # 验证Python解释器是否可执行且版本合适
            result = subprocess.run([python_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "Python 3." in result.stdout:
                _logger.info("[python-detect] 找到可用Python解释器: %s (%s)", 
                           python_path, result.stdout.strip())
                return python_path
        except Exception as e:
            _logger.debug("[python-detect] Python路径检查失败 %s: %s", python_path, e)
            continue
    
    # 如果没有找到，抛出错误
    raise RuntimeError(f"未找到可用的Python3解释器。已检查路径: {python_candidates}")

def _generate_dynamic_plist(python_path: str) -> str:
    """
    根据检测到的Python解释器路径生成动态plist内容
    """
    plist_template = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.jdcat.proxy.helper</string>

    <key>ProgramArguments</key>
    <array>
      <string>{python_path}</string>
      <string>/Library/PrivilegedHelperTools/jdcat_proxy_helper.py</string>
      <string>--port</string>
      <string>17901</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>UserName</key>
    <string>root</string>

    <!-- Optional logs for troubleshooting -->
    <key>StandardOutPath</key>
    <string>/var/log/com.jdcat.proxy.helper.out.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/com.jdcat.proxy.helper.err.log</string>
  </dict>
</plist>'''
    
    return plist_template.format(python_path=python_path)

def _helper_healthcheck(timeout: float = 1.0) -> bool:
    try:
        req = _urlreq.Request(url="http://127.0.0.1:17901/health", method="GET")
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            if status != 200:
                return False
            body = resp.read()
            txt = body.decode("utf-8", errors="ignore") if isinstance(body, (bytes, bytearray)) else str(body)
            import json as _json  # local import to minimize global deps
            try:
                obj = _json.loads(txt)
                return bool(obj.get("ok", False))
            except Exception:
                return False
    except Exception:
        return False

def install_if_needed() -> None:
    """
    安装 Root Helper，支持智能重试机制：
      1) 创建目录 /Library/PrivilegedHelperTools
      2) 复制打包内 jdcat/root_helper/jdcat_proxy_helper.py -> /Library/PrivilegedHelperTools/jdcat_proxy_helper.py（chmod 0755, chown root:wheel）
      3) 复制打包内 jdcat/resources/com.jdcat.proxy.helper.plist -> /Library/LaunchDaemons/com.jdcat.proxy.helper.plist（chmod 0644, chown root:wheel）
      4) launchctl bootstrap/enable/kickstart
    首次安装失败时自动重试一次，以解决macOS LaunchDaemon时序问题。
    """
    global _helper_install_attempted_once
    _ensure_darwin()

    # 若已存在且健康，直接返回（不弹窗）
    try:
        if os.path.exists(_helper_plist_path()) and _helper_healthcheck(timeout=0.6):
            _logger.info("[helper-install] 已存在且健康，跳过安装")
            return
    except Exception:
        pass

    # 防抖：本进程本轮仅允许一次安装尝试
    if _helper_install_attempted_once:
        _logger.info("[helper-install] 本轮已尝试安装，跳过重复安装与弹窗")
        return
    _helper_install_attempted_once = True
    
    # 执行安装
    _logger.info("[helper-install] 开始安装...")
    _perform_installation()

def _perform_installation() -> None:
    """
    执行安装过程
    """
    
    # 计算打包内源文件路径（基于当前模块 __file__）
    here = os.path.abspath(os.path.dirname(__file__))
    pkg_root = os.path.abspath(os.path.join(here, ".."))  # jdcat/
    
    # 详细路径调试信息
    _logger.info("[helper-install] 路径调试 - __file__: %s", __file__)
    _logger.info("[helper-install] 路径调试 - here: %s", here)
    _logger.info("[helper-install] 路径调试 - pkg_root: %s", pkg_root)
    _logger.info("[helper-install] 路径调试 - pkg_root内容: %s", 
                os.listdir(pkg_root) if os.path.exists(pkg_root) else "目录不存在")
    
    # 尝试多种路径查找策略
    src_helper = None
    src_plist = None
    
    # 策略1: 基于相对路径（开发环境）
    candidate_helper = os.path.abspath(os.path.join(pkg_root, "root_helper", "jdcat_proxy_helper.py"))
    candidate_plist = os.path.abspath(os.path.join(pkg_root, "resources", "com.jdcat.proxy.helper.plist"))
    
    _logger.info("[helper-install] 策略1 - 候选Helper路径: %s (存在: %s)", 
                candidate_helper, os.path.exists(candidate_helper))
    _logger.info("[helper-install] 策略1 - 候选plist路径: %s (存在: %s)", 
                candidate_plist, os.path.exists(candidate_plist))
    
    if os.path.exists(candidate_helper) and os.path.exists(candidate_plist):
        src_helper = candidate_helper
        src_plist = candidate_plist
        _logger.info("[helper-install] 策略1成功 - 使用相对路径")
    else:
        # 策略2: 使用importlib.resources（pip安装环境）
        _logger.info("[helper-install] 策略1失败，尝试策略2 - importlib.resources")
        try:
            import importlib.resources as pkg_resources
            import jdcat
            
            # 尝试读取资源
            try:
                with pkg_resources.path('root_helper', 'jdcat_proxy_helper.py') as helper_path:
                    src_helper = str(helper_path)
                    _logger.info("[helper-install] 策略2 - 找到Helper: %s", src_helper)
            except Exception as e:
                _logger.warning("[helper-install] 策略2 - Helper查找失败: %s", e)
            
            try:
                with pkg_resources.path('resources', 'com.jdcat.proxy.helper.plist') as plist_path:
                    src_plist = str(plist_path)
                    _logger.info("[helper-install] 策略2 - 找到plist: %s", src_plist)
            except Exception as e:
                _logger.warning("[helper-install] 策略2 - plist查找失败: %s", e)
                
        except ImportError as e:
            _logger.warning("[helper-install] 策略2失败 - importlib.resources不可用: %s", e)
    
    # 策略3: 搜索site-packages和data-files位置
    if not src_helper or not src_plist:
        _logger.info("[helper-install] 策略3 - 搜索site-packages和data-files")
        import site
        import sys
        
        search_paths = []
        # 添加site-packages路径
        search_paths.extend(site.getsitepackages() + [site.getusersitepackages()])
        # 添加sys.prefix下的share目录（data-files通常安装在这里）
        search_paths.append(os.path.join(sys.prefix, "share", "jdcat"))
        # 添加虚拟环境路径
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            search_paths.append(os.path.join(sys.prefix, "share", "jdcat"))
        
        for search_dir in search_paths:
            if not search_dir or not os.path.exists(search_dir):
                continue
            _logger.info("[helper-install] 策略3 - 检查目录: %s", search_dir)
            
            if not src_helper:
                # 搜索多个可能的Helper位置
                helper_candidates = [
                    os.path.join(search_dir, "root_helper", "jdcat_proxy_helper.py"),
                    os.path.join(search_dir, "share", "jdcat", "root_helper", "jdcat_proxy_helper.py"),
                    os.path.join(search_dir, "jdcat", "root_helper", "jdcat_proxy_helper.py")
                ]
                for candidate in helper_candidates:
                    if os.path.exists(candidate):
                        src_helper = candidate
                        _logger.info("[helper-install] 策略3 - 找到Helper: %s", src_helper)
                        break
            
            if not src_plist:
                # 搜索多个可能的plist位置
                plist_candidates = [
                    os.path.join(search_dir, "resources", "com.jdcat.proxy.helper.plist"),
                    os.path.join(search_dir, "share", "jdcat", "resources", "com.jdcat.proxy.helper.plist"),
                    os.path.join(search_dir, "jdcat", "resources", "com.jdcat.proxy.helper.plist")
                ]
                for candidate in plist_candidates:
                    if os.path.exists(candidate):
                        src_plist = candidate
                        _logger.info("[helper-install] 策略3 - 找到plist: %s", src_plist)
                        break
    
    # 最终路径确认
    _logger.info("[helper-install] 最终路径 - Helper: %s", src_helper)
    _logger.info("[helper-install] 最终路径 - plist: %s", src_plist)

    # 目标路径
    dst_helper = "/Library/PrivilegedHelperTools/jdcat_proxy_helper.py"
    dst_plist = _helper_plist_path()

    # 校验源文件存在
    if not os.path.exists(src_helper):
        raise RuntimeError(f"缺少打包内 Helper 脚本: {src_helper}")
    if not os.path.exists(src_plist):
        raise RuntimeError(f"缺少打包内 LaunchDaemon 模板: {src_plist}")

    # 详细诊断安装流程：分步执行，添加详细日志
    _logger.info("[helper-install] 开始分步诊断安装流程")
    
    # 诊断步骤1：检查源文件详情
    _logger.info("[helper-install] 诊断 - 源文件详情:")
    _logger.info("[helper-install] 诊断 - Helper脚本: %s (存在: %s, 大小: %s)",
                src_helper, os.path.exists(src_helper),
                os.path.getsize(src_helper) if os.path.exists(src_helper) else "N/A")
    _logger.info("[helper-install] 诊断 - plist模板: %s (存在: %s, 大小: %s)",
                src_plist, os.path.exists(src_plist),
                os.path.getsize(src_plist) if os.path.exists(src_plist) else "N/A")
    
    # 诊断步骤2：检查目标目录和现有文件
    _logger.info("[helper-install] 诊断 - 目标路径检查:")
    _logger.info("[helper-install] 诊断 - 目标Helper: %s (存在: %s)", dst_helper, os.path.exists(dst_helper))
    _logger.info("[helper-install] 诊断 - 目标plist: %s (存在: %s)", dst_plist, os.path.exists(dst_plist))
    _logger.info("[helper-install] 诊断 - PrivilegedHelperTools目录: %s", os.path.exists("/Library/PrivilegedHelperTools"))
    _logger.info("[helper-install] 诊断 - LaunchDaemons目录: %s", os.path.exists("/Library/LaunchDaemons"))
    
    # 诊断步骤3：检查现有服务状态
    _logger.info("[helper-install] 诊断 - 检查现有服务状态...")
    try:
        result = subprocess.run(["/bin/launchctl", "list", "com.jdcat.proxy.helper"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            _logger.info("[helper-install] 诊断 - 发现现有服务: %s", result.stdout.strip())
        else:
            _logger.info("[helper-install] 诊断 - 未发现现有服务 (正常)")
    except Exception as e:
        _logger.info("[helper-install] 诊断 - 服务状态检查失败: %s", e)
    
    # 步骤1：尝试无特权清理（静默失败，不弹窗）
    _logger.info("[helper-install] 步骤1 - 尝试无特权清理旧服务...")
    try:
        subprocess.run(["/bin/launchctl", "bootout", "gui/" + str(os.getuid()) + "/com.jdcat.proxy.helper"],
                      capture_output=True, timeout=5)
        _logger.info("[helper-install] 步骤1 - 用户级清理完成")
    except Exception:
        _logger.debug("[helper-install] 步骤1 - 用户级清理失败（预期）")
    
    # 获取授权提示
    config = _config.load_config()
    prompt = config.get("auth_prompt", _config.DEFAULT_AUTH_PROMPT)
    escaped_prompt = prompt.replace('"', '\\"')
    
    # 步骤2：分步执行安装脚本，每步单独记录
    _logger.info("[helper-install] 步骤2 - 构建分步安装脚本")
    
    # 检测可用的Python解释器路径
    _logger.info("[helper-install] 检测可用的Python解释器...")
    try:
        python_path = _detect_python_interpreter()
        _logger.info("[helper-install] 将使用Python解释器: %s", python_path)
    except RuntimeError as e:
        _logger.error("[helper-install] Python解释器检测失败: %s", e)
        raise e
    
    # 生成动态plist内容
    _logger.info("[helper-install] 生成适配的plist配置...")
    dynamic_plist_content = _generate_dynamic_plist(python_path)
    
    # 创建临时plist文件用于安装
    import tempfile
    temp_plist_fd = None
    temp_plist_path = None
    try:
        temp_plist_fd, temp_plist_path = tempfile.mkstemp(suffix='.plist', prefix='jdcat_helper_')
        with os.fdopen(temp_plist_fd, 'w') as f:
            f.write(dynamic_plist_content)
        temp_plist_fd = None  # 已关闭
        _logger.info("[helper-install] 临时plist文件已生成: %s", temp_plist_path)
        
        # 更新src_plist为动态生成的临时文件
        src_plist = temp_plist_path
        
    except Exception as e:
        if temp_plist_fd:
            try:
                os.close(temp_plist_fd)
            except:
                pass
        _logger.error("[helper-install] 临时plist文件创建失败: %s", e)
        raise RuntimeError(f"无法创建临时plist文件: {e}")
    
    # 构建AppleScript兼容的单行脚本，避免多行语法错误
    # 分步执行安装，每步单独记录结果和错误
    steps = [
        f"/bin/launchctl bootout system/com.jdcat.proxy.helper 2>/dev/null || echo 'STEP1-OK: bootout完成'",
        f"/bin/launchctl remove com.jdcat.proxy.helper 2>/dev/null || echo 'STEP1B-OK: remove完成'",
        f"/bin/launchctl unload '{dst_plist}' 2>/dev/null || echo 'STEP1C-OK: unload完成'",
        f"echo 'STEP1D-INFO: 等待清理完成...' && sleep 8",  # 简化为固定等待，避免AppleScript语法问题
        f"/bin/rm -f '{dst_plist}' '{dst_helper}' 2>/dev/null || echo 'STEP2-OK: 文件清理完成'",
        f"/bin/mkdir -p '/Library/PrivilegedHelperTools' && echo 'STEP3-OK: 目录创建成功' || echo 'STEP3-FAIL: 目录创建失败'",
        f"/bin/cp '{src_helper}' '{dst_helper}' && echo 'STEP4-OK: Helper复制成功' || echo 'STEP4-FAIL: Helper复制失败'",
        f"/bin/chmod 0755 '{dst_helper}' && echo 'STEP5-OK: Helper权限设置成功' || echo 'STEP5-FAIL: Helper权限设置失败'",
        f"/usr/sbin/chown root:wheel '{dst_helper}' && echo 'STEP6-OK: Helper所有者设置成功' || echo 'STEP6-FAIL: Helper所有者设置失败'",
        f"/usr/bin/xattr -d com.apple.provenance '{dst_helper}' 2>/dev/null || echo 'STEP7-OK: Helper扩展属性清理完成'",
        f"/bin/cp '{src_plist}' '{dst_plist}' && echo 'STEP8-OK: plist复制成功' || echo 'STEP8-FAIL: plist复制失败'",
        f"/bin/chmod 0644 '{dst_plist}' && echo 'STEP9-OK: plist权限设置成功' || echo 'STEP9-FAIL: plist权限设置失败'",
        f"/usr/sbin/chown root:wheel '{dst_plist}' && echo 'STEP10-OK: plist所有者设置成功' || echo 'STEP10-FAIL: plist所有者设置失败'",
        f"/usr/bin/xattr -d com.apple.provenance '{dst_plist}' 2>/dev/null || echo 'STEP11-OK: plist扩展属性清理完成'",
        f"/usr/bin/plutil -lint '{dst_plist}' && echo 'STEP12-OK: plist格式验证成功' || echo 'STEP12-FAIL: plist格式验证失败'",
        f"echo 'STEP13-START: 开始bootstrap' && /bin/launchctl bootstrap system '{dst_plist}' && echo 'STEP13-OK: bootstrap成功' || echo 'STEP13-FAIL: bootstrap失败，错误码=$?'",
        f"/bin/launchctl enable system/com.jdcat.proxy.helper && echo 'STEP14-OK: enable成功' || echo 'STEP14-FAIL: enable失败'",
        f"/bin/launchctl kickstart -k system/com.jdcat.proxy.helper && echo 'STEP15-OK: kickstart成功' || echo 'STEP15-FAIL: kickstart失败'"
    ]
    
    # 将所有步骤合并为一个命令
    simple_script = " && ".join(steps)
    
    applescript = f'do shell script "{simple_script}" with administrator privileges with prompt "{escaped_prompt}"'
    
    _logger.info("[helper-install] 步骤2 - 执行详细诊断安装脚本")
    
    try:
        # 增加超时时间，因为安装过程可能需要更长时间，特别是在系统权限检查时
        p = subprocess.run(["/usr/bin/osascript", "-e", applescript], capture_output=True, text=True, timeout=90)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        code = int(p.returncode or 0)
        
        # 详细记录所有输出
        _logger.info("[helper-install] 脚本执行完成，返回码: %s", code)
        if out:
            _logger.info("[helper-install] 标准输出:\n%s", out)
        if err:
            _logger.info("[helper-install] 标准错误:\n%s", err)
        
        # 检查是否有bootstrap失败
        bootstrap_failed = False
        kickstart_failed = False
        
        if code == 0:
            _logger.info("[helper-install] 诊断安装脚本执行成功")
            
            # 解析输出，查找具体失败步骤
            if out:
                lines = out.split('\n')
                for line in lines:
                    if line.strip():
                        _logger.info("[helper-install] 步骤结果: %s", line.strip())
                        # 检查关键步骤是否失败
                        if "STEP13-FAIL: bootstrap失败" in line:
                            bootstrap_failed = True
                        if "STEP15-FAIL: kickstart失败" in line:
                            kickstart_failed = True
        else:
            _logger.error("[helper-install] 诊断安装脚本执行失败，返回码: %s", code)
            
            # 分析错误输出，找出具体失败的步骤
            error_output = err or out
            _logger.error("[helper-install] 完整错误信息:\n%s", error_output)
            
            # 尝试解析具体失败步骤
            if "Bootstrap failed" in error_output:
                _logger.error("[helper-install] 诊断结果: LaunchDaemon bootstrap 失败")
                if "Input/output error" in error_output:
                    _logger.error("[helper-install] 诊断结果: I/O错误，可能原因:")
                    _logger.error("[helper-install] 诊断结果: 1. plist文件格式错误")
                    _logger.error("[helper-install] 诊断结果: 2. 文件权限问题")
                    _logger.error("[helper-install] 诊断结果: 3. 服务已存在冲突")
                    _logger.error("[helper-install] 诊断结果: 4. 系统完整性保护限制")
            
            raise RuntimeError(f"Helper安装失败 - 详细诊断信息请查看日志: {error_output}")
        
        # 如果bootstrap失败，尝试自动重试一次
        if bootstrap_failed:
            _logger.warning("[helper-install] Bootstrap首次失败，等待5秒后自动重试...")
            time.sleep(5)  # 等待系统状态稳定
            
            # 构建重试的bootstrap和kickstart命令
            retry_steps = [
                f"echo 'RETRY-START: 开始重试bootstrap' && /bin/launchctl bootstrap system '{dst_plist}' && echo 'RETRY-BOOTSTRAP-OK: 重试bootstrap成功' || echo 'RETRY-BOOTSTRAP-FAIL: 重试bootstrap失败'",
                f"/bin/launchctl enable system/com.jdcat.proxy.helper && echo 'RETRY-ENABLE-OK: 重试enable成功' || echo 'RETRY-ENABLE-FAIL: 重试enable失败'",
                f"/bin/launchctl kickstart -k system/com.jdcat.proxy.helper && echo 'RETRY-KICKSTART-OK: 重试kickstart成功' || echo 'RETRY-KICKSTART-FAIL: 重试kickstart失败'"
            ]
            
            retry_script = " && ".join(retry_steps)
            retry_applescript = f'do shell script "{retry_script}" with administrator privileges with prompt "{escaped_prompt}"'
            
            _logger.info("[helper-install] 执行重试...")
            
            try:
                retry_p = subprocess.run(["/usr/bin/osascript", "-e", retry_applescript], 
                                       capture_output=True, text=True, timeout=30)
                retry_out = (retry_p.stdout or "").strip()
                retry_err = (retry_p.stderr or "").strip()
                retry_code = int(retry_p.returncode or 0)
                
                _logger.info("[helper-install] 重试执行完成，返回码: %s", retry_code)
                if retry_out:
                    _logger.info("[helper-install] 重试输出:\n%s", retry_out)
                
                # 检查重试结果
                retry_bootstrap_success = "RETRY-BOOTSTRAP-OK" in retry_out
                
                if retry_code == 0 and retry_bootstrap_success:
                    _logger.info("[helper-install] ✅ 重试成功！Bootstrap已完成")
                    bootstrap_failed = False  # 重置失败标记
                else:
                    _logger.error("[helper-install] ❌ 重试仍然失败")
                    if retry_err:
                        _logger.error("[helper-install] 重试错误: %s", retry_err)
                    
            except subprocess.TimeoutExpired:
                _logger.error("[helper-install] 重试超时（30秒）")
            except Exception as e:
                _logger.error("[helper-install] 重试执行异常: %s", e)
        
        # 如果重试后仍然失败，则报错
        if bootstrap_failed:
            _logger.error("[helper-install] Bootstrap失败（包括重试），服务无法注册，停止后续检查")
            raise RuntimeError("LaunchDaemon bootstrap失败（已重试） - 服务无法注册到系统，可能是系统繁忙或权限问题")
        
    except subprocess.TimeoutExpired:
        _logger.error("[helper-install] 安装脚本执行超时（90秒）")
        # 清理临时plist文件
        if temp_plist_path and os.path.exists(temp_plist_path):
            try:
                os.unlink(temp_plist_path)
                _logger.info("[helper-install] 临时plist文件已清理: %s", temp_plist_path)
            except Exception as cleanup_e:
                _logger.warning("[helper-install] 临时plist文件清理失败: %s", cleanup_e)
        raise RuntimeError("Helper安装超时（90秒）- 可能系统权限对话框未响应或安装过程较慢")
    except Exception as e:
        # 清理临时plist文件
        if temp_plist_path and os.path.exists(temp_plist_path):
            try:
                os.unlink(temp_plist_path)
                _logger.info("[helper-install] 临时plist文件已清理: %s", temp_plist_path)
            except Exception as cleanup_e:
                _logger.warning("[helper-install] 临时plist文件清理失败: %s", cleanup_e)
        
        if "用户已取消" in str(e) or "User canceled" in str(e):
            _logger.info("[helper-install] 用户取消了管理员授权")
            raise RuntimeError("用户取消了管理员授权")
        else:
            _logger.error("[helper-install] 安装过程异常: %s", e)
            raise RuntimeError(f"Helper安装执行失败: {e}")

    # 安装完成后：先确认LaunchDaemon状态，再进行健康检查
    _logger.info("[helper-install] 安装完成，等待LaunchDaemon服务加载...")
    
    # 由于launchctl list检测不可靠，直接跳过LaunchDaemon状态检查
    # 改为直接进行健康检查，这是更可靠的服务可用性检测方式
    _logger.info("[helper-install] 跳过LaunchDaemon状态检查，直接进行服务健康检查...")
    
    _logger.info("[helper-install] 开始Helper服务健康检查...")
    
    # 诊断：检查LaunchDaemon状态和日志
    _logger.info("[helper-install] 诊断 - 检查LaunchDaemon状态...")
    try:
        # 检查服务是否已加载
        result = subprocess.run(["/bin/launchctl", "list", "com.jdcat.proxy.helper"],
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            _logger.info("[helper-install] 诊断 - 服务状态: %s", result.stdout.strip())
        else:
            _logger.warning("[helper-install] 诊断 - 服务未找到或未加载: %s", result.stderr.strip())
        
        # 检查系统日志中的相关错误
        log_result = subprocess.run(["/usr/bin/log", "show", "--predicate", 
                                   "process == 'launchd' AND eventMessage CONTAINS 'com.jdcat.proxy.helper'",
                                   "--style", "syslog", "--last", "2m"],
                                  capture_output=True, text=True, timeout=10)
        if log_result.stdout.strip():
            _logger.info("[helper-install] 诊断 - 系统日志: %s", log_result.stdout.strip())
        
        # 检查Helper服务的标准输出和错误日志
        helper_logs = [
            "/var/log/com.jdcat.proxy.helper.out.log",
            "/var/log/com.jdcat.proxy.helper.err.log"
        ]
        for log_file in helper_logs:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        content = f.read().strip()
                        if content:
                            _logger.info("[helper-install] 诊断 - %s 内容: %s", log_file, content[-500:])  # 只显示最后500字符
                        else:
                            _logger.info("[helper-install] 诊断 - %s 为空", log_file)
                except Exception as e:
                    _logger.warning("[helper-install] 诊断 - 无法读取 %s: %s", log_file, e)
            else:
                _logger.info("[helper-install] 诊断 - %s 不存在", log_file)
        
        # 尝试验证Helper脚本的语法和导入
        _logger.info("[helper-install] 诊断 - 验证Helper脚本语法...")
        try:
            # 使用python -m py_compile验证语法
            syntax_check = subprocess.run([
                python_path, "-m", "py_compile", "/Library/PrivilegedHelperTools/jdcat_proxy_helper.py"
            ], capture_output=True, text=True, timeout=10)
            
            _logger.info("[helper-install] 诊断 - 语法检查结果: 返回码=%s", syntax_check.returncode)
            if syntax_check.stderr:
                _logger.info("[helper-install] 诊断 - 语法检查错误: %s", syntax_check.stderr.strip())
                
        except Exception as e:
            _logger.warning("[helper-install] 诊断 - 语法检查失败: %s", e)
        
        # 尝试导入测试Helper脚本的依赖
        _logger.info("[helper-install] 诊断 - 测试Python依赖...")
        try:
            import_test = subprocess.run([
                python_path, "-c", 
                "import json, logging, argparse, os, subprocess, sys; "
                "from http.server import BaseHTTPRequestHandler, HTTPServer; "
                "from socketserver import ThreadingMixIn; "
                "print('依赖导入成功')"
            ], capture_output=True, text=True, timeout=10)
            
            _logger.info("[helper-install] 诊断 - 依赖测试结果: 返回码=%s", import_test.returncode)
            if import_test.stdout:
                _logger.info("[helper-install] 诊断 - 依赖测试输出: %s", import_test.stdout.strip())
            if import_test.stderr:
                _logger.info("[helper-install] 诊断 - 依赖测试错误: %s", import_test.stderr.strip())
                
        except Exception as e:
            _logger.warning("[helper-install] 诊断 - 依赖测试失败: %s", e)
        
        # 检查plist文件的实际内容
        try:
            with open(dst_plist, 'r') as f:
                plist_content = f.read()
        except Exception as e:
            _logger.warning("[helper-install] 诊断 - 无法读取plist文件: %s", e)
                
    except Exception as e:
        _logger.warning("[helper-install] 诊断 - 状态检查失败: %s", e)
    
    try:
        from . import root_helper_client as _rhc
    except Exception:
        _rhc = None

    wait_ok = False
    if _rhc and hasattr(_rhc, "wait_for_helper"):
        # 使用更长的超时时间，给LaunchDaemon足够启动时间
        wait_ok = bool(_rhc.wait_for_helper(timeout=15.0, interval=2.0))
    else:
        # 实现轮询健康检查：每2秒检查一次，15秒后失败
        _logger.info("[helper-install] 开始健康检查轮询（每2秒检查一次，最多15秒）...")
        max_checks = 8  # 8次 * 2秒 = 16秒（约15秒）
        for i in range(max_checks):
            check_time = (i + 1) * 2
            _logger.info("[helper-install] 第%d/%d次健康检查（%d秒）...", i + 1, max_checks, check_time)
            
            if _helper_healthcheck(timeout=2.0):  # 增加单次检查超时时间
                _logger.info("[helper-install] ✅ 健康检查成功！Helper服务在%d秒后就绪", check_time)
                wait_ok = True
                break
            
            if i < max_checks - 1:  # 不是最后一次检查
                _logger.info("[helper-install] ⏳ Helper服务尚未就绪，2秒后重试...")
                time.sleep(2)
            else:
                _logger.warning("[helper-install] ❌ 健康检查超时，已尝试%d次（共%d秒）", max_checks, max_checks * 2)

    if not wait_ok:
        _logger.error("[helper-install] Helper服务15秒内未能启动，服务可能存在问题")
        _logger.error("[helper-install] 建议：检查系统日志或Helper服务日志文件")
        
        # 清理临时plist文件
        if temp_plist_path and os.path.exists(temp_plist_path):
            try:
                os.unlink(temp_plist_path)
                _logger.info("[helper-install] 临时plist文件已清理: %s", temp_plist_path)
            except Exception as e:
                _logger.warning("[helper-install] 临时plist文件清理失败: %s", e)
        
        raise RuntimeError("Root Helper 安装后健康检查失败（/health 不可达）- 服务在15秒内未能启动，可能存在配置或权限问题")

    _logger.info("[helper-install] 健康检查通过，Helper 就绪")
    
    # 清理临时plist文件
    if temp_plist_path and os.path.exists(temp_plist_path):
        try:
            os.unlink(temp_plist_path)
            _logger.info("[helper-install] 临时plist文件已清理: %s", temp_plist_path)
        except Exception as e:
            _logger.warning("[helper-install] 临时plist文件清理失败: %s", e)

class NoActiveNetworkServices(Exception):
    """Raised when no active macOS network services are detected."""
    pass


def detect_services() -> List[str]:
    """
    Use /usr/sbin/networksetup -listallnetworkservices and filter:
    - skip lines starting with 'An asterisk (*) denotes'
    - skip lines starting with '*' (disabled services)
    - skip empty lines
    Return active service names. If none, raise NoActiveNetworkServices with guidance.
    """
    _ensure_darwin()
    code, out, err = _run(["/usr/sbin/networksetup", "-listallnetworkservices"])
    if code != 0:
        raise RuntimeError(f"Failed to list network services: {err or out}")
    services: List[str] = []
    for raw in (out or "").splitlines():
        line = (raw or "").strip()
        if not line:
            continue
        low = line.lower()
        # Robustly skip header/notice lines from networksetup output
        if low.startswith("an asterisk") or "asterisk (*) denotes" in low:
            continue
        if line.lstrip().startswith("*"):  # disabled service line
            continue
        # Heuristic: skip localized header lines mentioning disabled services
        if ("带星号" in line or "已禁用" in line) and ("网络服务" in line or "network service" in low):
            continue
        services.append(line)
    # Validate services with -getinfo to avoid header/noise being treated as names
    valid: List[str] = []
    for svc in services:
        c, o, e = _run(["/usr/sbin/networksetup", "-getinfo", svc])
        if c == 0:
            valid.append(svc)
    services = valid
    if not services:
        raise NoActiveNetworkServices("no_active_network_services: 请在系统设置启用某个网络服务（如 Wi‑Fi）后重试")
    return services


def _parse_proxy_get(output: str) -> Dict[str, Any]:
    """
    Parse output of `networksetup -getwebproxy` or `-getsecurewebproxy`.
    Example:
      Enabled: Yes
      Server: 127.0.0.1
      Port: 8080
      Authenticated Proxy Enabled: 0
    """
    enabled = False
    host: str | None = None
    port: int | None = None
    for line in (output or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("enabled:"):
            val = line.split(":", 1)[1].strip().lower()
            enabled = val in ("yes", "1", "true")
        elif line.lower().startswith("server:"):
            v = line.split(":", 1)[1].strip()
            host = v if v else None
        elif line.lower().startswith("port:"):
            v = line.split(":", 1)[1].strip()
            try:
                port = int(v)
            except Exception:
                port = None
    return {"enabled": enabled, "host": host, "port": port}


def _get_webproxy(service: str) -> Dict[str, Any]:
    code, out, err = _run(["/usr/sbin/networksetup", "-getwebproxy", service])
    if code != 0:
        # Some services may not support; treat as disabled
        return {"enabled": False, "host": None, "port": None}
    return _parse_proxy_get(out)


def _get_securewebproxy(service: str) -> Dict[str, Any]:
    code, out, err = _run(["/usr/sbin/networksetup", "-getsecurewebproxy", service])
    if code != 0:
        return {"enabled": False, "host": None, "port": None}
    return _parse_proxy_get(out)


def _get_bypass(service: str) -> list[str]:
    code, out, err = _run(["/usr/sbin/networksetup", "-getproxybypassdomains", service])
    if code != 0:
        # If not supported, return empty
        return []
    # When none configured, it prints: "There aren't any configured for this service!"
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if lines and "there aren't any configured" in lines[0].lower():
        return []
    return lines


def snapshot_proxy_state(services: List[str]) -> Dict[str, Any]:
    """
    Snapshot proxy settings for given services.
    Returns a dict that can be passed to restore_proxy_state.
    """
    _ensure_darwin()
    items: Dict[str, Any] = {}
    for svc in services:
        http = _get_webproxy(svc)
        https = _get_securewebproxy(svc)
        bypass = _get_bypass(svc)
        items[svc] = {"http": http, "https": https, "bypass": bypass}
    return {"services": list(services), "items": items}


def _set_webproxy(service: str, host: str, port: int, enabled: bool) -> None:
    # Use batch execution to reduce admin prompts
    args1 = ["/usr/sbin/networksetup", "-setwebproxy", service, host, str(port)]
    args2 = ["/usr/sbin/networksetup", "-setwebproxystate", service, "on" if enabled else "off"]
    
    results = _run_admin_batch([args1, args2])
    c1, o1, e1 = results[0]
    c2, o2, e2 = results[1]
    
    _logger.info("[proxy-set] HTTP setwebproxy service=%s host=%s port=%s code=%s", service, host, port, c1)
    if c1 != 0:
        raise RuntimeError(f"Failed to set HTTP proxy for {service}: {e1 or o1}")
    
    _logger.info("[proxy-set] HTTP setwebproxystate service=%s enabled=%s code=%s", service, enabled, c2)
    if c2 != 0:
        raise RuntimeError(f"Failed to toggle HTTP proxy for {service}: {e2 or o2}")


def _set_securewebproxy(service: str, host: str, port: int, enabled: bool) -> None:
    # Use batch execution to reduce admin prompts
    args1 = ["/usr/sbin/networksetup", "-setsecurewebproxy", service, host, str(port)]
    args2 = ["/usr/sbin/networksetup", "-setsecurewebproxystate", service, "on" if enabled else "off"]
    
    results = _run_admin_batch([args1, args2])
    c1, o1, e1 = results[0]
    c2, o2, e2 = results[1]
    
    _logger.info("[proxy-set] HTTPS setsecurewebproxy service=%s host=%s port=%s code=%s", service, host, port, c1)
    if c1 != 0:
        raise RuntimeError(f"Failed to set HTTPS proxy for {service}: {e1 or o1}")
    
    _logger.info("[proxy-set] HTTPS setsecurewebproxystate service=%s enabled=%s code=%s", service, enabled, c2)
    if c2 != 0:
        raise RuntimeError(f"Failed to toggle HTTPS proxy for {service}: {e2 or o2}")


def _set_bypass(service: str, domains: list[str]) -> None:
    # If empty, explicitly clear list using the special 'Empty' token
    if not domains:
        args = ["/usr/sbin/networksetup", "-setproxybypassdomains", service, "Empty"]
    else:
        args = ["/usr/sbin/networksetup", "-setproxybypassdomains", service] + domains
    
    # Use single admin call for bypass domains
    results = _run_admin_batch([args])
    c, o, e = results[0]
    
    if not domains:
        _logger.info("[proxy-set] bypass clear service=%s code=%s", service, c)
        if c != 0:
            raise RuntimeError(f"Failed to clear bypass domains for {service}: {e or o}")
    else:
        _logger.info("[proxy-set] bypass set service=%s domains=%s code=%s", service, domains, c)
        if c != 0:
            raise RuntimeError(f"Failed to set bypass domains for {service}: {e or o}")


def enable_system_proxy(services: List[str], port: int, bypass_domains: list[str] | None = None) -> Dict[str, Any]:
    """
    启用系统代理到 127.0.0.1:port（HTTP/HTTPS），最小可行：优先通过 Root Helper 执行。
    流程：
      1) 若 Helper 可用（GET /health 成功），直接调用 root_helper_client.enable(...)
      2) 若不可用，执行"首次安装流程"，然后再次尝试 Helper
    注意：不再直接用 AppleScript 调用 networksetup；AppleScript 仅用于安装 Helper 的提权复制与 launchctl。
    """
    global _proxy_applied_this_round, _network_permission_requested
    _ensure_darwin()

    # 首次启用时尝试申请本地网络权限（保留现有逻辑）
    if not _network_permission_requested:
        try:
            from .network_permission import request_local_network_permission
            _logger.info("首次启用代理，申请本地网络权限...")
            request_local_network_permission()
            _network_permission_requested = True
            _logger.info("本地网络权限申请完成")
        except Exception as e:
            _logger.warning(f"本地网络权限申请失败，但继续执行代理设置: {e}")
            _network_permission_requested = True
    else:
        _logger.debug("本地网络权限已申请过，跳过")

    # 组装 host/port/bypass
    host = "127.0.0.1"
    defaults = list(_config.DEFAULT_BYPASS) if hasattr(_config, "DEFAULT_BYPASS") else ["aq.jdtest.net", "aqapi.jdtest.local", "0.0.0.0", "::1"]
    merged = defaults + (bypass_domains or [])
    seen: set[str] = set()
    final_domains: list[str] = []
    for d in merged:
        key = str(d).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        final_domains.append(str(d).strip())

    # 调用 Root Helper
    try:
        from . import root_helper_client as _rhc
    except Exception as e:
        raise RuntimeError(f"缺少 Root Helper 客户端模块: {e}")

    # 1) 尝试直连 Helper
    if _rhc.health(timeout=1.0):
        _logger.info("[helper] 健康检查通过，直接调用 /enable")
        _rhc.enable(host, int(port), list(services), final_domains, timeout=5.0)
        _proxy_applied_this_round = True
        return {"enabled": True, "host": host, "port": int(port), "bypass": final_domains, "services": list(services)}

    # 2) 不可用则执行安装流程并重试
    _logger.info("[helper] 不可用，开始安装 Helper...")
    install_if_needed()
    if not _rhc.health(timeout=1.0):
        raise RuntimeError("Root Helper 安装后仍不可用（/health 检测失败）")
    _logger.info("[helper] 安装完成，调用 /enable")
    _rhc.enable(host, int(port), list(services), final_domains, timeout=5.0)
    _proxy_applied_this_round = True
    return {"enabled": True, "host": host, "port": int(port), "bypass": final_domains, "services": list(services)}


def restore_proxy_state(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    恢复系统代理（最小实现）：根据快照中的服务列表将 HTTP/HTTPS 代理状态关闭。
    逻辑：
      - 仅当本轮确实启用过系统代理（_proxy_applied_this_round 为 True）时才执行恢复
      - 优先通过 Root Helper 的 /restore 接口关闭所有服务上的代理
      - Helper 不可用则直接跳过（不触发安装或任何新弹窗），记录警告
    """
    global _proxy_applied_this_round
    _ensure_darwin()
    if not isinstance(snapshot, dict):
        raise RuntimeError("Invalid snapshot")

    services = snapshot.get("services") or []
    if not services:
        return {"restored": True, "services": []}

    # 若本轮未启用过系统代理，则不做恢复（避免“启用失败却恢复”的路径）
    if not _proxy_applied_this_round:
        _logger.info("[restore] 本轮未启用系统代理，跳过恢复")
        return {"restored": False, "services": list(services), "skipped": True}

    try:
        from . import root_helper_client as _rhc
    except Exception as e:
        raise RuntimeError(f"缺少 Root Helper 客户端模块: {e}")

    if _rhc.health(timeout=1.0):
        _logger.info("[helper] 健康检查通过，调用 /restore")
        _rhc.restore(list(services), timeout=5.0)
        return {"restored": True, "services": list(services)}

    # 不做过度兜底：不安装、不弹窗，直接跳过
    _logger.warning("[helper] 不可用，跳过 /restore（不触发安装或弹窗）")
    return {"restored": False, "services": list(services), "skipped": True}


# Backward-compat wrappers (no-op if not used)
def enable_system_proxy_legacy(port: int) -> Dict[str, Any]:
    _ensure_darwin()
    svcs = detect_services()
    enable_system_proxy(svcs, port, None)
    return {"enabled": True, "services": svcs, "port": port}


def disable_system_proxy_legacy() -> Dict[str, Any]:
    _ensure_darwin()
    svcs = detect_services()
    snap = snapshot_proxy_state(svcs)
    # Turn off directly
    for svc in svcs:
        _set_webproxy(svc, "127.0.0.1", 8888, False)
        _set_securewebproxy(svc, "127.0.0.1", 8888, False)
    return {"disabled": True, "services": svcs, "snapshot": snap}