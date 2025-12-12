import time

import htmlmin
from curl_cffi import requests
from lxml import html, etree
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions


# 传入requests的set-cookie的str，返回一个cookie dict
def cookie_str2dict(cookie_str: str):
    if cookie_str == "":
        return {}
    cookie_dict = {}
    cookie_list = [cookie.split(";")[0] for cookie in cookie_str.split("HttpOnly,")]
    for cookie in cookie_list:
        key, value = cookie.split("=")
        cookie_dict[key] = value
    return cookie_dict


# 使用requests获取html，用于测试是否使用了瑞数和jsl
def requests_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers, verify=False)
    # print("response headers=> ", type(response.headers.get("Set-Cookie")),
    #       cookie_str2dict(response.headers.get("Set-Cookie", "")))
    response.encoding = "utf-8"
    return response.text, response.status_code


# 使用dp无头模式获取html，用于测试是否使用了其他waf，如移动waf
def dp_headless_html(url):
    opt = ChromiumOptions().headless(True)
    opt.set_argument('--no-sandbox')
    opt.set_local_port(9976)

    page = ChromiumPage(opt)
    # page = ChromiumPage()

    tab = page.latest_tab
    # tab.set.load_mode.normal()
    tab.get(url)
    # tab.wait.eles_loaded()
    time.sleep(10)
    # tab.wait.load_start()
    page_html = tab.html
    # print(page_html)
    # print("dp_cookies=>", tab.cookies())
    page.quit()
    return page_html


# 使用dp无头模式获取html，用于测试是否使用了其他waf，如移动waf
def dp_html(url):
    opt = ChromiumOptions()
    opt.set_local_port(9223)
    # opt.set_argument('--no-sandbox')
    page = ChromiumPage(opt)
    # page = ChromiumPage()

    tab = page.latest_tab
    # tab.set.load_mode.normal()
    tab.get(url)
    # tab.wait.eles_loaded()
    # time.sleep(10)

    tab.wait.doc_loaded()
    page_html = tab.html
    # print(page_html)
    # print("dp_cookies=>", tab.cookies())
    page.quit()
    return page_html


# 压缩html
def compress_html(content, only_text=False):
    doc = html.fromstring(content)
    # 删除 style 和 script 标签
    for element in doc.xpath('//style | //script'):
        element.getparent().remove(element)

    # 删除 link 标签
    for link in doc.xpath('//link[@rel="stylesheet"]'):
        link.getparent().remove(link)

    # 删除 meta 标签（新增功能）
    for meta in doc.xpath('//meta'):
        meta.getparent().remove(meta)

    # 删除 style 属性
    for element in doc.xpath('//*[@style]'):
        element.attrib.pop('style')

    # 删除所有 on* 事件属性
    for element in doc.xpath('//*'):
        for attr in list(element.attrib.keys()):
            if attr.startswith('on'):
                element.attrib.pop(attr)

    result = etree.tostring(doc, encoding='unicode')
    result = htmlmin.minify(result)
    print(f"html压缩比=> {len(content) / len(result) * 100:.2f}%")
    if not only_text:
        return result
    soup = BeautifulSoup(result, 'html.parser')
    result = soup.get_text(strip=True)
    return result


def test(target_url):
    raw_html, status_code = requests_html(target_url)
    raw_html = compress_html(raw_html, only_text=True)
    # print("raw_html=>", status_code, compress_html(raw_html))
    print("raw_html=>", status_code, raw_html)
    page_html = dp_html(target_url)
    page_html = compress_html(page_html, only_text=True)
    # print("render_text=>", compress_html(page_html))
    print("render_text_head=>", page_html)

    page_html = dp_headless_html(target_url)
    page_html = compress_html(page_html, only_text=True)
    # print("render_text=>", compress_html(page_html))
    print("render_text=>", page_html)

    # print("\n")
    # raw_html, status_code = requests_html(target_url)
    # raw_html = compress_html(raw_html, only_text=True)
    # # print("raw_html=>", status_code, compress_html(raw_html))
    # print("raw_html=>", status_code, raw_html)
    # print("\n")


if __name__ == '__main__':
    # raw_html, status_code = requests_html("https://www.nxzgh.org.cn/#/newsCenter/index2/2")
    # raw_html, status_code = requests_html("http://www.ncha.gov.cn/col/col722/index.html")
    # raw_html, status_code = requests_html("https://scgh.org/page/news/tmore36403294e28a11ea8ba48cec4b967595.html")
    # raw_html, status_code = requests_html("https://scgh.org/page/news/tmore36403294e28a11ea8ba48cec4b967595.html")
    # url = "https://www.nmpa.gov.cn/yaowen/ypjgyw/index.html"
    # url = "http://www.customs.gov.cn/customs/xwfb34/302425/index.html"
    # url = "https://scgh.org/page/news/tmore36403294e28a11ea8ba48cec4b967595.html"
    # url = "https://www.gjxfj.gov.cn/gjxfj/news/ttxw.htm"
    # url = "https://www.gsgh.org.cn/#/moreNews_?position=%E7%9C%81%E6%80%BB%E6%96%B0%E9%97%BB&categoryId=502"
    url = "https://www.acftu.org/xwdt/ghyw/"
    # url = "https://www.nxzgh.org.cn/#/newsCenter/index2/2"  # 移动waf，会检测浏览器无头
    # url = "https://www.chengdu.gov.cn/cdsrmzf/zfxx/cjj.shtml" # 超严格瑞数6，怀疑他会检测端口，我使用9222端口无论如何都获取不到结果
    # url = "https://www.jsgh.org/col/col3577/index.html?uid=18462&pageNum=1"
    # render_html = dp_headless_html(url)
    # print("\n")
    # print("render_html=>", render_html)
    # for i in range(20):
    test(url)
    # todo: 大致盘一下各种判定的逻辑【以下的所有压缩比之间的差距均取“绝对值”】
    #  1. 如果requests、无头、有头获取到的压缩比之间从差距都在15%以内，则认定该页面是静态页面，此时优先使用requests请求
    #  2. 如果requests的status_code为特定的412，或者521，则判定是瑞数和jsl。[此时还有一个特点：requests的压缩比会与其他两种方式获取到的压缩比差距非常大(一两千的那种)]
    #  3. 如果requests、无头、有头获取到的压缩比之间差距都在40%以上，则判定该页面只可以用有头采集
    #  4. 如果无头和有头获取到的压缩比之间差距小于15%，但是requests和无头的差距大于40%，则认定该页面可以使用无头浏览器采集
    #  5. 如果requests和有头获取到的压缩比之间差距小于15%，但是无头和有头的差距大于40%，则认定该页面优先使用有头浏览器采集
    #  【此时可能是：1.使用了别的检测无头的waf。2.网站使用瑞数，但是这次请求没有拦截requests（不知道是不是瑞数那边故意设置的），
    #   此时如果想进一步判定是否是瑞数，可以使用有头浏览器取一下cookies，如果cookies里面存在瑞数的cookie，那么就可以断定是瑞数】
    #  6.
