"""
数据迁移脚本：为 messages 表添加 type 字段
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ntchat_bot.settings import DATABASE_PATH, DATABASE_TYPE, MYSQL_CONFIG


def migrate_sqlite():
    """迁移 SQLite 数据库"""
    import sqlite3
    
    db_path = str(DATABASE_PATH)
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        print("无需迁移，新表会自动创建")
        return
    
    print(f"开始迁移 SQLite 数据库: {db_path}")
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前表字段: {columns}")
        
        # 如果不存在 type 字段则添加
        if 'type' not in columns:
            print("添加 type 字段...")
            cursor.execute("ALTER TABLE messages ADD COLUMN type INTEGER DEFAULT 0")
            conn.commit()
            print("迁移完成！")
        else:
            print("type 字段已存在，无需迁移")
        
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


def migrate_mysql():
    """迁移 MySQL 数据库"""
    import pymysql
    
    config = MYSQL_CONFIG
    print(f"开始迁移 MySQL 数据库: {config.get('host', '')}:{config.get('port', '')}/{config.get('database', '')}")
    
    conn = None
    try:
        conn = pymysql.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            user=config.get('user', 'root'),
            password=config.get('password', ''),
            database=config.get('database', ''),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute("DESCRIBE messages")
        columns = [col[0] for col in cursor.fetchall()]
        print(f"当前表字段: {columns}")
        
        # 如果不存在 type 字段则添加
        if 'type' not in columns:
            print("添加 type 字段...")
            # 在 wx_type 字段后添加 type 字段
            cursor.execute("ALTER TABLE messages ADD COLUMN type INT DEFAULT 0 AFTER wx_type")
            # 添加索引
            cursor.execute("ALTER TABLE messages ADD INDEX idx_type (type)")
            conn.commit()
            print("迁移完成！")
        else:
            print("type 字段已存在，无需迁移")
        
        # 验证结果
        cursor.execute("DESCRIBE messages")
        new_columns = [col[0] for col in cursor.fetchall()]
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


def main():
    """主函数"""
    print("=" * 50)
    print("messages 表 type 字段迁移脚本")
    print("=" * 50)
    
    if DATABASE_TYPE == 'mysql':
        migrate_mysql()
    else:
        migrate_sqlite()
    
    print("=" * 50)


if __name__ == '__main__':
    main()