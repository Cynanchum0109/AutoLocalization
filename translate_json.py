import os
import json
from openai import OpenAI

# 读取API Key
with open('apikey.txt', 'r', encoding='utf-8') as f:
    client = OpenAI(api_key=f.read().strip())

# 读取Prompt
with open('prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read().strip()

# 创建翻译缓存字典
translation_cache = {}

def translate_text(text, field_type=None):
    print(f"正在翻译: {text}")  # 调试信息
    
    # 对于teller、title和place，检查缓存
    if field_type in ["teller", "title", "place"]:
        if text in translation_cache:
            return translation_cache[text]
    
    try:
        # 根据字段类型添加特定提示
        field_prompt = ""
        temperature = 0.5  # 默认使用较低的温度，保持标准翻译
        
        if field_type == "teller":
            field_prompt = "你要翻译的是说话者的名字或身份或描述，应当翻译成名词。"
        elif field_type == "title":
            field_prompt = "你要翻译的是说话者的职位名称，应当简洁明了，保持职位名称的格式。"
        elif field_type in ["content", "dlg"]:  # dlg和content使用相同的策略
            field_prompt = "你要翻译的是对话内容，应当保持对话的语气和风格。"
            temperature = 0.7  # 对话内容使用较高的温度，允许更灵活的翻译
        elif field_type == "place":
            field_prompt = "你要翻译的是地点名称，应当翻译成合适的地名或场所名。"

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"{field_prompt}\n原文：{text}"}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=temperature
        )
        translated = response.choices[0].message.content.strip()
        print(f"翻译结果: {translated}")  # 调试信息
        
        # 对于teller、title和place，保存到缓存
        if field_type in ["teller", "title", "place"]:
            translation_cache[text] = translated
            
        return translated
    except Exception as e:
        print(f"翻译出错: {e}")  # 调试信息
        return text

def process_json_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "dataList" in data:
        for item in data["dataList"]:
            for field in ["teller", "title", "content", "place", "dlg"]:  # 添加dlg字段
                if field in item and isinstance(item[field], str):
                    # 检查是否包含英文字母
                    if any('a' <= c.lower() <= 'z' for c in item[field]):
                        zh = translate_text(item[field], field)
                        item[field] = f"{item[field]} {zh}"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    input_dir = "Workplace/original"  # 输入路径
    output_dir = "Workplace/translated"  # 输出路径
    os.makedirs(output_dir, exist_ok=True)

    # 获取所有需要翻译的文件
    files_to_translate = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    total_files = len(files_to_translate)
    
    for index, filename in enumerate(files_to_translate, 1):
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace("EN_", "", 1)  # 去掉EN_前缀
        output_path = os.path.join(output_dir, output_filename)
        process_json_file(input_path, output_path)
        print(f"已翻译文档 {index}/{total_files}")

if __name__ == "__main__":
    main()
