"""
数据迁移脚本：重新排列 contacts 表字段顺序

使用方法：
python -m scripts.reorder_contacts
"""

import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ntchat_bot.settings import DATABASE_PATH


def reorder_contacts_table():
    """重新排列 contacts 表字段顺序"""
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
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [(col[1], col[2]) for col in cursor.fetchall()]
        print(f"当前字段顺序:")
        for col_name, col_type in columns:
            print(f"  {col_name} {col_type}")
        
        # 创建临时表，使用正确的字段顺序
        print("\n创建临时表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts_new (
                wxid TEXT PRIMARY KEY,
                account TEXT,
                nickname TEXT,
                remark TEXT,
                avatar TEXT,
                city TEXT,
                province TEXT,
                country TEXT,
                sex INTEGER,
                create_time TEXT,
                update_time TEXT
            )
        ''')
        
        # 复制数据到临时表
        print("复制数据到临时表...")
        cursor.execute('''
            INSERT INTO contacts_new 
            (wxid, account, nickname, remark, avatar, city, province, country, sex, create_time, update_time)
            SELECT 
                wxid, 
                COALESCE(account, ''),
                COALESCE(nickname, ''),
                COALESCE(remark, ''),
                COALESCE(avatar, ''),
                COALESCE(city, ''),
                COALESCE(province, ''),
                COALESCE(country, ''),
                COALESCE(sex, 0),
                COALESCE(create_time, ''),
                COALESCE(update_time, '')
            FROM contacts
        ''')
        
        # 删除旧表
        print("删除旧表...")
        cursor.execute("DROP TABLE contacts")
        
        # 重命名临时表
        print("重命名临时表...")
        cursor.execute("ALTER TABLE contacts_new RENAME TO contacts")
        
        conn.commit()
        print("\n迁移完成！")
        
        # 验证结果
        cursor.execute("PRAGMA table_info(contacts)")
        new_columns = [(col[1], col[2]) for col in cursor.fetchall()]
        print("\n新字段顺序:")
        for i, (col_name, col_type) in enumerate(new_columns, 1):
            print(f"  {i}. {col_name} {col_type}")
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM contacts")
        count = cursor.fetchone()[0]
        print(f"\n联系人总数: {count}")
        
    except Exception as e:
        print(f"\n迁移失败: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    reorder_contacts_table()