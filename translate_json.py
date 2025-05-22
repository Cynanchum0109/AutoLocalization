import os
import json
from openai import OpenAI
import threading
from queue import Queue, Empty
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from check_missing_files import find_missing_files

# 读取API Key
with open('apikey.txt', 'r', encoding='utf-8') as f:
    client = OpenAI(api_key=f.read().strip())

# 读取术语表
with open('glossary.json', 'r', encoding='utf-8') as f:
    glossary = json.load(f)

# 创建翻译缓存字典
translation_cache = {}
# 创建线程锁来保护缓存访问
cache_lock = threading.Lock()

def get_similarity_ratio(str1, str2):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def find_similar_terms(text, glossary, threshold=0.8):
    """查找文本中与术语表相似的词"""
    similar_terms = {}
    
    # 将文本分割成单词
    words = text.split()
    
    for term, translation in glossary.items():
        # 检查完整术语
        if get_similarity_ratio(text, term) >= threshold:
            similar_terms[term] = translation
            continue
            
        # 检查术语中的每个单词
        term_words = term.split()
        for word in words:
            for term_word in term_words:
                if get_similarity_ratio(word, term_word) >= threshold:
                    similar_terms[term] = translation
                    break
    
    return similar_terms

def translate_text(text, field_type=None, context=None):
    # 对于teller、title、place、name和nickName，检查缓存
    if field_type in ["teller", "title", "place", "name", "nickName"]:
        with cache_lock:
            if text in translation_cache:
                return translation_cache[text]
            
    try:
        # 根据字段类型添加特定提示
        field_prompt = ""
        temperature = 0.5  # 默认使用较低的温度，保持标准翻译
        
        if field_type in ["teller", "name"]:
            field_prompt = "你要翻译的是说话者的名字或身份或描述，应当翻译成名词。"
        elif field_type in ["title", "nickName"]:
            field_prompt = "你要翻译的是说话者的职位或从属组织，应当简洁明了，保持职位或组织的格式。"
        elif field_type in ["content", "dlg"]:
            field_prompt = "你要翻译的是对话内容，应当保持对话的语气和风格。"
            temperature = 0.7
        elif field_type == "place":
            field_prompt = "你要翻译的是地点名称，应当翻译成合适的地名或场所名。"

        # 添加上下文提示
        context_prompt = ""
        if context and field_type in ["content", "dlg"]:
            context_prompt = "\n前文参考：\n" + "\n".join(context)

        # 查找相似术语
        similar_terms = find_similar_terms(text, glossary, threshold=0.8)
        
        # 构建消息
        messages = [
            {"role": "system", "content": "你是一个专业的中英翻译游戏剧情台词本地化助手。只需将英文翻译成中文，不要解释。"}
        ]
        
        # 只在找到相似术语时添加术语表
        if similar_terms:
            term_prompt = f"请参考以下术语进行翻译：\n{json.dumps(similar_terms, ensure_ascii=False, indent=None)}"
            messages.append({
                "role": "user", 
                "content": term_prompt
            })
        
        # 添加翻译请求
        messages.append({
            "role": "user", 
            "content": f"{field_prompt}{context_prompt}\n原文：{text}"
        })
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=temperature
        )
        translated = response.choices[0].message.content.strip()
        
        # 对于teller、title、place、name和nickName，保存到缓存
        if field_type in ["teller", "title", "place", "name", "nickName"]:
            with cache_lock:
                translation_cache[text] = translated
            
        return translated
    except Exception as e:
        print(f"\n翻译出错: {e}")
        print(f"错误文本: {text}")
        print(f"字段类型: {field_type}")
        print("程序终止")
        sys.exit(1)

def process_json_file(input_path, output_path, progress_queue):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "dataList" in data:
        # 用于存储前文的列表
        context_buffer = []
        
        # 计算需要翻译的文本总数
        total_texts = sum(1 for item in data["dataList"] 
                         for field in ["teller", "title", "content", "place", "dlg"]
                         if field in item and isinstance(item[field], str) 
                         and any('a' <= c.lower() <= 'z' for c in item[field]))
        
        current_text = 0
        
        for item in data["dataList"]:
            for field in ["teller", "title", "content", "place", "dlg"]:
                if field in item and isinstance(item[field], str):
                    # 检查是否包含英文字母
                    if any('a' <= c.lower() <= 'z' for c in item[field]):
                        current_text += 1
                        # 获取前文
                        current_context = context_buffer[-2:] if context_buffer else []
                        zh = translate_text(item[field], field, current_context)
                        item[field] = f"{zh}\n {item[field]}"
                        
                        # 如果是对话内容，添加到上下文缓冲区
                        if field in ["content", "dlg"]:
                            context_buffer.append(f"{item.get('teller', '')}: {item[field]}")
                        
                        # 更新进度
                        progress_queue.put(('progress', current_text, total_texts, os.path.basename(input_path)))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    progress_queue.put(('complete', input_path))

