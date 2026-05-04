"""
创建 MySQL 数据库脚本

使用方法：
1. 配置 .env 文件中的 MySQL 连接信息
2. 运行脚本：python -m scripts.create_mysql_database

注意：需要确保 MySQL 用户有创建数据库的权限
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mysql.connector
from mysql.connector import Error

from src.ntchat_bot.settings import MYSQL_CONFIG


def create_database():
    """创建 MySQL 数据库"""
    config = MYSQL_CONFIG.copy()
    db_name = config.pop('database', 'wechat')
    
    try:
        # 先连接到 MySQL（不指定数据库）
        conn = mysql.connector.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            user=config.get('user'),
            password=config.get('password'),
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        create_db_sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        cursor.execute(create_db_sql)
        
        # 检查数据库是否创建成功
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if result:
            print(f"✓ 数据库 '{db_name}' 创建成功（或已存在）")
            
            # 设置为当前数据库
            cursor.execute(f"USE `{db_name}`")
            
            # 创建必要的表结构（可选）
            print("  初始化表结构...")
            init_tables(cursor)
            print("  ✓ 表结构初始化完成")
        else:
            print(f"✗ 数据库 '{db_name}' 创建失败")
        
        conn.close()
        return True
        
    except Error as e:
        print(f"✗ MySQL 操作失败: {e}")
        return False


def init_tables(cursor):
    """初始化表结构"""
    # messages 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            msg_id VARCHAR(64) UNIQUE NOT NULL,
            from_wxid VARCHAR(128),
            to_wxid VARCHAR(128),
            room_wxid VARCHAR(128),
            content TEXT,
            raw_msg TEXT,
            wx_type INT DEFAULT 0,
            is_group TINYINT DEFAULT 0,
            timestamp BIGINT,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            extra TEXT,
            INDEX idx_from_wxid (from_wxid),
            INDEX idx_to_wxid (to_wxid),
            INDEX idx_room_wxid (room_wxid)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # contacts 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            wxid VARCHAR(128) PRIMARY KEY,
            account VARCHAR(128),
            nickname VARCHAR(256),
            remark VARCHAR(256),
            avatar TEXT,
            city VARCHAR(128),
            province VARCHAR(128),
            country VARCHAR(32),
            sex TINYINT DEFAULT 0,
            create_time DATETIME,
            update_time DATETIME,
            INDEX idx_nickname (nickname)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # rooms 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_wxid VARCHAR(128) PRIMARY KEY,
            name VARCHAR(256),
            member_count INT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # group_members 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            room_wxid VARCHAR(128),
            wxid VARCHAR(128),
            account VARCHAR(128),
            nickname VARCHAR(256),
            display_name VARCHAR(256),
            avatar TEXT,
            city VARCHAR(128),
            province VARCHAR(128),
            country VARCHAR(32),
            remark VARCHAR(256),
            sex TINYINT DEFAULT 0,
            PRIMARY KEY (room_wxid, wxid)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # system_events 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_type VARCHAR(64),
            data TEXT,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_event_type (event_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')


def main():
    print("=" * 60)
    print("创建 MySQL 数据库")
    print("=" * 60)
    
    print(f"配置信息:")
    print(f"  主机: {MYSQL_CONFIG.get('host', 'localhost')}")
    print(f"  端口: {MYSQL_CONFIG.get('port', 3306)}")
    print(f"  用户: {MYSQL_CONFIG.get('user')}")
    print(f"  数据库: {MYSQL_CONFIG.get('database', 'wechat')}")
    print()
    
    success = create_database()
    
    if success:
        print("\n✓ 操作完成！")
        print("提示：可以运行迁移脚本将 SQLite 数据迁移到 MySQL")
        print("命令: python -m scripts.migrate_sqlite_to_mysql")
    else:
        print("\n✗ 操作失败，请检查 MySQL 连接信息和权限")


if __name__ == '__main__':
    main()