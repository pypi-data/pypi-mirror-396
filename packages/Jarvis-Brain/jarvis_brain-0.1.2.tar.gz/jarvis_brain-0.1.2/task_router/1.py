import asyncio
import os.path
import aiofiles.os as async_os
from typing import Callable, List
import json

from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeSDKClient, ClaudeAgentOptions

base_cwd = "/Users/user/PycharmProjects/JARVIS"


class SimpleTaskManager:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results = []

    async def execute_task(self, task_id: int, coro_func: Callable, *args, **kwargs):
        """执行单个任务"""
        async with self.semaphore:
            try:
                result = await coro_func(*args, **kwargs)
                self.results.append((task_id, result))
                print(f"✅ 任务 {task_id} 完成")
                return result
            except Exception as e:
                error_msg = f"任务 {task_id} 失败: {e}"
                self.results.append((task_id, error_msg))
                print(f"❌ {error_msg}")
                return None

    async def process_all(self, tasks: List[tuple]):
        """
        处理所有任务
        tasks: 列表，每个元素是 (coro_func, args, kwargs) 元组
        """
        print(f"🚀 开始处理 {len(tasks)} 个任务，最大并发数: {self.semaphore._value}")

        # 创建所有任务
        task_coroutines = []
        for i, (coro_func, args, kwargs) in enumerate(tasks):
            task_coroutines.append(self.execute_task(i, coro_func, *args, **kwargs))

        # 并发执行所有任务
        await asyncio.gather(*task_coroutines)

        print(f"🎉 所有任务完成！成功: {len([r for r in self.results if '失败' not in str(r[1])])}")
        return self.results


options = ClaudeAgentOptions(
    permission_mode='bypassPermissions',
    cwd=base_cwd,
    mcp_servers={
        "team-node-dp": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "/Users/user/PycharmProjects/JARVIS/mcp_tools",
                "main.py"
            ],
            "env": {
                "MCP_MODULES": "TeamNode-Dp"
            }
        },
        "jarvis-node": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "/Users/user/PycharmProjects/JARVIS/mcp_tools",
                "main.py"
            ],
            "env": {
                "MCP_MODULES": "JarvisNode"
            }
        },
    },
    # setting_sources=["project"],
    allowed_tools=[
        "mcp__team-node-dp__get_html",
        "mcp__team-node-dp__visit_url",
        "mcp__team-node-dp__get_new_tab",
        "mcp__team-node-dp__switch_tab",
        "mcp__team-node-dp__close_tab",
        "mcp__team-node-dp__check_selector",
        "mcp__jarvis-node__assert_Static_Web",  # 判断当前页面是否为静态页面
        "mcp__jarvis-node__assert_waf",  # 判断传入的url是否使用了瑞数，jsl等防火墙
        'Read',
        'Write',
        'Edit',
        'MultiEdit',
        'Grep',
        'Glob',
        'TodoWrite'
    ]
)


# 使用自定义工具与 Claude


async def run(url):
    from urllib.parse import urlparse
    print(f"开始任务：{url}")
    parser = urlparse(url)
    domain = parser.netloc
    analysis_file_path = os.path.join(base_cwd, f'{domain}.json')
    async with ClaudeSDKClient(options=options) as client:
        # prompt = f"请使用mcp工具打开网页：{url}"
        prompt = f"""请使用mcp工具告诉我网页{url}，是否存在waf，以及是否为静态网页，分析完成后关闭浏览器。
                    将分析结果存放在{analysis_file_path}中。
                    json文件的格式为:
                    {{
                        "url": "http://www.customs.gov.cn/customs/xwfb34/302425/index.html",
                        "site_name":"今日海关"
                        "waf_type":"瑞数",
                        "static":true,
                        "static_possibility":96%
                    }}
                    """
        # prompt = f"请列出所有你可以使用的mcp工具"
        await client.query(prompt)

        # 提取并打印响应
        async for msg in client.receive_response():
            print(msg)


async def main():
    tasks = []
    with open("/Users/user/Desktop/mapping_copy.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    mapping = dict(list(mapping.items()))
    for key, value in mapping.items():
        tasks.append((run, (), {  # 关键字参数字典
            "url": value,
        }))
    manager = SimpleTaskManager(max_concurrent=1)
    results = await manager.process_all(tasks)
    # 输出结果
    print("\n任务结果摘要:")
    for task_id, result in results[:5]:  # 只显示前5个
        print(f"  任务 {task_id}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
