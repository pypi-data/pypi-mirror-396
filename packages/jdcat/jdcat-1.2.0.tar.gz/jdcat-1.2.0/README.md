# JDCat

JDCat 是一个 Python 包装工具，提供命令行入口来启动本地安全测试助手服务。该服务是 sensitive-check-local 项目的 FastAPI 服务封装，用于安全测试中的代理和数据捕获。

## 项目说明

- **功能**：包装并启动本地助手 FastAPI 服务，提供安全测试所需的代理功能
- **技术栈**：Python 3.10-3.14, FastAPI, uvicorn, mitmproxy
- **默认端口**：17866
- **业务逻辑**：完全来自 sensitive-check-local 项目，本包仅提供 CLI 入口

## 本地调试

### 开发环境安装
```bash
# 克隆项目并进入 jdcat 目录
cd jdcat

# 安装开发依赖（可编辑模式）
uv pip install -e .
```

### 本地开发调试
```bash
# 使用本地代码运行（推荐开发方式，默认会自动打开浏览器）
uv run python -m jdcat start

# 或者直接运行模块
python -m jdcat start

# 启动但不自动打开浏览器
uv run python -m jdcat start --no-open-browser

# 停止服务
uv run python -m jdcat stop
```

### 构建测试
```bash
# 构建包
uv pip install -U build
python -m build

# 验证构建结果
ls -la dist/
```

## 分发服务

### 一键构建和发布
```bash
# 在 jdcat 目录下执行构建脚本
./build_and_publish.sh
```

该脚本会自动完成：
- 清理之前的构建文件
- 安装构建工具（build、twine）
- 构建分发包（wheel 和 tar.gz）
- 检查包完整性
- 可选择上传到 PyPI 或 Test PyPI

## 分发后使用

### 安装方式

**使用 pip（推荐）**

```bash
# 安装最新版本
pip install jdcat

# 升级到最新版本
pip install --upgrade jdcat

# 安装指定版本
pip install jdcat==1.0.4
```

**使用 pipx（隔离安装）**

```bash
# 安装 pipx
python -m pip install --user pipx
python -m pipx ensurepath

# 安装 jdcat 最新版本
pipx install jdcat

# 升级 jdcat 到最新版本
pipx upgrade jdcat

# 强制重新安装最新版本
pipx uninstall jdcat && pipx install jdcat
```

**使用 uv（快速安装）**

```bash
# 直接运行最新版本（无需安装）
uv run --from jdcat jdcat start

# 安装到全局
uv tool install jdcat

# 升级到最新版本
uv tool upgrade jdcat
```

### 基本使用

```bash
# 启动服务（默认会自动打开浏览器到 http://aq.jdtest.net:8007/）
jdcat start

# 启动服务但不自动打开浏览器
jdcat start --no-open-browser

# 启动服务并指定自定义浏览器URL
jdcat start --browser-url "http://localhost:8007/"

# 指定端口启动服务
jdcat start --port 18000

# 停止服务
jdcat stop

# 查看帮助
jdcat --help

# 检查版本
jdcat --version
```

### 常见问题

**externally-managed-environment 错误**
- 原因：现代 Python 环境管理安全特性（PEP 668）
- 解决：使用 uv 或 pipx 安装，避免直接在系统 Python 中安装
```bash
# 推荐使用 uv
uv run --from jdcat jdcat start --port 17866

# 或使用 pipx
pipx install jdcat
```

**mitmdump 不存在**
- 原因：jdcat 依赖 mitmproxy 提供的 mitmdump 工具
- 解决方案：
  1. **检查版本**：确保使用最新版本的 jdcat
     ```bash
     # 检查当前版本
     jdcat --version
     
     # 升级到最新版本（当前：1.0.3）
     pip install --upgrade jdcat
     
     # 或使用 pipx
     pipx upgrade jdcat
     ```
  2. **重新安装**：完全重新安装 jdcat 和依赖
     ```bash
     # 使用 pip
     pip uninstall jdcat mitmproxy
     pip install jdcat
     
     # 使用 pipx
     pipx uninstall jdcat
     pipx install jdcat
     ```
  3. **手动安装 mitmproxy**：
     ```bash
     # macOS
     brew install mitmproxy
     
     # 使用 pip
     pip install mitmproxy
     
     # 验证安装
     mitmdump --version
     ```
  4. **使用 uv（推荐）**：
     ```bash
     # 直接运行，自动处理依赖
     uv run --from jdcat jdcat start
     ```

**端口占用**
- 解决：指定其他端口
```bash
jdcat start --port 18000
```

## 开源信息

- 作者：Sensitive Check Team
- 许可：详见 LICENSE 文件
- Python 版本：3.10 - 3.14