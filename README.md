# 边狱公司文本翻译工具 | Limbus Company Text Translation Tool

这是一个用于翻译边狱公司（Limbus Company）游戏文本的自动化工具。该工具使用GPT-4模型进行翻译，支持术语表对照。

This is an automated tool for translating Limbus Company game texts. The tool uses GPT-4 model for translation and supports glossary reference.

## 功能特点 | Features

- 仅翻译人格剧情、人格语音、剧情。
- 仅支持英文翻译

- Only translates personality stories, personality voice lines, and story content.
- Only supports English to Chinese translation

## 环境要求 | Requirements

- Python 3.6+
- OpenAI API密钥 | OpenAI API Key
- 必要的Python包 | Required Python packages：
  - openai
  - json
  - os

## 安装步骤 | Installation

1. 克隆或下载本项目到本地 | Clone or download this project to local
2. 安装必要的Python包 | Install required Python packages：
   ```bash
   pip install openai
   ```
3. 在`apikey.txt`文件中填入OpenAI API密钥 | Fill in your OpenAI API key in `apikey.txt`
4. 确保`prompt.txt`和`glossary.json`文件存在 | Ensure `prompt.txt` and `glossary.json` files exist

## 使用方法 | Usage

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
5. 将对应的文件放进边狱公司游戏源文件的对应位置中。我自己一般是直接放在零协汉化底下，这样他们更新了可以直接覆盖我的机翻。

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
- `apikey.txt`: OpenAI API密钥文件 | OpenAI API key file
- `prompt.txt`: 翻译提示词文件 | Translation prompt file
- `glossary.json`: 术语对照表 | Glossary reference file
- `Workplace/original/`: 原始JSON文件目录 | Original JSON files directory
- `Workplace/translated/`: 翻译后文件目录 | Translated files directory

## 注意事项 | Notes

1. 请确保API密钥有效且有足够的额度 | Ensure the API key is valid and has sufficient quota
2. 翻译过程中请保持网络连接 | Maintain internet connection during translation
3. 建议定期更新备份术语表 | Regularly update and backup the glossary
4. 如遇到翻译错误，请检查API密钥和网络连接 | If translation errors occur, check the API key and internet connection

欢迎bilibili私聊白前Cynanchum，不作技术方面回答。

Feel free to contact 白前Cynanchum on bilibili, but no technical support will be provided.
