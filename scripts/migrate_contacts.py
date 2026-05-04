"""
数据迁移脚本：为 contacts 表添加缺失字段并填充默认值

使用方法：
python -m scripts.migrate_contacts
"""

import os
import sqlite3
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ntchat_bot.settings import DATABASE_PATH


def migrate_contacts_table():
    """迁移 contacts 表，添加缺失字段并填充默认值"""
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
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前表字段: {columns}")
        
        # 需要添加的字段
        required_columns = ['account', 'city', 'province', 'country', 'sex']
        
        # 添加缺失字段
        for col in required_columns:
            if col not in columns:
                print(f"添加字段: {col}")
                if col == 'sex':
                    cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col} INTEGER DEFAULT 0")
                else:
                    cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col} TEXT DEFAULT ''")
        
        # 填充空值
        print("填充空值...")
        cursor.execute("UPDATE contacts SET account = '' WHERE account IS NULL")
        cursor.execute("UPDATE contacts SET city = '' WHERE city IS NULL")
        cursor.execute("UPDATE contacts SET province = '' WHERE province IS NULL")
        cursor.execute("UPDATE contacts SET country = '' WHERE country IS NULL")
        cursor.execute("UPDATE contacts SET sex = 0 WHERE sex IS NULL")
        
        conn.commit()
        print("迁移完成！")
        
        # 验证迁移结果
        cursor.execute("PRAGMA table_info(contacts)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"迁移后表字段: {new_columns}")
        
        # 统计数据
        cursor.execute("SELECT COUNT(*) FROM contacts")
        count = cursor.fetchone()[0]
        print(f"联系人总数: {count}")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    migrate_contacts_table()