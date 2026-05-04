"""
数据库迁移脚本：将 SQLite 数据迁移到 MySQL

使用方法：
1. 配置 .env 文件中的 MySQL 连接信息
2. 确保 MySQL 中已创建数据库
3. 运行脚本：python -m scripts.migrate_sqlite_to_mysql

注意：
- 迁移前请备份 SQLite 数据库
- 确保 MySQL 服务已启动
- 脚本会自动创建表结构
"""

import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mysql.connector
from mysql.connector import Error

from src.ntchat_bot.settings import DATABASE_PATH, MYSQL_CONFIG


def connect_sqlite(db_path):
    """连接 SQLite 数据库"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print(f"✓ SQLite 连接成功: {db_path}")
        return conn
    except Exception as e:
        print(f"✗ SQLite 连接失败: {e}")
        return None


def connect_mysql(config):
    """连接 MySQL 数据库"""
    try:
        conn = mysql.connector.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            user=config.get('user'),
            password=config.get('password'),
            database=config.get('database'),
            charset='utf8mb4',
            autocommit=True
        )
        print(f"✓ MySQL 连接成功: {config.get('host')}:{config.get('port')}/{config.get('database')}")
        return conn
    except Error as e:
        print(f"✗ MySQL 连接失败: {e}")
        return None


def init_mysql_tables(mysql_conn):
    """初始化 MySQL 表结构"""
    try:
        cursor = mysql_conn.cursor()
        
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
                create_time DATETIME,
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
                create_time DATETIME,
                update_time DATETIME,
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
                create_time DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        print("✓ MySQL 表结构初始化完成")
        return True
    except Error as e:
        print(f"✗ MySQL 表初始化失败: {e}")
        return False


def migrate_table(sqlite_conn, mysql_conn, table_name, columns, sql_template):
    """迁移单个表的数据"""
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()
        
        # 查询 SQLite 中的数据
        sqlite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  - {table_name}: 无数据需要迁移")
            return 0
        
        # 插入 MySQL
        count = 0
        for row in rows:
            try:
                values = tuple(row)
                mysql_cursor.execute(sql_template, values)
                count += 1
            except Error as e:
                if "Duplicate entry" in str(e):
                    print(f"    ! 跳过重复数据: {row[0]}")
                    continue
                else:
                    print(f"    ! 插入失败: {e}")
                    continue
        
        print(f"  ✓ {table_name}: {count} 条数据迁移成功")
        return count
    except Exception as e:
        print(f"  ✗ {table_name} 迁移失败: {e}")
        return 0


def main():
    print("=" * 60)
    print("SQLite 到 MySQL 数据迁移脚本")
    print("=" * 60)
    
    # 连接数据库
    sqlite_conn = connect_sqlite(str(DATABASE_PATH))
    if not sqlite_conn:
        print("✗ SQLite 连接失败，退出")
        return
    
    mysql_conn = connect_mysql(MYSQL_CONFIG)
    if not mysql_conn:
        print("✗ MySQL 连接失败，退出")
        sqlite_conn.close()
        return
    
    # 初始化 MySQL 表结构
    if not init_mysql_tables(mysql_conn):
        sqlite_conn.close()
        mysql_conn.close()
        return
    
    print("\n开始数据迁移...")
    
    total_count = 0
    
    # 迁移 contacts 表
    print("\n[1/5] 迁移 contacts 表")
    contacts_columns = [
        'wxid', 'account', 'nickname', 'remark', 'avatar',
        'city', 'province', 'country', 'sex', 'create_time', 'update_time'
    ]
    contacts_sql = '''
        INSERT IGNORE INTO contacts 
        (wxid, account, nickname, remark, avatar, city, province, country, sex, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    total_count += migrate_table(sqlite_conn, mysql_conn, 'contacts', contacts_columns, contacts_sql)
    
    # 迁移 rooms 表
    print("\n[2/5] 迁移 rooms 表")
    rooms_columns = ['room_wxid', 'name', 'member_count', 'create_time', 'update_time']
    rooms_sql = '''
        INSERT IGNORE INTO rooms 
        (room_wxid, name, member_count, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s)
    '''
    total_count += migrate_table(sqlite_conn, mysql_conn, 'rooms', rooms_columns, rooms_sql)
    
    # 迁移 group_members 表
    print("\n[3/5] 迁移 group_members 表")
    members_columns = [
        'room_wxid', 'wxid', 'account', 'nickname', 'display_name',
        'avatar', 'city', 'province', 'country', 'remark', 'sex'
    ]
    members_sql = '''
        INSERT IGNORE INTO group_members 
        (room_wxid, wxid, account, nickname, display_name, avatar, city, province, country, remark, sex)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    total_count += migrate_table(sqlite_conn, mysql_conn, 'group_members', members_columns, members_sql)
    
    # 迁移 messages 表
    print("\n[4/5] 迁移 messages 表")
    messages_columns = [
        'msg_id', 'from_wxid', 'to_wxid', 'room_wxid', 'content', 'raw_msg',
        'wx_type', 'is_group', 'timestamp', 'create_time', 'extra'
    ]
    messages_sql = '''
        INSERT IGNORE INTO messages 
        (msg_id, from_wxid, to_wxid, room_wxid, content, raw_msg, wx_type, is_group, timestamp, create_time, extra)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    total_count += migrate_table(sqlite_conn, mysql_conn, 'messages', messages_columns, messages_sql)
    
    # 迁移 system_events 表
    print("\n[5/5] 迁移 system_events 表")
    events_columns = ['event_type', 'data', 'create_time']
    events_sql = '''
        INSERT INTO system_events (event_type, data, create_time)
        VALUES (%s, %s, %s)
    '''
    total_count += migrate_table(sqlite_conn, mysql_conn, 'system_events', events_columns, events_sql)
    
    # 关闭连接
    sqlite_conn.close()
    mysql_conn.close()
    
    print("\n" + "=" * 60)
    print(f"迁移完成！共迁移 {total_count} 条数据")
    print("=" * 60)


if __name__ == '__main__':
    main()