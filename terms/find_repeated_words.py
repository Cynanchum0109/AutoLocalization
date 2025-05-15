import re
import os

# 修改文件路径，确保正确读取terms.md
with open(os.path.join(os.path.dirname(__file__), 'terms.md'), 'r', encoding='utf-8') as file:
    content = file.read()

# 提取所有英文单词
words = re.findall(r'\b[a-zA-Z]+\b', content)

# 统计每个单词出现的次数
word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

# 输出重复的单词
for word, count in word_count.items():
    if count > 1:
        print(f"{word}: {count}")