import os
import json
from openai import OpenAI

# 读取API Key
with open('apikey.txt', 'r', encoding='utf-8') as f:
    client = OpenAI(api_key=f.read().strip())

# 读取Prompt
with open('prompt.txt', 'r', encoding='utf-8') as f:
    prompt = f.read().strip()

def translate_text(text):
    print(f"正在翻译: {text}")  # 调试信息
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        translated = response.choices[0].message.content.strip()
        print(f"翻译结果: {translated}")  # 调试信息
        return translated
    except Exception as e:
        print(f"翻译出错: {e}")  # 调试信息
        return text

def process_json_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "dataList" in data:
        for item in data["dataList"]:
            for field in ["teller", "title", "content", "place"]:
                if field in item and isinstance(item[field], str):
                    # 检查是否包含英文字母
                    if any('a' <= c.lower() <= 'z' for c in item[field]):
                        zh = translate_text(item[field])
                        item[field] = f"{item[field]} {zh}"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    input_dir = "Workplace/original"  # 输入路径
    output_dir = "Workplace/translated"  # 输出路径
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.replace("EN_", "", 1)  # 去掉EN_前缀
            output_path = os.path.join(output_dir, output_filename)
            process_json_file(input_path, output_path)
            print(f"已翻译并保存：{output_path}")

if __name__ == "__main__":
    main()