def worker(file_queue, progress_queue):
    while True:
        try:
            input_path, output_path = file_queue.get_nowait()
            process_json_file(input_path, output_path, progress_queue)
            file_queue.task_done()
        except Empty:
            break

def main():
    # 检查original目录是否为空
    original_dir = "Workplace/original"
    if not os.path.exists(original_dir) or not os.listdir(original_dir):
        print("Original目录为空，开始检查丢失文件...")
        
        # 定义目录路径
        zh_dir = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\StoryData"
        en_dir = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\StoryData"
        output_dir = "Workplace/translated/StoryData"
        os.makedirs(output_dir, exist_ok=True)

        # 获取缺失文件列表
        missing_files = find_missing_files(zh_dir, en_dir)

        if not missing_files:
            print("没有发现需要翻译的文件！")
            return

        print(f"\n发现 {len(missing_files)} 个需要翻译的文件")
        
        # 创建文件队列
        file_queue = Queue()
        progress_queue = Queue()
        
        # 将文件添加到队列
        for filename in sorted(missing_files):
            input_path = os.path.join(en_dir, f"EN_{filename}")
            output_path = os.path.join(output_dir, filename)
            file_queue.put((input_path, output_path))
        
        # 创建并启动工作线程
        num_threads = 1  # 固定1个线程
        completed_files = 0
        current_progress = 0
        total_texts = 0
        
        # 用于存储每个文件的进度
        file_progress = {}
        
        # 按批次处理文件
        while not file_queue.empty():
            # 创建新的一批线程
            current_threads = []
            for _ in range(num_threads):
                if file_queue.empty():
                    break
                t = threading.Thread(target=worker, args=(file_queue, progress_queue))
                t.start()
                current_threads.append(t)
            
            # 显示进度
            while len(current_threads) > 0:
                try:
                    msg_type, *args = progress_queue.get(timeout=1)
                    if msg_type == 'progress':
                        current_progress, total_texts, filename = args
                        file_progress[filename] = (current_progress, total_texts)
                        print(f"{filename}进度: {current_progress}/{total_texts}")
                    elif msg_type == 'complete':
                        completed_files += 1
                        print(f"\n完成文件 {completed_files}/{len(missing_files)}: {os.path.basename(args[0])}")
                        # 从当前线程列表中移除已完成的线程
                        for t in current_threads[:]:
                            if not t.is_alive():
                                current_threads.remove(t)
                except Empty:
                    continue
        
        print("\n所有文件翻译完成！")
    else:
        # 原有的处理逻辑
        input_dir = "Workplace/original"
        output_dir = "Workplace/translated"
        os.makedirs(output_dir, exist_ok=True)

        # 获取所有需要翻译的文件
        files_to_translate = [f for f in os.listdir(input_dir) if f.endswith(".json")]
        total_files = len(files_to_translate)
        
        # 创建文件队列
        file_queue = Queue()
        progress_queue = Queue()
        
        # 将文件添加到队列
        for filename in files_to_translate:
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace("EN_", "", 1)
            output_path = os.path.join(output_dir, output_filename)
            file_queue.put((input_path, output_path))
        
        # 创建并启动工作线程
        num_threads = 1  # 固定1个线程
        completed_files = 0
        current_progress = 0
        total_texts = 0
        
        # 用于存储每个文件的进度
        file_progress = {}
        
        # 按批次处理文件
        while not file_queue.empty():
            # 创建新的一批线程
            current_threads = []
            for _ in range(num_threads):
                if file_queue.empty():
                    break
                t = threading.Thread(target=worker, args=(file_queue, progress_queue))
                t.start()
                current_threads.append(t)
            
            # 显示进度
            while len(current_threads) > 0:
                try:
                    msg_type, *args = progress_queue.get(timeout=1)
                    if msg_type == 'progress':
                        current_progress, total_texts, filename = args
                        file_progress[filename] = (current_progress, total_texts)
                        print(f"{filename}进度: {current_progress}/{total_texts}")
                    elif msg_type == 'complete':
                        completed_files += 1
                        print(f"\n完成文件 {completed_files}/{total_files}: {os.path.basename(args[0])}")
                        # 从当前线程列表中移除已完成的线程
                        for t in current_threads[:]:
                            if not t.is_alive():
                                current_threads.remove(t)
                except Empty:
                    continue
        
        print("\n所有文件翻译完成！")

if __name__ == "__main__":
    main()
