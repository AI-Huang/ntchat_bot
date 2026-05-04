"""
将转发消息日志转换为JSON格式

使用方法:
python -m scripts.convert_log_to_json <log_path> <output_path>

示例:
python -m scripts.convert_log_to_json logs/转发消息.log logs/转发消息.json
"""

import argparse
import json
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def parse_log_line(line):
    """解析单行日志，提取消息数据"""
    match = re.search(r'on recv message: (.+)', line)
    if not match:
        return None
    
    msg_str = match.group(1)
    msg_str = msg_str.rstrip('...')
    
    try:
        import ast
        data = ast.literal_eval(msg_str)
        return data
    except Exception as e:
        print(f"解析失败: {e}")
        return None


def convert_to_json(log_path, output_path):
    """将日志文件转换为JSON文件"""
    if not os.path.exists(log_path):
        print(f"错误: 日志文件不存在: {log_path}")
        return
    
    print(f"正在解析日志文件: {log_path}")
    
    messages = []
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        for line in lines:
            if 'on recv message:' in line:
                data = parse_log_line(line)
                if data:
                    messages.append(data)
    
    if not messages:
        print("未找到任何消息")
        return
    
    print(f"找到 {len(messages)} 条消息")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    
    print(f"JSON文件已保存: {output_path}")
    
    return messages


def main():
    parser = argparse.ArgumentParser(description='将日志文件转换为JSON格式')
    parser.add_argument('log_path', help='输入日志文件路径')
    parser.add_argument('output_path', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    convert_to_json(args.log_path, args.output_path)


if __name__ == '__main__':
    main()