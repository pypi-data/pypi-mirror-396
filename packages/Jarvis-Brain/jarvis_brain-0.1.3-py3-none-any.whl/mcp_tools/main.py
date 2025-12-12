# main.py
from mcp_tools.dp_tools import *
from mcp_tools.requests_tools import *
from fastmcp import FastMCP

mcp = FastMCP("Jarvis Brain Mcp Tools")

# 根据环境变量加载模块
enabled_modules = os.getenv("MCP_MODULES", "TeamNode-Dp").split(",")

if "TeamNode-Dp" in enabled_modules:
    register_visit_url(mcp)
    register_close_tab(mcp)
    register_switch_tab(mcp)
    register_get_html(mcp)
    register_get_new_tab(mcp)
    register_check_selector(mcp)

if "JarvisNode" in enabled_modules:
    register_assert_waf(mcp)
    register_assert_Static_Web(mcp)


def main():
    mcp.run(transport="stdio")


if __name__ == '__main__':
    main()
