#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说翻译脚本
使用OpenAI API将英文小说翻译成中文，保持文学性和准确性
"""

import openai
import json
import re
import os
from typing import List, Tuple

def load_api_key(file_path: str) -> str:
    """从文件加载API密钥"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"错误：找不到API密钥文件 {file_path}")
        return ""

def read_novel_file(file_path: str) -> str:
    """读取小说文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return ""

def split_into_paragraphs(text: str) -> List[str]:
    """将文本分割成段落"""
    # 按双换行符分割段落，但保留空行作为段落分隔符
    lines = text.split('\n')
    paragraphs = []
    current_para = []
    
    for line in lines:
        if line.strip() == "":
            if current_para:
                paragraphs.append('\n'.join(current_para))
                current_para = []
            paragraphs.append("")  # 保留空段落
        else:
            current_para.append(line)
    
    if current_para:
        paragraphs.append('\n'.join(current_para))
    
    return paragraphs

def create_translation_prompt(original_text: str) -> str:
    """创建翻译提示词"""
    prompt = f"""
请将以下英文小说翻译成中文。翻译要求：

1. 保持原文的文学性和情感表达
2. 确保翻译准确，忠实于原文
3. 使用流畅自然的中文表达
4. 保持原文的段落结构
5. 重要术语翻译：
   - Heathcliff → 希斯克利夫
   - Hong Lu → 鸿璐
   - Full-stop office → 句点事务所
   - Sinclair → 辛克莱

请直接输出中文翻译，不要添加任何解释或注释：

{original_text}
"""
    return prompt

def translate_with_openai(text: str, api_key: str) -> str:
    """使用OpenAI API进行翻译"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一位专业的文学翻译家，擅长将英文小说翻译成流畅自然的中文，保持原文的文学性和情感表达。"
                },
                {
                    "role": "user", 
                    "content": create_translation_prompt(text)
                }
            ],
            max_tokens=4000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"翻译过程中出现错误：{e}")
        return ""

def merge_translations(original_paragraphs: List[str], translation: str) -> str:
    """将翻译结果与原文本合并"""
    # 将翻译文本也分割成段落
    translated_paragraphs = split_into_paragraphs(translation)
    
    result_lines = []
    
    for i, original_para in enumerate(original_paragraphs):
        # 添加原文段落
        if original_para.strip():  # 只处理非空段落
            result_lines.append(original_para)
            
            # 添加对应的中文翻译（如果存在）
            if i < len(translated_paragraphs) and translated_paragraphs[i].strip():
                result_lines.append("")
                result_lines.append(translated_paragraphs[i])
            
            # 段落之间添加空行
            result_lines.append("")
        else:
            # 保留空段落
            result_lines.append("")
    
    return '\n'.join(result_lines)

def main():
    """主函数"""
    # 文件路径
    novel_file = "句点67.txt"
    api_key_file = "apikey.txt"
    output_file = "句点67_翻译.txt"
    pure_output_file = "句点67_纯中文.txt"
    
    print("开始翻译小说...")
    
    # 加载API密钥
    api_key = load_api_key(api_key_file)
    if not api_key:
        return
    
    # 读取原文
    original_text = read_novel_file(novel_file)
    if not original_text:
        return
    
    print("原文读取完成，开始翻译...")
    
    # 分割段落
    paragraphs = split_into_paragraphs(original_text)
    print(f"共分割出 {len(paragraphs)} 个段落")
    
    # 进行翻译
    translation = translate_with_openai(original_text, api_key)
    if not translation:
        print("翻译失败")
        return
    
    # 先输出纯中文译文
    try:
        with open(pure_output_file, 'w', encoding='utf-8') as f:
            f.write(translation)
        print(f"纯中文译文已保存到 {pure_output_file}")
    except Exception as e:
        print(f"保存纯中文译文时出现错误：{e}")

    print("翻译完成，正在合并结果...")
    
    # 合并翻译结果
    merged_result = merge_translations(paragraphs, translation)
    
    # 保存结果
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_result)
        print(f"翻译完成！结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存文件时出现错误：{e}")

if __name__ == "__main__":
    main()
