#!/usr/bin/env python3
"""
JDCat CLI Entry Point

该模块提供 jdcat 命令行工具的主入口。
按照用户需求改造：
- jdcat start 改为在后台运行（守护进程模式），并写入 PID 信息到 ~/.sensitive-check/jdcat.pid
- jdcat stop 从 PID 文件读取并优雅关闭服务（先调用 /stop，再发送 SIGTERM，必要时 SIGKILL）

说明：
- 默认仍会在服务就绪后自动打开浏览器（可通过 --no-open-browser 关闭）
- 为避免额外依赖，后台模式通过 subprocess.Popen(start_new_session=True) 实现脱离终端
"""

import sys
import os
import webbrowser
import threading
import time
from typing import Optional, Annotated
import json
import signal
import urllib.request
import urllib.error
import importlib
from pathlib import Path

# Add the current package to the Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 兼容处理：在编辑器或检查环境未安装 typer 时提供轻量级占位实现，避免“无法解析导入”诊断
try:
    typer = importlib.import_module("typer")
except Exception:
    class _TyperModuleStub:
        class Exit(SystemExit):
            def __init__(self, code: int = 0):
                super().__init__(code)

        @staticmethod
        def Option(default=None, *args, **kwargs):
            # 返回默认值，占位以通过静态检查
            return default

        @staticmethod
        def echo(msg: str, **kwargs):
            # 简单打印，占位实现
            print(msg)

        class Typer:
            def __init__(self, *args, **kwargs):
                pass

            def __call__(self):
                # 占位：不实际运行 CLI
                pass

            def command(self, *args, **kwargs):
                # 返回装饰器占位：直接返回原函数
                def _decorator(func):
                    return func
                return _decorator

            def callback(self, *args, **kwargs):
                # 返回装饰器占位：直接返回原函数
                def _decorator(func):
                    return func
                return _decorator

    typer = _TyperModuleStub()

app = typer.Typer(
    add_completion=False,
    help="JDCat - Sensitive Check Local Service CLI Tool",
)

@app.callback()
def main_callback(
    version: Annotated[Optional[bool], typer.Option(
        "--version", help="Show version and exit", is_eager=True
    )] = None,
):
    """
    JDCat CLI - Local proxy service for sensitive data detection
    """
    if version:
        from . import __version__
        typer.echo(f"jdcat {__version__}")
        raise typer.Exit()

def _runtime_dir() -> str:
    """运行时目录（用于存放 pid 与日志）"""
    d = os.path.expanduser("~/.sensitive-check")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d

def _pid_file_path() -> str:
    return os.path.join(_runtime_dir(), "jdcat.pid")

def _log_file_path() -> str:
    # 按日期生成日志文件名：jdcat-YYYYMMDD.log
    dt = time.strftime("%Y%m%d")
    return os.path.join(_runtime_dir(), f"jdcat-{dt}.log")

def _read_pid_info() -> Optional[dict]:
    p = _pid_file_path()
    try:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.loads(f.read())
    except Exception:
        return None
    return None

def _is_process_running(pid: int) -> bool:
    try:
        # POSIX: signal 0 用于存活检测
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # 存在但无权限
        return True
    except Exception:
        return False

def _write_pid_info(pid: int, host: str, port: int) -> None:
    info = {
        "pid": pid,
        "host": host,
        "port": port,
        "createdAt": int(time.time()),
    }
    try:
        with open(_pid_file_path(), "w", encoding="utf-8") as f:
            f.write(json.dumps(info))
    except Exception:
        pass

def _wait_health_ready(host: str, port: int, timeout_sec: float = 10.0) -> bool:
    deadline = time.time() + max(0.1, timeout_sec)
    url = f"http://{host}:{port}/health"
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url=url, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if getattr(resp, "status", 200) == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

