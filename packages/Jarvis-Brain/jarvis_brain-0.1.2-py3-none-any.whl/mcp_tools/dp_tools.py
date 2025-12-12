import json
import os
import random
from pyexpat.errors import messages
from typing import Any

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage._elements.none_element import NoneElement
from fastmcp import FastMCP

from tools.tools import compress_html, requests_html
from tools.simhash_tools import HTMLSimHashComparator

html_source_code_local_save_path = os.path.join(os.getcwd(), "html-source-code")
browser_pool = {}


# 随机一个浏览器池中不存在的端口，创建一个浏览器，返回随机端口，和浏览器对象。
def create_browser():
    global browser_pool
    random_port = random.randint(9222, 9934)
    while random_port in browser_pool:
        random_port = random.randint(9222, 9934)
    co = ChromiumOptions().set_local_port(random_port)
    browser_pool[random_port] = ChromiumPage(co)
    return random_port, browser_pool[random_port]


# 根据传入的端口查找对应的浏览器对象
def get_page(port):
    return browser_pool.get(port, None)


# 根据传入的端口查找并弹出一个浏览器对象
def remove_page(port):
    browser = browser_pool.pop(port, None)
    return browser is not None, browser


def register_visit_url(mcp: FastMCP):
    @mcp.tool(name="visit_url", description="使用Drissionpage打开url访问某个网站")
    async def visit_url(url: str) -> dict[str, Any]:
        port, _browser = create_browser()
        tab = _browser.get_tab()
        tab.get(url)
        tab_id = tab.tab_id
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已在[{port}]端口创建浏览器对象，并已打开链接：{url}",
                    "tab_id": tab_id,
                    "browser_port": port,
                }, ensure_ascii=False)
            }]
        }


def register_get_html(mcp: FastMCP):
    @mcp.tool(name="get_html", description="使用Drissionpage获取某一个tab页的html")
    async def get_html(browser_port: int, tab_id: str) -> dict[str, Any]:
        _browser = get_page(browser_port)
        tab = _browser.get_tab(tab_id)
        file_name = tab.title + f"_{tab_id}.html"
        if not os.path.exists(html_source_code_local_save_path):
            os.makedirs(html_source_code_local_save_path)
        abs_path = os.path.join(html_source_code_local_save_path, file_name)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(compress_html(tab.html))
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已保存tab页：【{tab_id}】的html源码",
                    "tab_id": tab_id,
                    "html_local_path": abs_path
                }, ensure_ascii=False)
            }]
        }


def register_get_new_tab(mcp: FastMCP):
    @mcp.tool(name="get_new_tab", description="使用Drissionpage创建一个新的tab页，在新的tab页中打开url")
    async def get_new_tab(browser_port: int, url: str) -> dict[str, Any]:
        _browser = get_page(browser_port)
        tab = _browser.new_tab(url)
        _browser.activate_tab(tab)
        tab_id = tab.tab_id
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已创建新的tab页，并打开链接：{url}",
                    "tab_id": tab_id,
                }, ensure_ascii=False)
            }]
        }


def register_switch_tab(mcp: FastMCP):
    @mcp.tool(name="switch_tab", description="根据传入的tab_id切换到对应的tab页", )
    async def switch_tab(browser_port: int, tab_id: str) -> dict[str, Any]:
        _browser = get_page(browser_port)
        _browser.activate_tab(tab_id)
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已将tab页:【{tab_id}】切换至最前端",
                }, ensure_ascii=False)
            }]
        }


def register_close_tab(mcp: FastMCP):
    @mcp.tool(name="close_tab", description="根据传入的tab_id关闭tab页", )
    async def close_tab(browser_port, tab_id) -> dict[str, Any]:
        _browser = get_page(browser_port)
        _browser.close_tabs(tab_id)
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已将tab页:【{tab_id}】关闭",
                }, ensure_ascii=False)
            }]
        }


def register_check_selector(mcp: FastMCP):
    @mcp.tool(name="check_selector", description="查找tab页中是否包含元素")
    async def check_selector(browser_port: int, tab_id: str, css_selector: str) -> dict[str, Any]:
        _browser = get_page(browser_port)
        target_tab = _browser.get_tab(tab_id)
        css_selector = css_selector
        if "css:" not in css_selector:
            css_selector = "css:" + css_selector
        target_ele = target_tab.ele(css_selector)
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已完成tab页:【{tab_id}】对：【{css_selector}】的检查",
                    "tab_id": tab_id,
                    "selector": css_selector,
                    "selector_ele_exist": not isinstance(target_ele, NoneElement),
                }, ensure_ascii=False)
            }]
        }


def register_quit_browser(mcp: FastMCP):
    @mcp.tool(name="quit_browser", description="退出浏览器会话，关闭浏览器")
    async def quit_browser(browser_port: int) -> dict[str, Any]:
        flag, _browser = remove_page(browser_port)
        if flag:
            _browser.quit()
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"浏览器[{browser_port}]，退出会话，关闭浏览器{'成功' if flag else '失败'}",
                    "browser_port": browser_port,
                    "quit_flag": flag,
                }, ensure_ascii=False)
            }]
        }


def register_assert_Static_Web(mcp: FastMCP):
    @mcp.tool(name="assert_Static_Web", description="判断tab页中的网页是否是静态网页")
    def assert_Static_Web(browser_port: int, tab_id: str) -> dict[str, Any]:
        _browser = get_page(browser_port)
        target_tab = _browser.get_tab(tab_id)
        target_url = target_tab.url
        raw_html, stat_code = requests_html(target_url)
        if stat_code != 200:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "messages": f"已完成tab页:【{tab_id}】的分析，该tab页使用requests获取的html状态码为[{stat_code}]，并非200，请使用assert_waf判断是否有waf",
                        "tab_id": tab_id,
                        "url": target_url,
                        "stat_code": stat_code,
                    }, ensure_ascii=False)
                }]
            }
        render_html = target_tab.html
        comparator = HTMLSimHashComparator(raw_html, render_html, False)
        result = comparator.compare_simhash()
        print("SimHash比较结果:")
        print(f"页面1 SimHash: {result['simhash1']}")
        print(f"页面2 SimHash: {result['simhash2']}")
        print(f"汉明距离: {result['hamming_distance']}")
        print(f"相似度: {result['similarity_percentage']}")
        threshold_result = comparator.compare_with_threshold(threshold=0.7)
        print(f"\n基于阈值{threshold_result['threshold']}的判断:")
        print(f"是否相似: {threshold_result['is_similar']}")
        static_html_flag = threshold_result['is_similar']
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": f"已完成tab页:【{tab_id}】的分析，该tab页静态页面和渲染页面的相似度为[{result['similarity_percentage']}]，判定为 {'静态页面' if static_html_flag else '动态渲染'}",
                    "tab_id": tab_id,
                    "is_static_web": static_html_flag,
                    "static_web_possibility": result['similarity_percentage'],
                }, ensure_ascii=False)
            }]
        }
