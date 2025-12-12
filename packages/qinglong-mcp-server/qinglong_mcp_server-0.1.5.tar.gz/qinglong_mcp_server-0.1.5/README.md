# 青龙面板 MCP Server

[![PyPI version](https://badge.fury.io/py/qinglong-mcp-server.svg)](https://badge.fury.io/py/qinglong-mcp-server)

这是一个 Model Context Protocol (MCP) server，用于查询和执行青龙面板中的定时任务。

> **说明**：本仓库包含源代码，供开发者参考。普通用户请直接通过 pip 或 uvx 安装使用。

## 功能

- `list_qinglong_tasks`: 查询青龙面板中的所有定时任务列表
- `run_task`: 执行任务并等待完成，自动返回执行日志（最多等待30秒）
- `run_task_async`: 异步启动任务，不等待执行完成
- `get_task_logs`: 获取青龙面板中指定任务的执行日志
- `get_task_status`: 获取青龙面板中指定任务的执行状态
- `list_subscriptions`: 查询青龙面板中的所有订阅列表
- `run_subscription`: 运行指定的订阅

## 安装

使用 pip 安装：

```bash
pip install qinglong-mcp-server
```

或使用 uvx（推荐，无需安装）：

```bash
uvx qinglong-mcp-server
```

## 配置

首次运行时会自动创建配置文件模板。

编辑配置文件：

**macOS/Linux:**
```bash
nano ~/.qinglong-mcp/.env
```

**Windows:**
```cmd
notepad %USERPROFILE%\.qinglong-mcp\.env
```

填入你的青龙面板信息：

```
QINGLONG_URL=https://your-qinglong-url.com
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```

## 使用

### 在 MCP 客户端中使用

编辑 MCP 配置文件，添加以下内容：

```json
{
  "mcpServers": {
    "qinglong": {
      "command": "uvx",
      "args": ["qinglong-mcp-server"]
    }
  }
}
```

配置文件位置（以 Kiro CLI 为例）：
- `~/.kiro/settings/mcp.json`

### 开发测试

运行测试脚本：

```bash
./test_query_tasks.py
```

## 升级

```bash
pip install -U qinglong-mcp-server
```

## 项目地址

- PyPI: https://pypi.org/project/qinglong-mcp-server/
- GitHub: https://github.com/pholex/qinglong-mcp-server

## 联系方式

Email: pholex@gmail.com