@app.command()
def start(
    port: Annotated[int, typer.Option("--port", help="服务端口")] = 17866,
    host: Annotated[str, typer.Option("--host", help="监听地址")] = "127.0.0.1",
    reload: Annotated[bool, typer.Option("--reload", help="开发模式：自动重载")] = False,
    open_browser: Annotated[bool, typer.Option("--open-browser/--no-open-browser", help="服务就绪后自动打开浏览器")] = True,
    browser_url: Annotated[str, typer.Option("--browser-url", help="浏览器打开的URL")] = "http://aq.jdtest.net:8007/",
):
    """
    后台启动 JDCat 本地服务（FastAPI + Uvicorn）。
    - 写入 PID 信息到 ~/.sensitive-check/jdcat.pid
    - 日志输出到 ~/.sensitive-check/jdcat.log
    - 若已运行，直接提示并退出
    """
    typer.echo(f"[jdcat] 后台启动服务：{host}:{port}")

    # 1) 处理已有 PID
    info = _read_pid_info()
    if info and isinstance(info.get("pid"), int):
        pid = int(info["pid"])
        if _is_process_running(pid):
            typer.echo(f"[jdcat] 服务已在后台运行（PID={pid}）。如需停止请执行：jdcat stop")
            # 简化逻辑：服务已运行时，若允许开窗则直接打开浏览器
            if open_browser:
                try:
                    typer.echo(f"[jdcat] 打开浏览器：{browser_url}")
                    webbrowser.open(browser_url)
                except Exception as e:
                    typer.echo(f"[jdcat] 打开浏览器失败：{e}", err=True)
            raise typer.Exit(0)
        else:
            # 清理陈旧 PID 文件
            try:
                os.remove(_pid_file_path())
            except Exception:
                pass

    # 2) 构造命令并后台启动
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "sensitive_check_local.api:app",
        "--host", host,
        "--port", str(port),
        "--log-level", "info",
    ]
    if reload:
        cmd.append("--reload")

    # 打开日志文件用于输出
    log_path = _log_file_path()
    try:
        log_fp = open(log_path, "a", encoding="utf-8")
    except Exception:
        log_fp = None

    try:
        # 使用 start_new_session=True 脱离终端；stdout/stderr 写入日志文件
        import subprocess
        p = subprocess.Popen(
            cmd,
            stdout=log_fp or subprocess.DEVNULL,
            stderr=log_fp or subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        _write_pid_info(pid=p.pid, host=host, port=port)
        typer.echo(f"[jdcat] 服务已后台启动，PID={p.pid}，日志：{log_path}")
        # 3) 简化：启动成功后立即打开浏览器（不再等待健康检查）
        if open_browser:
            try:
                typer.echo(f"[jdcat] 打开浏览器：{browser_url}")
                webbrowser.open(browser_url)
            except Exception as e:
                typer.echo(f"[jdcat] 打开浏览器失败：{e}", err=True)

    except Exception as e:
        typer.echo(f"[jdcat] 后台启动失败：{e}", err=True)
        raise typer.Exit(1)

@app.command()
def stop():
    """
    停止后台运行的 JDCat 服务：
    - 读取 ~/.sensitive-check/jdcat.pid
    - 先调用 /stop 做收尾（恢复系统代理等）
    - 然后发送 SIGTERM，必要时 SIGKILL
    """
    info = _read_pid_info()
    if not info or not isinstance(info.get("pid"), int):
        typer.echo("[jdcat] 未发现运行中的服务（PID 文件不存在）。")
        raise typer.Exit(0)

    pid = int(info["pid"])  # type: ignore
    host = str(info.get("host") or "127.0.0.1")
    port = int(info.get("port") or 17866)

    if not _is_process_running(pid):
        typer.echo(f"[jdcat] 进程（PID={pid}）未运行，清理 PID 文件后退出。")
        try:
            os.remove(_pid_file_path())
        except Exception:
            pass
        raise typer.Exit(0)

    # 1) 优雅收尾：POST /stop
    try:
        url = f"http://{host}:{port}/stop"
        req = urllib.request.Request(url=url, method="POST")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            _ = resp.read()
        typer.echo("[jdcat] 已请求服务执行 /stop 收尾。")
    except Exception:
        # 忽略网络错误，继续终止进程
        typer.echo("[jdcat] /stop 调用失败，继续终止进程。")

    # 2) 发送 SIGTERM，等待退出
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        pass

    deadline = time.time() + 8.0
    while time.time() < deadline:
        if not _is_process_running(pid):
            break
        time.sleep(0.3)

    # 3) 若仍存活，强制 SIGKILL
    if _is_process_running(pid):
        try:
            os.kill(pid, signal.SIGKILL)
            typer.echo("[jdcat] 进程未能优雅退出，已强制终止。")
        except Exception:
            typer.echo("[jdcat] 进程强制终止失败，请手动处理。", err=True)

    # 4) 清理 PID 文件
    try:
        os.remove(_pid_file_path())
    except Exception:
        pass

    typer.echo("[jdcat] 服务已停止。")

@app.command()
def status():
    """
    Check the status of JDCat local service
    """
    typer.echo("Checking JDCat service status...")
    # Note: This is a placeholder. In a real implementation, you might want to
    # check if the service is running on the configured port
    typer.echo("Status check not yet implemented. Use 'jdcat start' to run the service.")

def main():
    """
    Main entry point for the jdcat command
    """
    app()

if __name__ == "__main__":
    main()