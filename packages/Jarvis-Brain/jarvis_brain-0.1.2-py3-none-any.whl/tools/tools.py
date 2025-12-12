import htmlmin
import requests
from lxml import html, etree
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions


# 使用requests获取html，用于测试是否使用了瑞数和jsl
def requests_html(url):
    headers = {
        # "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
        # "sec-ch-ua-mobile": "?0",
        # "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        # "Sec-Fetch-Site": "none",
        # "Sec-Fetch-Mode": "navigate",
        # "Sec-Fetch-User": "?1",
        # "Sec-Fetch-Dest": "document",
        # "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    response = requests.get(url, headers=headers, verify=False)
    print("response headers=> ", response.headers)
    return response.text, response.status_code


# 使用dp无头模式获取html，用于测试是否使用了其他waf，如移动waf
def dp_headless_html(url):
    opt = ChromiumOptions().headless(True)
    opt.set_argument('--no-sandbox')
    page = ChromiumPage(opt)
    page.get(url)
    page_html = page.html
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
    page_html = dp_headless_html(target_url)
    print("render_text=>", compress_html(page_html, only_text=True))
    print("\n")
    raw_html, status_code = requests_html(target_url)
    print("raw_html=>", status_code, compress_html(raw_html, only_text=True))
    print("\n")


if __name__ == '__main__':
    # raw_html, status_code = requests_html("https://www.nxzgh.org.cn/#/newsCenter/index2/2")
    # raw_html, status_code = requests_html("http://www.ncha.gov.cn/col/col722/index.html")
    # raw_html, status_code = requests_html("https://scgh.org/page/news/tmore36403294e28a11ea8ba48cec4b967595.html")
    # raw_html, status_code = requests_html("https://scgh.org/page/news/tmore36403294e28a11ea8ba48cec4b967595.html")
    # url = "https://www.nmpa.gov.cn/yaowen/ypjgyw/index.html"
    url = "http://www.customs.gov.cn/customs/xwfb34/302425/index.html"
    # url = "https://www.acftu.org/xwdt/ghyw/"

    for i in range(20):
        test(url)
