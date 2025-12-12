#!/usr/bin/env python3
import json
import sys
import os
import requests
import logging
import time
from dotenv import load_dotenv
from pathlib import Path

logging.disable(logging.CRITICAL)

# 尝试从多个位置加载 .env 文件
env_paths = [
    Path.cwd() / ".env",  # 当前工作目录
    Path.home() / ".qinglong-mcp" / ".env",  # 用户主目录
    Path(__file__).parent / ".env",  # 脚本所在目录
]

# 如果配置文件不存在，自动创建
config_dir = Path.home() / ".qinglong-mcp"
config_file = config_dir / ".env"
if not config_file.exists():
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        "QINGLONG_URL=https://your-qinglong-url.com\n"
        "CLIENT_ID=your_client_id\n"
        "CLIENT_SECRET=your_client_secret\n"
    )

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

QINGLONG_URL = os.getenv("QINGLONG_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_token():
    if not all([QINGLONG_URL, CLIENT_ID, CLIENT_SECRET]):
        return None
    try:
        url = f"{QINGLONG_URL}/open/auth/token"
        params = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        return result["data"]["token"] if result.get("code") == 200 else None
    except Exception:
        return None

def main():
    for line in sys.stdin:
        request = None
        try:
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            method = request.get("method")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "qinglong-mcp", "version": "1.0.0"}
                    }
                }
                print(json.dumps(response), flush=True)
            elif method == "notifications/initialized":
                pass  # Notifications don't require response
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "result": {
                        "tools": [
                            {
                                "name": "list_qinglong_tasks",
                                "description": "查询青龙面板中的所有定时任务列表",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            {
                                "name": "run_task",
                                "description": "执行任务并等待完成，返回执行日志（最多等待30秒）",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "integer", "description": "任务 ID"}
                                    },
                                    "required": ["task_id"]
                                }
                            },
                            {
                                "name": "run_task_async",
                                "description": "异步启动任务，不等待执行完成",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "integer", "description": "任务 ID"}
                                    },
                                    "required": ["task_id"]
                                }
                            },
                            {
                                "name": "get_task_logs",
                                "description": "获取青龙面板中指定任务的执行日志",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "integer", "description": "任务 ID"}
                                    },
                                    "required": ["task_id"]
                                }
                            },
                            {
                                "name": "get_task_status",
                                "description": "获取青龙面板中指定任务的执行状态",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "integer", "description": "任务 ID"}
                                    },
                                    "required": ["task_id"]
                                }
                            },
                            {
                                "name": "list_subscriptions",
                                "description": "查询青龙面板中的所有订阅列表",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            {
                                "name": "run_subscription",
                                "description": "运行指定的订阅",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "subscription_id": {"type": "integer", "description": "订阅 ID"}
                                    },
                                    "required": ["subscription_id"]
                                }
                            }
                        ]
                    }
                }
                print(json.dumps(response), flush=True)
            elif method == "tools/call":
                tool_name = request["params"]["name"]
                arguments = request["params"]["arguments"]
                
                token = get_token()
                if not token:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request["id"],
                        "error": {"code": -32603, "message": "获取 token 失败，请检查凭证是否正确"}
                    }
                    print(json.dumps(response), flush=True)
                    continue
                
                if tool_name == "list_qinglong_tasks":
                    try:
                        url = f"{QINGLONG_URL}/open/crons"
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = requests.get(url, headers=headers, timeout=10)
                        result = resp.json()
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"请求失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    if result.get("code") == 200:
                        data = result["data"]
                        crons = data.get("data", [])
                        crons.sort(key=lambda x: x.get('id', 0))
                        total = data.get("total", 0)
                        
                        output = f"青龙面板: {QINGLONG_URL}\n共 {total} 个任务:\n\n"
                        for cron in crons:
                            output += f"ID: {cron.get('id')}\n"
                            output += f"名称: {cron.get('name')}\n"
                            output += f"命令: {cron.get('command')}\n"
                            output += f"定时: {cron.get('schedule')}\n"
                            output += f"状态: {'启用' if cron.get('isDisabled') == 0 else '禁用'}\n"
                            last_running = cron.get('last_running_time')
                            if last_running:
                                output += f"上次运行时长: {last_running}秒\n"
                            output += "-" * 50 + "\n"
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": output}]}
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"获取任务列表失败: {result}"}
                        }
                
                elif tool_name == "run_task_async":
                    task_id = arguments.get("task_id")
                    try:
                        url = f"{QINGLONG_URL}/open/crons/run"
                        headers = {"Authorization": f"Bearer {token}"}
                        data = [task_id]
                        
                        resp = requests.put(url, headers=headers, json=data, timeout=10)
                        result = resp.json()
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"请求失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    if result.get("code") == 200:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": f"任务 {task_id} 已成功启动"}]}
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"运行任务失败: {result}"}
                        }
                
                elif tool_name == "get_task_logs":
                    task_id = arguments.get("task_id")
                    try:
                        url = f"{QINGLONG_URL}/open/crons/{task_id}"
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = requests.get(url, headers=headers, timeout=10)
                        result = resp.json()
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"请求失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    if result.get("code") == 200:
                        cron = result["data"]
                        log_path = cron.get("log_path", "")
                        
                        if log_path:
                            try:
                                log_url = f"{QINGLONG_URL}/open/crons/{task_id}/log"
                                log_resp = requests.get(log_url, headers=headers, timeout=10)
                                log_result = log_resp.json()
                                
                                if log_result.get("code") == 200:
                                    log_content = log_result["data"]
                                    output = f"任务 {task_id} ({cron.get('name')}) 的执行日志:\n\n{log_content}"
                                else:
                                    output = f"获取日志失败: {log_result}"
                            except Exception as e:
                                output = f"读取日志失败: {str(e)}"
                        else:
                            output = f"任务 {task_id} ({cron.get('name')}) 暂无执行日志"
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": output}]}
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"获取任务信息失败: {result}"}
                        }
                
                elif tool_name == "get_task_status":
                    task_id = arguments.get("task_id")
                    try:
                        url = f"{QINGLONG_URL}/open/crons/{task_id}"
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = requests.get(url, headers=headers, timeout=10)
                        result = resp.json()
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"请求失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    if result.get("code") == 200:
                        cron = result["data"]
                        status_map = {0: "运行中", 1: "空闲", 2: "禁用"}
                        status = status_map.get(cron.get("status"), "未知")
                        
                        output = f"任务 {task_id} 状态信息:\n\n"
                        output += f"名称: {cron.get('name')}\n"
                        output += f"状态: {status}\n"
                        output += f"是否禁用: {'是' if cron.get('isDisabled') == 1 else '否'}\n"
                        output += f"是否置顶: {'是' if cron.get('isPinned') == 1 else '否'}\n"
                        last_running = cron.get('last_running_time')
                        output += f"上次运行时长: {last_running}秒\n" if last_running else "上次运行时长: 未运行\n"
                        output += f"最后执行时间: {cron.get('last_execution_time', '未执行')}\n"
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": output}]}
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"获取任务状态失败: {result}"}
                        }
                
                elif tool_name == "run_task":
                    task_id = arguments.get("task_id")
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    try:
                        url = f"{QINGLONG_URL}/open/crons/run"
                        resp = requests.put(url, headers=headers, json=[task_id], timeout=10)
                        result = resp.json()
                        if result.get("code") != 200:
                            response = {
                                "jsonrpc": "2.0",
                                "id": request["id"],
                                "error": {"code": -32603, "message": f"启动任务失败: {result}"}
                            }
                            print(json.dumps(response), flush=True)
                            continue
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"启动任务失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    time.sleep(2)
                    response = None
                    task_started = False
                    
                    for _ in range(6):
                        time.sleep(5)
                        try:
                            status_url = f"{QINGLONG_URL}/open/crons/{task_id}"
                            status_resp = requests.get(status_url, headers=headers, timeout=10)
                            status_result = status_resp.json()
                            
                            if status_result.get("code") == 200:
                                cron = status_result["data"]
                                task_status = cron.get("status")
                                
                                # status: 0=运行中, 1=空闲
                                if task_status == 0:
                                    task_started = True
                                elif task_status == 1 and task_started:
                                    log_url = f"{QINGLONG_URL}/open/crons/{task_id}/log"
                                    log_resp = requests.get(log_url, headers=headers, timeout=10)
                                    log_result = log_resp.json()
                                    
                                    if log_result.get("code") == 200:
                                        response = {
                                            "jsonrpc": "2.0",
                                            "id": request["id"],
                                            "result": {"content": [{"type": "text", "text": log_result["data"]}]}
                                        }
                                    else:
                                        response = {
                                            "jsonrpc": "2.0",
                                            "id": request["id"],
                                            "error": {"code": -32603, "message": f"获取日志失败: {log_result}"}
                                        }
                                    break
                        except Exception as e:
                            response = {
                                "jsonrpc": "2.0",
                                "id": request["id"],
                                "error": {"code": -32603, "message": f"检查任务失败: {str(e)}"}
                            }
                            break
                    
                    if response is None:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": f"任务 {task_id} 超时（30秒），请使用 get_task_logs 查看日志"}]}
                        }
                
                elif tool_name == "list_subscriptions":
                    try:
                        url = f"{QINGLONG_URL}/open/subscriptions"
                        headers = {"Authorization": f"Bearer {token}"}
                        resp = requests.get(url, headers=headers, timeout=10)
                        result = resp.json()
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"请求失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    if result.get("code") == 200:
                        subscriptions = result["data"] if isinstance(result["data"], list) else []
                        subscriptions.sort(key=lambda x: x.get('id', 0))
                        total = len(subscriptions)
                        
                        output = f"青龙面板: {QINGLONG_URL}\n共 {total} 个订阅:\n\n"
                        for sub in subscriptions:
                            output += f"ID: {sub.get('id')}\n"
                            output += f"名称: {sub.get('name')}\n"
                            output += f"URL: {sub.get('url')}\n"
                            output += f"类型: {sub.get('type')}\n"
                            output += f"定时: {sub.get('schedule')}\n"
                            output += f"状态: {'启用' if sub.get('is_disabled') == 0 else '禁用'}\n"
                            output += "-" * 50 + "\n"
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": output}]}
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"获取订阅列表失败: {result}"}
                        }
                
                elif tool_name == "run_subscription":
                    subscription_id = arguments.get("subscription_id")
                    try:
                        url = f"{QINGLONG_URL}/open/subscriptions/run"
                        headers = {"Authorization": f"Bearer {token}"}
                        data = [subscription_id]
                        
                        resp = requests.put(url, headers=headers, json=data, timeout=10)
                        result = resp.json()
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"请求失败: {str(e)}"}
                        }
                        print(json.dumps(response), flush=True)
                        continue
                    
                    if result.get("code") == 200:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "result": {"content": [{"type": "text", "text": f"订阅 {subscription_id} 已成功运行"}]}
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request["id"],
                            "error": {"code": -32603, "message": f"运行订阅失败: {result}"}
                        }
                
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request["id"],
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }
                
                print(json.dumps(response), flush=True)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
                print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if request else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
