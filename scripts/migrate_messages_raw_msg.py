"""
数据迁移脚本：为 messages 表添加 raw_msg 字段
"""

import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ntchat_bot.settings import DATABASE_PATH


def migrate_messages_table():
    """为 messages 表添加 raw_msg 字段"""
    db_path = str(DATABASE_PATH)
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        print("无需迁移，新表会自动创建")
        return
    
    print(f"开始迁移数据库: {db_path}")
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前表字段: {columns}")
        
        # 如果不存在 raw_msg 字段则添加
        if 'raw_msg' not in columns:
            print("添加 raw_msg 字段...")
            cursor.execute("ALTER TABLE messages ADD COLUMN raw_msg TEXT")
            conn.commit()
            print("迁移完成！")
        else:
            print("raw_msg 字段已存在，无需迁移")
        
        # 验证结果
        cursor.execute("PRAGMA table_info(messages)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"迁移后表字段: {new_columns}")
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        print(f"消息总数: {count}")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    migrate_messages_table()