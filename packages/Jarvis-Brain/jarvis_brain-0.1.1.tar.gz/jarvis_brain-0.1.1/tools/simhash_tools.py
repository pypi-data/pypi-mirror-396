import re
from bs4 import BeautifulSoup
from simhash import Simhash, SimhashIndex
import jieba
import hashlib
from tools.tools import compress_html


class HTMLSimHashComparator:
    def __init__(self, html1, html2, is_file=False):
        """
        初始化比较器

        Args:
            html1: 第一个HTML内容或文件路径
            html2: 第二个HTML内容或文件路径
            is_file: 是否为文件路径（True则为文件路径，False则为HTML字符串）
        """
        if is_file:
            with open(html1, 'r', encoding='utf-8') as f1:
                self.html1 = f1.read()
            with open(html2, 'r', encoding='utf-8') as f2:
                self.html2 = f2.read()
        else:
            self.html1 = html1
            self.html2 = html2

    def clean_html(self, html_content):
        text = compress_html(html_content, only_text=True)
        return text

    def extract_features(self, text):
        """从文本中提取特征"""
        # 使用jieba进行中文分词（如果是中文内容）
        # 如果是英文，可以使用空格分词或其他方式
        words = jieba.lcut(text)

        # 过滤停用词和短词
        stop_words = set(['的', '了', '在', '是', '我', '有', '和', '就',
                          '不', '人', '都', '一', '一个', '上', '也', '很',
                          '到', '说', '要', '去', '你', '会', '着', '没有',
                          '看', '好', '自己', '这'])

        features = []
        for word in words:
            # 过滤停用词和长度小于2的词
            if word not in stop_words and len(word) >= 2:
                features.append(word)

        return features

    def calculate_simhash(self, html_content):
        """计算HTML内容的SimHash值"""
        # 清洗HTML
        text = self.clean_html(html_content)

        # 提取特征
        features = self.extract_features(text)

        # 计算SimHash（默认使用64位）
        simhash = Simhash(features, f=64)

        return simhash

    def compare_simhash(self):
        """比较两个HTML的SimHash值"""
        # 计算SimHash值
        simhash1 = self.calculate_simhash(self.html1)
        simhash2 = self.calculate_simhash(self.html2)

        # 计算汉明距离
        hamming_distance = simhash1.distance(simhash2)

        # 计算相似度（0-1之间）
        # 64位SimHash的最大汉明距离是64
        similarity = 1 - (hamming_distance / 64)

        return {
            'simhash1': bin(simhash1.value),
            'simhash2': bin(simhash2.value),
            'hamming_distance': hamming_distance,
            'similarity': similarity,
            'similarity_percentage': f"{similarity * 100:.2f}%"
        }

    def compare_with_threshold(self, threshold=0.8):
        """基于阈值判断是否相似"""
        result = self.compare_simhash()
        is_similar = result['similarity'] >= threshold

        return {
            **result,
            'threshold': threshold,
            'is_similar': is_similar
        }


# 3. 使用示例
def main():
    # 示例1：直接传入HTML字符串
    html1 = """
    <html>
        <head><title>测试页面1</title></head>
        <body>
            <h1>欢迎来到我的网站</h1>
            <p>这是一个测试页面，用于演示SimHash比较。</p>
            <p>Python是一种流行的编程语言。</p>
        </body>
    </html>
    """

    html2 = """
    <html>
        <head><title>测试页面2</title></head>
        <body>
            <h1>欢迎访问我的网站</h1>
            <p>这是一个测试页面，用于展示SimHash比较功能。</p>
            <p>Python编程语言非常流行。</p>
        </body>
    </html>
    """

    # 创建比较器并比较
    comparator = HTMLSimHashComparator(html1, html2)
    result = comparator.compare_simhash()

    print("SimHash比较结果:")
    print(f"页面1 SimHash: {result['simhash1']}")
    print(f"页面2 SimHash: {result['simhash2']}")
    print(f"汉明距离: {result['hamming_distance']}")
    print(f"相似度: {result['similarity_percentage']}")

    # 基于阈值判断
    threshold_result = comparator.compare_with_threshold(threshold=0.7)
    print(f"\n基于阈值{threshold_result['threshold']}的判断:")
    print(f"是否相似: {threshold_result['is_similar']}")


# 4. 高级功能：批量比较和聚类
class BatchHTMLComparator:
    def __init__(self):
        self.documents = []
        self.simhashes = []

    def add_document(self, doc_id, html_content):
        """添加文档到比较器"""
        comparator = HTMLSimHashComparator(html_content, html_content)
        simhash = comparator.calculate_simhash(html_content)

        self.documents.append({
            'id': doc_id,
            'content': html_content,
            'simhash': simhash
        })
        self.simhashes.append((doc_id, simhash))

    def find_duplicates(self, k=3):
        """查找相似的文档（k为汉明距离阈值）"""
        index = SimhashIndex(self.simhashes, k=k)

        duplicates = []
        for doc_id, simhash in self.simhashes:
            # 查找相似文档
            similar_ids = index.get_near_dups(simhash)
            if len(similar_ids) > 1:
                duplicates.append({
                    'doc_id': doc_id,
                    'similar_docs': similar_ids
                })

        return duplicates

    def compare_all_pairs(self):
        """比较所有文档对"""
        comparisons = []
        n = len(self.documents)

        for i in range(n):
            for j in range(i + 1, n):
                comparator = HTMLSimHashComparator(
                    self.documents[i]['content'],
                    self.documents[j]['content']
                )
                result = comparator.compare_simhash()

                comparisons.append({
                    'doc1': self.documents[i]['id'],
                    'doc2': self.documents[j]['id'],
                    'hamming_distance': result['hamming_distance'],
                    'similarity': result['similarity']
                })

        return sorted(comparisons, key=lambda x: x['similarity'], reverse=True)


if __name__ == "__main__":
    # 运行示例
    main()

    # 批量比较示例
    print("\n=== 批量比较示例 ===")
    batch_comparator = BatchHTMLComparator()

    # 添加多个文档
    batch_comparator.add_document("doc1", """
        <html><body><h1>Python编程</h1><p>学习Python很有趣。</p></body></html>
    """)

    batch_comparator.add_document("doc2", """
        <html><body><h1>Python代码</h1><p>编写Python代码很有趣。</p></body></html>
    """)

    batch_comparator.add_document("doc3", """
        <html><body><h1>Java编程</h1><p>Java是一种编程语言。</p></body></html>
    """)

    # 查找重复文档
    duplicates = batch_comparator.find_duplicates(k=3)
    print("相似的文档:")
    for dup in duplicates:
        print(f"文档 {dup['doc_id']} 与 {dup['similar_docs']} 相似")

    # 比较所有文档对
    all_comparisons = batch_comparator.compare_all_pairs()
    print("\n所有文档对比较:")
    for comp in all_comparisons:
        print(f"{comp['doc1']} vs {comp['doc2']}: "
              f"相似度 {comp['similarity']:.2%}")
