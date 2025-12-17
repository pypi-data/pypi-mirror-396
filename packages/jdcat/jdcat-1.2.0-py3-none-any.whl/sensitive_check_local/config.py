"""
Configuration loader for the sensitive-check-local CLI.

Precedence: CLI overrides > environment variables > config file > defaults.
This step returns a plain dict only; no validation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

DEFAULTS: Dict[str, Any] = {
    "realtime": {
        "batchIntervalSec": 10,
        "batchSize": 5,
        "maxQueueSize": 1000,
        "finalFlushOnStop": True
    },
    "notify": {
        "intervalSec": 30
    },
    "paramTest": {
        # 生成阶段调度间隔：扫描待测接口并入队“测试数据生成”的频率
        # 间隔过小会增加本地与后端压力，过大则降低时效性；单位秒
        "runIntervalSec": 12,

        # 执行阶段调度间隔：把已生成完成的接口派发到“测试执行”队列的频率
        # 与内部每分钟执行上限配合使用，防止短时间内过量请求；单位秒
        "executeIntervalSec": 10,

        # 生成完成后是否自动触发断言检查：开启后会将接口加入断言查询队列
        # 关闭时需要手动触发或依赖其它调度器，否则断言结果不会自动更新
        "triggerAfterCompleteEnable": True,

        # 从“生成完成”到触发断言检查的等待时间：给后端入库/索引预留缓冲
        # 延迟过短可能导致首次断言查询为空或进行中；单位秒
        "triggerAfterCompleteDelaySec": 10,

        # 断言检查并发工作线程数：并行查询外部断言结果的数量
        # 数值越大并发越高，但可能触发限流或占用更多CPU；按后端QPS与本机性能调整
        "assertionWorkerCount": 3,

        # 断言队列轮询间隔：每次批量取待断言任务并发起查询的周期；单位秒
        # 间隔过小会造成高频轮询，过大则断言完成判定不够及时
        "assertionIntervalSec": 5,

        # 单个接口首次断言查询的初始延迟：避免生成刚完成就立即查询导致为空/未完成
        # 与最大尝试次数配合使用，提高断言结果的命中率；单位秒
        "assertionCheckDelaySec": 20,

        # 断言查询最大尝试次数：在每次延迟后重复查询的上限
        # 若超过该次数仍未返回 finished，则本次断言终止；默认 5 次
        "assertionCheckMaxAttempts": 5,

        # 生成阶段运行超时时间（秒）：超过该时长仍未完成则标记失败
        "runningTimeoutSec": 300
    }
}

# Default bypass domains for macOS system proxy
DEFAULT_BYPASS: list[str] = ["aq.jdtest.net", "aqapi.jdtest.local", "0.0.0.0", "::1"]

# Default authorization prompt message for macOS admin privileges
DEFAULT_AUTH_PROMPT: str = "jdcat 需要管理员权限来配置系统代理设置，以便进行安全测试。"

# Default authorization dialog title for macOS admin privileges
DEFAULT_AUTH_TITLE: str = "jdcat 安全测试工具"

# Mapping from logical config keys to environment variable names (in priority order)
ENV_MAP: Dict[str, list[str]] = {
    "port": ["SCL_PORT", "TRAFFIC_TOOLS_PORT"],
    "ingest_url": ["SCL_INGEST_URL", "TRAFFIC_TOOLS_INGEST_URL"],
    "ingest_key": ["SCL_INGEST_KEY", "TRAFFIC_TOOLS_INGEST_KEY"],
    # identity fields for isolation/auditing
    "user_id": ["SCL_USER_ID", "TRAFFIC_TOOLS_USER_ID", "USER_ID"],
    "project_id": ["SCL_PROJECT_ID", "TRAFFIC_TOOLS_PROJECT_ID", "PROJECT_ID"],
    "task_id": ["SCL_TASK_ID", "TRAFFIC_TOOLS_TASK_ID", "TASK_ID"],
    # macOS authorization prompt customization
    "auth_prompt": ["SCL_AUTH_PROMPT", "JDCAT_AUTH_PROMPT"],
    "auth_title": ["SCL_AUTH_TITLE", "JDCAT_AUTH_TITLE"],
}

def _first_nonempty(values: list[Optional[str]]) -> Optional[str]:
    for v in values:
        if v is not None and str(v).strip() != "":
            return v
    return None

def _read_yaml_file(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data, dict):
            return data
        return {}
    except FileNotFoundError:
        return {}
    except Exception:
        # Keep it silent for this minimal step; later we can add logging
        return {}

def _discover_config_path(explicit_path: Optional[str]) -> Optional[Path]:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    env_path = os.environ.get("SCL_CONFIG") or os.environ.get("TRAFFIC_TOOLS_CONFIG")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path.cwd() / "config.yaml")
    # Repo example location (when running from source tree)
    candidates.append(Path(__file__).resolve().parents[1] / "config.yaml")
    for p in candidates:
        try:
            if p.is_file():
                return p
        except Exception:
            continue
    return None

def _env_config() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, names in ENV_MAP.items():
        for name in names:
            val = os.environ.get(name)
            if val is None or str(val).strip() == "":
                continue
            if key == "port":
                try:
                    out[key] = int(val)
                except ValueError:
                    # Ignore invalid int; later steps can add validation
                    pass
            else:
                out[key] = val
            break  # first hit wins
    return out

def _drop_none(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}

def load_config(file_path: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Merge configuration dictionaries with precedence:
    overrides (CLI) > environment > config file > defaults.
    """
    cfg_path = _discover_config_path(file_path)
    file_cfg = _read_yaml_file(cfg_path) if cfg_path else {}
    env_cfg = _env_config()
    cli_cfg = _drop_none(overrides or {})

    merged: Dict[str, Any] = {}
    merged.update(DEFAULTS)
    merged.update(file_cfg or {})
    merged.update(env_cfg or {})
    merged.update(cli_cfg or {})
    return merged
