"""
数据迁移脚本：重新排列 messages 表字段，将 timestamp 移到 create_time 之前
"""

import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ntchat_bot.settings import DATABASE_PATH


def reorder_messages_table():
    """重新排列 messages 表字段顺序"""
    db_path = str(DATABASE_PATH)
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"开始重新排列表字段: {db_path}")
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(messages)")
        columns = [(col[1], col[2]) for col in cursor.fetchall()]
        print("当前字段顺序:")
        for col_name, col_type in columns:
            print(f"  {col_name} {col_type}")
        
        # 创建临时表，使用正确的字段顺序
        print("\n创建临时表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id TEXT UNIQUE,
                from_wxid TEXT,
                to_wxid TEXT,
                room_wxid TEXT,
                content TEXT,
                wx_type INTEGER,
                is_group INTEGER DEFAULT 0,
                timestamp INTEGER,
                create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                extra TEXT
            )
        ''')
        
        # 复制数据到临时表
        print("复制数据到临时表...")
        cursor.execute('''
            INSERT INTO messages_new 
            (id, msg_id, from_wxid, to_wxid, room_wxid, content, wx_type, is_group, timestamp, create_time, extra)
            SELECT 
                id, 
                msg_id, 
                from_wxid, 
                to_wxid, 
                room_wxid, 
                content, 
                wx_type, 
                COALESCE(is_group, 0),
                COALESCE(timestamp, 0),
                COALESCE(create_time, ''),
                extra
            FROM messages
        ''')
        
        # 删除旧表
        print("删除旧表...")
        cursor.execute("DROP TABLE messages")
        
        # 重命名临时表
        print("重命名临时表...")
        cursor.execute("ALTER TABLE messages_new RENAME TO messages")
        
        conn.commit()
        print("\n迁移完成！")
        
        # 验证结果
        cursor.execute("PRAGMA table_info(messages)")
        new_columns = [(col[1], col[2]) for col in cursor.fetchall()]
        print("\n新字段顺序:")
        for i, (col_name, col_type) in enumerate(new_columns, 1):
            print(f"  {i}. {col_name} {col_type}")
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        print(f"\n消息总数: {count}")
        
    except Exception as e:
        print(f"\n迁移失败: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    reorder_messages_table()