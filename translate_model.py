import json
import os
from translate_json import translate_text

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
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

def process_scenario_model_codes():
    """处理ScenarioModelCodes-AutoCreated.json文件"""
    # 文件路径
    en_file = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\EN_ScenarioModelCodes-AutoCreated.json"
    zh_file = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\ScenarioModelCodes-AutoCreated.json"
    output_dir = "Workplace/translated"
    output_file = os.path.join(output_dir, "ScenarioModelCodes-AutoCreated.json")

    # 加载文件
    en_data = load_json_file(en_file)
    zh_data = load_json_file(zh_file)

    if not en_data or not zh_data:
        print("无法加载ScenarioModelCodes文件，跳过处理")
        return

    # 获取现有ID列表和翻译缓存
    existing_ids = {item.get('id') for item in zh_data['dataList'] if item.get('id')}
    translation_cache = {}
    
    # 创建name和nickName的翻译缓存
    for item in zh_data['dataList']:
        if item.get('name'):
            translation_cache[item['name']] = item['name']
        if item.get('nickName'):
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
            print(f"正在翻译ScenarioModelCodes: {item['id']}")

    # 将新条目添加到中文文件
    if new_items:
        # 创建新的数据列表，包含原始中文数据和新翻译的数据
        combined_data = {
            'dataList': zh_data['dataList'] + new_items
        }
        save_json_file(output_file, combined_data)
        print(f"\nScenarioModelCodes成功添加 {len(new_items)} 个新条目")
        print(f"新文件已保存到: {output_file}")
        print("新增条目列表：")
        for item in new_items:
            print(f"ID: {item['id']}")
            print(f"名称: {item['name']}")
            print(f"昵称: {item['nickName']}")
            print("---")
    else:
        print("\nScenarioModelCodes没有发现需要翻译的新条目")
        # 即使没有新条目，也复制原始文件到输出目录
        save_json_file(output_file, zh_data)
        print(f"已复制原始ScenarioModelCodes文件到: {output_file}")

def process_battle_speech_bubble():
    """处理BattleSpeechBubbleDlg.json文件"""
    # 文件路径
    en_file = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\EN_BattleSpeechBubbleDlg.json"
    zh_file = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\BattleSpeechBubbleDlg.json"
    output_dir = "Workplace/translated"
    output_file = os.path.join(output_dir, "BattleSpeechBubbleDlg.json")

    # 加载文件
    en_data = load_json_file(en_file)
    zh_data = load_json_file(zh_file)

    if not en_data or not zh_data:
        print("无法加载BattleSpeechBubbleDlg文件，跳过处理")
        return

    # 获取现有ID列表和翻译缓存
    existing_ids = {item.get('id') for item in zh_data['dataList'] if item.get('id')}
    translation_cache = {}
    
    # 创建dlg的翻译缓存
    for item in zh_data['dataList']:
        if item.get('dlg'):
            translation_cache[item['dlg']] = item['dlg']
    
    # 需要翻译的新条目
    new_items = []
    for item in en_data['dataList']:
        if item['id'] not in existing_ids:
            # 处理dlg
            dlg = item['dlg']
            if dlg:
                if "??" in dlg:
                    dlg = dlg
                elif dlg in translation_cache:
                    dlg = translation_cache[dlg]
                else:
                    dlg = translate_text(dlg, 'dlg')
                    translation_cache[dlg] = dlg
            
            new_item = {
                'id': item['id'],
                'desc': item.get('desc', ''),
                'dlg': dlg if dlg else ""
            }
            new_items.append(new_item)
            print(f"正在翻译BattleSpeechBubbleDlg: {item['id']}")

    # 将新条目添加到中文文件
    if new_items:
        # 创建新的数据列表，包含原始中文数据和新翻译的数据
        combined_data = {
            'dataList': zh_data['dataList'] + new_items
        }
        save_json_file(output_file, combined_data)
        print(f"\nBattleSpeechBubbleDlg成功添加 {len(new_items)} 个新条目")
        print(f"新文件已保存到: {output_file}")
        print("新增条目列表：")
        for item in new_items:
            print(f"ID: {item['id']}")
            print(f"描述: {item['desc']}")
            print(f"对话: {item['dlg']}")
            print("---")
    else:
        print("\nBattleSpeechBubbleDlg没有发现需要翻译的新条目")
        # 即使没有新条目，也复制原始文件到输出目录
        save_json_file(output_file, zh_data)
        print(f"已复制原始BattleSpeechBubbleDlg文件到: {output_file}")

def main():
    print("开始处理翻译任务...")
    print("=" * 50)
    
    # 处理ScenarioModelCodes-AutoCreated.json文件
    print("1. 处理ScenarioModelCodes-AutoCreated.json文件")
    process_scenario_model_codes()
    
    print("\n" + "=" * 50)
    
    # 处理BattleSpeechBubbleDlg.json文件
    print("2. 处理BattleSpeechBubbleDlg.json文件")
    process_battle_speech_bubble()
    
    print("\n" + "=" * 50)
    print("所有翻译任务完成！")

if __name__ == "__main__":
    main() 