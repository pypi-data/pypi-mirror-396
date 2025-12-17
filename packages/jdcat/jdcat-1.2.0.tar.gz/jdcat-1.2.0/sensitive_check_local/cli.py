"""
CLI entry for sensitive-check-local using Typer.

本步仅提供占位命令：
- sensitive-check-local --help
- sensitive-check-local start [--port 8080] [--ingest-url <url>] [--ingest-key <key>] [--config <path>]
- sensitive-check-local stop
- sensitive-check-local status
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Any, Dict

import typer

from .config import load_config
from . import __version__
from . import server as _server

app = typer.Typer(
    add_completion=False,
    help="Sensitive Check 项目的本地助手 CLI。当前为最小可用版本，仅含占位命令。",
)

@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", help="显示版本并退出", is_eager=True
    ),
):
    """
    全局回调，支持 --version。
    """
    if version:
        typer.echo(f"sensitive-check-local {__version__}")
        raise typer.Exit()

@app.command("start")
def cmd_start(
    port: Optional[int] = typer.Option(
        None, "--port", help="本地代理端口（示例：8080）", min=1, max=65535
    ),
    ingest_url: Optional[str] = typer.Option(
        None, "--ingest-url", help="上报 API 地址（示例：https://your-domain/api/traffic/ingest/batch）"
    ),
    ingest_key: Optional[str] = typer.Option(
        None, "--ingest-key", help="上报鉴权密钥（示例：dev-ingest-key）"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="配置文件路径（YAML）"
    ),
):
    """
    启动占位：仅打印将要使用的配置（CLI > 环境变量 > 配置文件），不落地不执行。
    """
    overrides: Dict[str, Any] = {
        "port": port,
        "ingest_url": ingest_url,
        "ingest_key": ingest_key,
    }
    cfg = load_config(file_path=str(config) if config else None, overrides=overrides)
    typer.echo("[sensitive-check-local] 将使用如下配置（未落地）：")
    typer.echo(json.dumps(cfg, ensure_ascii=False, indent=2))
    typer.echo("占位：下一步将实现启动 mitmdump 与系统代理切换")
    raise typer.Exit(code=0)

@app.command("stop")
def cmd_stop():
    """
    停止占位：仅提示信息。
    """
    typer.echo("占位：下一步将实现停止与恢复系统代理")
    raise typer.Exit(code=0)

@app.command("status")
def cmd_status():
    """
    状态占位：输出固定 JSON。
    """
    placeholder = {
        "running": False,
        "pid": None,
        "port": None,
        "sessionId": None,
        "lastError": None,
    }
    typer.echo(json.dumps(placeholder, ensure_ascii=False))
    raise typer.Exit(code=0)

@app.command("serve")
def cmd_serve(
    host: str = typer.Option("127.0.0.1", "--host", help="监听地址"),  # 本地服务自身是在localhost启动的，这里保留127.0.0.1
    port: int = typer.Option(17866, "--port", help="监听端口，默认17866"),
):
    """
    启动本地助手 HTTP 服务（FastAPI）。
    """
    typer.echo(f"Starting sensitive-check-local server at http://{host}:{port}")
    _server.run(host=host, port=port)

if __name__ == "__main__":
    app()