import json
import os
from translate_json import translate_text

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None

def save_json_file(file_path, data):
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存文件 {file_path} 时出错: {e}")

def main():
    # 文件路径
    en_file = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\EN_ScenarioModelCodes-AutoCreated.json"
    zh_file = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\ScenarioModelCodes-AutoCreated.json"
    output_dir = "Workplace/translated"
    output_file = os.path.join(output_dir, "ScenarioModelCodes-AutoCreated.json")

    # 加载文件
    en_data = load_json_file(en_file)
    zh_data = load_json_file(zh_file)

    if not en_data or not zh_data:
        print("无法加载文件，程序终止")
        return

    # 获取现有ID列表和翻译缓存
    existing_ids = {item['id'] for item in zh_data['dataList']}
    translation_cache = {}
    
    # 创建name和nickName的翻译缓存
    for item in zh_data['dataList']:
        if item['name']:
            translation_cache[item['name']] = item['name']
        if item['nickName']:
            translation_cache[item['nickName']] = item['nickName']
    
    # 需要翻译的新条目
    new_items = []
    for item in en_data['dataList']:
        if item['id'] not in existing_ids:
            # 处理name
            name = item['name']
            if name:
                if "??" in name:
                    name = name
                elif name in translation_cache:
                    name = translation_cache[name]
                else:
                    name = translate_text(name, 'name')
                    translation_cache[name] = name
            
            # 处理nickName
            nickName = item['nickName']
            if nickName:
                if "??" in nickName:
                    nickName = nickName
                elif nickName in translation_cache:
                    nickName = translation_cache[nickName]
                else:
                    nickName = translate_text(nickName, 'nickName')
                    translation_cache[nickName] = nickName
            
            new_item = {
                'id': item['id'],
                'name': name if name else "",
                'nickName': nickName if nickName else ""
            }
            new_items.append(new_item)
            print(f"正在翻译: {item['id']}")

    # 将新条目添加到中文文件
    if new_items:
        # 创建新的数据列表，包含原始中文数据和新翻译的数据
        combined_data = {
            'dataList': zh_data['dataList'] + new_items
        }
        save_json_file(output_file, combined_data)
        print(f"\n成功添加 {len(new_items)} 个新条目")
        print(f"新文件已保存到: {output_file}")
        print("新增条目列表：")
        for item in new_items:
            print(f"ID: {item['id']}")
            print(f"名称: {item['name']}")
            print(f"昵称: {item['nickName']}")
            print("---")
    else:
        print("\n没有发现需要翻译的新条目")
        # 即使没有新条目，也复制原始文件到输出目录
        save_json_file(output_file, zh_data)
        print(f"已复制原始文件到: {output_file}")

if __name__ == "__main__":
    main() 