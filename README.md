# 边狱公司文本翻译工具

这是一个用于翻译边狱公司（Limbus Company）游戏文本的自动化工具。该工具使用GPT-4模型进行翻译，支持术语表对照。

## 功能特点

- 仅翻译人格剧情、人格语音、剧情。
- 仅支持英文翻译

## 环境要求

- Python 3.6+
- OpenAI API密钥
- 必要的Python包：
  - openai
  - json
  - os

## 安装步骤

1. 克隆或下载本项目到本地
2. 安装必要的Python包：
   ```bash
   pip install openai
   ```
3. 在`apikey.txt`文件中填入OpenAI API密钥
4. 确保`prompt.txt`和`glossary.json`文件存在

## 使用方法

1. 在边狱公司源文件找到需要翻译的英文文本，一般以"EN_"为前缀。仅限StoryData与PersonalityVoiceDlg文件夹中的文本内容。

   目录：
   ```
   Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\StoryData
   Limbus Company\LimbusCompany_Data\Assets\Resources_moved\Localize\en\PersonalityVoiceDlg
   ```

2. 将需要翻译的JSON文件放入`Workplace/original`目录
3. 运行翻译脚本：
   ```bash
   python translate_json.py
   ```
4. 翻译后的文件将保存在`Workplace/translated`目录中
5. 将对应的文件放进边狱公司游戏源文件的对应位置中。我自己一般是直接放在零协汉化底下，这样他们更新了可以直接覆盖我的机翻。

   目录：
   ```
   Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\PersonalityVoiceDlg
   Limbus Company\LimbusCompany_Data\Lang\LLC_zh-CN\StoryData
   ```

6. 我在Workplace/original里放了两个例子，可以作为测试用。到时候自己用的时候别拖错了。

## 文件说明

- `translate_json.py`: 主程序文件
- `apikey.txt`: OpenAI API密钥文件
- `prompt.txt`: 翻译提示词文件
- `glossary.json`: 术语对照表
- `Workplace/original/`: 原始JSON文件目录
- `Workplace/translated/`: 翻译后文件目录

## 注意事项

1. 请确保API密钥有效且有足够的额度
2. 翻译过程中请保持网络连接
3. 建议定期更新备份术语表
4. 如遇到翻译错误，请检查API密钥和网络连接

欢迎bilibili私聊白前Cynanchum，不作技术方面回答。
