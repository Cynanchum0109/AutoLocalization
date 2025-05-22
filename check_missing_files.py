import os

def get_files_in_directory(directory):
    """获取指定目录中的所有文件"""
    try:
        return set(os.listdir(directory))
    except Exception as e:
        print(f"读取目录 {directory} 时出错: {str(e)}")
        return set()

def find_missing_files(zh_dir, en_dir):
    """查找缺失的文件
    
    Args:
        zh_dir (str): 中文文件目录路径
        en_dir (str): 英文文件目录路径
        
    Returns:
        set: 缺失的文件名集合
    """
    # 获取两个目录中的文件列表
    zh_files = get_files_in_directory(zh_dir)
    en_files = get_files_in_directory(en_dir)

    # 创建英文文件名对应的中文文件名集合（去掉EN_前缀）
    expected_zh_files = {f[3:] for f in en_files if f.startswith('EN_')}

    # 找出缺失的文件
    missing_files = expected_zh_files - zh_files
    
    return missing_files

def main():
    # 定义两个目录路径
    zh_dir = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\StoryData"
    en_dir = r"D:\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\StoryData"

    # 获取缺失文件列表
    missing_files = find_missing_files(zh_dir, en_dir)

    # 输出结果
    if missing_files:
        print("\n以下文件在中文目录中缺失：")
        for file in sorted(missing_files):
            print(f"- {file}")
        print(f"\n总共缺失 {len(missing_files)} 个文件")
    else:
        print("\n没有发现缺失的文件！")

if __name__ == "__main__":
    main() 