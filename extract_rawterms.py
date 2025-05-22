import json
import os

class TermExtractor:
    def __init__(self):
        self.terms = {}  # 直接使用键值对存储 {英文: 中文}

    def process_text(self, text: str, translation: str = None):
        """处理文本，跳过重复条目"""
        if text in self.terms:
            if translation and not self.terms[text]:
                self.terms[text] = translation
                print(f"更新翻译: {text} -> {translation}")
            return
        
        self.terms[text] = translation
        print(f"添加新术语: {text}")

    def process_file_pair(self, en_path: str, cn_path: str):
        """处理对应的中英文文件对"""
        print(f"\n处理文件对: {os.path.basename(en_path)} -> {os.path.basename(cn_path)}")
        
        # 读取英文文件
        try:
            with open(en_path, 'r', encoding='utf-8') as f:
                en_data = json.load(f)
        except Exception as e:
            print(f"处理英文文件时出错: {str(e)}")
            return

        # 读取中文文件
        try:
            with open(cn_path, 'r', encoding='utf-8') as f:
                cn_data = json.load(f)
        except Exception as e:
            print(f"处理中文文件时出错: {str(e)}")
            return

        # 创建ID到中文内容的映射
        cn_map = {}
        if "dataList" in cn_data:
            for item in cn_data["dataList"]:
                if "id" not in item:
                    continue
                cn_map[item["id"]] = item

        # 处理英文文件，匹配中文翻译
        if "dataList" in en_data:
            for item in en_data["dataList"]:
                if "id" not in item:
                    continue
                
                # 获取对应的中文内容
                cn_item = cn_map.get(item["id"], {})
                
                # 处理角色名称、职位和地点
                for field in ["teller", "title", "place"]:
                    if field in item and isinstance(item[field], str):
                        if any('a' <= c.lower() <= 'z' for c in item[field]):
                            translation = cn_item.get(field, "")
                            self.process_text(item[field], translation)

    def save_terms(self):
        """保存提取的术语到新文件"""
        print("\n保存提取的术语...")
        
        # 保存到新文件
        with open('new_glossary.json', 'w', encoding='utf-8') as f:
            json.dump(self.terms, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(self.terms)} 个术语到 new_glossary.json")

def main():
    # 设置输入路径
    en_dir = "Originaltext/EN"
    cn_dir = "Originaltext/CN"
    
    # 创建提取器实例
    extractor = TermExtractor()
    
    # 处理所有文件
    print(f"\n开始处理文件...")
    
    # 获取所有英文文件名
    en_files = [f for f in os.listdir(en_dir) if f.endswith('.json')]
    
    for en_filename in en_files:
        # 构建对应的中文文件名
        cn_filename = en_filename.replace("EN_", "", 1)
        en_path = os.path.join(en_dir, en_filename)
        cn_path = os.path.join(cn_dir, cn_filename)
        
        if os.path.exists(cn_path):
            extractor.process_file_pair(en_path, cn_path)
        else:
            print(f"跳过: 找不到对应的中文文件 {cn_filename}")
    
    # 保存提取的术语
    extractor.save_terms()

if __name__ == "__main__":
    main() 