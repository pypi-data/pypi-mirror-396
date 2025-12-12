import json

from fastmcp import FastMCP
from tools.tools import requests_html, dp_headless_html


def register_assert_waf(mcp: FastMCP):
    @mcp.tool(name="assert_waf", description="判断传入的url对应的网页是否存在瑞数、jsl等风控防火墙")
    def assert_waf(url: str):
        # 先试用requests判断瑞数和jsl
        text, code = requests_html(url)
        waf_text_type = {
            521: "jsl",
            412: "瑞数",
            "触发WAF": "其他waf"
        }
        has_waf = code in waf_text_type.keys()
        if not has_waf:
            # 不是瑞数和jsl，使用无头浏览器判断是否为其他waf
            headless_html = dp_headless_html(url)
            if "触发WAF" in headless_html:
                has_waf = True
                code = "触发WAF"
        if not has_waf:
            waf_type = "不存在waf"
        else:
            waf_type = waf_text_type[code]
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(
                    {
                        "message": f"链接{url} [{'存在' if has_waf else '不存在'}] waf",
                        "url": url,
                        "waf_type": waf_type,
                        "has_waf": has_waf
                    }, ensure_ascii=False
                )
            }]
        }
