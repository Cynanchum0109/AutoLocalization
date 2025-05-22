# 边狱公司文本翻译工具 | Limbus Company Text Translation Tool

这是一个用于翻译边狱公司（Limbus Company）游戏文本的自动化工具。该工具使用GPT-4模型进行翻译，支持术语表对照。

This is an automated tool for translating Limbus Company game texts. The tool uses GPT-4 model for translation and supports glossary reference.

## 功能特点 | Features

- 仅翻译人格剧情、人格语音、剧情。
- 仅支持英文翻译
- 支持自动检测缺失文件并翻译
- 支持翻译缓存，避免重复翻译相同内容
- 支持术语表对照，保持翻译一致性

- Only translates personality stories, personality voice lines, and story content.
- Only supports English to Chinese translation
- Supports automatic detection and translation of missing files
- Supports translation cache to avoid duplicate translations
- Supports glossary reference for consistent translation

## 环境要求 | Requirements

- Python 3.6+
- OpenAI API密钥 | OpenAI API Key
- 必要的Python包 | Required Python packages：
  - openai
  - json
  - os
  - threading
  - queue
  - difflib

## 安装步骤 | Installation

1. 克隆或下载本项目到本地 | Clone or download this project to local
2. 安装必要的Python包 | Install required Python packages：
   ```bash
   pip install openai
   ```
3. 新建`apikey.txt`文件，在`apikey.txt`文件中填入OpenAI API密钥 | Create an `apikey.txt` file and fill in your OpenAI API key.
4. 确保`glossary.json`文件存在（当前不在远程仓库中） | Ensure the `glossary.json` file exists (it is currently not included in the remote repository)

## 使用方法 | Usage

### 方法一：直接翻译指定文件 | Method 1: Direct Translation

1. 在边狱公司源文件找到需要翻译的英文文本，一般以"EN_"为前缀。仅限StoryData与PersonalityVoiceDlg文件夹中的文本内容。

   Find the English texts to be translated in the Limbus Company source files, usually prefixed with "EN_". Limited to text content in StoryData and PersonalityVoiceDlg folders.

   目录 | Directory：
   ```
   Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\StoryData
   Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\PersonalityVoiceDlg
   ```

2. 将需要翻译的JSON文件放入`Workplace/original`目录 | Put the JSON files to be translated in the `Workplace/original` directory
3. 运行翻译脚本 | Run the translation script：
   ```bash
   python translate_json.py
   ```
4. 翻译后的文件将保存在`Workplace/translated`目录中 | Translated files will be saved in the `Workplace/translated` directory

### 方法二：自动检测并翻译缺失文件 | Method 2: Auto-detect and Translate Missing Files

1. 确保`Workplace/original`目录为空 | Ensure the `Workplace/original` directory is empty
2. 运行翻译脚本 | Run the translation script：
   ```bash
   python translate_json.py
   ```
3. 脚本会自动：
   - 检测中文StoryData目录中缺失的文件
   - 翻译缺失的文件
   - 将翻译后的文件保存到`Workplace/translated/StoryData`目录

   The script will automatically:
   - Detect missing files in StoryData in the Chinese directory
   - Translate missing files
   - Save translated files to `Workplace/translated/StoryData` directory

### 文件放置 | File Placement

将对应的文件放进边狱公司游戏源文件的对应位置中。我自己一般是直接放在零协汉化底下，这样他们更新了可以直接覆盖我的机翻。

Put the corresponding files in the appropriate location in the Limbus Company game source files. I usually put them directly under the LLC translation folder, so they can be overwritten when they update.

目录 | Directory：
```
Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\PersonalityVoiceDlg
Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\StoryData
```

6. 我在Workplace/original里放了两个例子，可以作为测试用。到时候自己用的时候别拖错了。

   I've included two examples in Workplace/original for testing. Make sure not to drag the wrong files when using it yourself.

## 文件说明 | File Description

- `translate_json.py`: 主程序文件 | Main program file
- `check_missing_files.py`: 缺失文件检测工具 | Missing files detection tool
- `apikey.txt`: OpenAI API密钥文件 | OpenAI API key file
- `glossary.json`: 术语对照表 | Glossary reference file
- `Workplace/original/`: 原始JSON文件目录 | Original JSON files directory
- `Workplace/translated/`: 翻译后文件目录 | Translated files directory

## 注意事项 | Notes

1. 请确保API密钥有效且有足够的额度 | Ensure the API key is valid and has sufficient quota
2. 翻译过程中请保持网络连接 | Maintain internet connection during translation
3. 建议定期更新备份术语表 | Regularly update and backup the glossary
4. 如遇到翻译错误，请检查API密钥和网络连接 | If translation errors occur, check the API key and internet connection
5. 翻译缓存会保存在内存中，程序结束后会清除 | Translation cache is stored in memory and will be cleared after the program ends
6. 自动检测功能仅支持StoryData目录 | Auto-detection feature only supports StoryData directory

欢迎bilibili私聊白前Cynanchum，不作技术方面回答。

Feel free to contact 白前Cynanchum on bilibili, but no technical support will be provided.
