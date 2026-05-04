"""
MySQL 数据库服务
"""

import time
from typing import Any, Dict, List, Optional

import mysql.connector
from mysql.connector import Error

from src.ntchat_bot.settings import MYSQL_CONFIG

from .base_service import BaseDatabaseService


class MySQLService(BaseDatabaseService):
    """MySQL数据库服务类（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = MYSQL_CONFIG
        self._conn = None
        self._initialized = True
        self._init_tables()
    
    def _connect(self):
        """建立数据库连接"""
        if self._conn is None or not self._conn.is_connected():
            try:
                self._conn = mysql.connector.connect(
                    host=self.config.get('host', 'localhost'),
                    port=self.config.get('port', 3306),
                    user=self.config.get('user'),
                    password=self.config.get('password'),
                    database=self.config.get('database'),
                    charset='utf8mb4',
                    autocommit=True,
                    pool_size=10,
                    pool_name='wechat_pool'
                )
            except Error as e:
                print(f"MySQL连接失败: {e}")
                raise
    
    def _close(self):
        """关闭数据库连接"""
        if self._conn is not None and self._conn.is_connected():
            self._conn.close()
            self._conn = None
    
    def _init_tables(self):
        """初始化表结构"""
        self._connect()
        try:
            cursor = self._conn.cursor(dictionary=True)
            
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
                    INDEX idx_room_wxid (room_wxid),
                    INDEX idx_create_time (create_time)
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
                    INDEX idx_nickname (nickname),
                    INDEX idx_remark (remark)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # groups 表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_wxid VARCHAR(128) PRIMARY KEY,
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
                    group_wxid VARCHAR(128),
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
                    PRIMARY KEY (group_wxid, wxid),
                    INDEX idx_group_wxid (group_wxid),
                    INDEX idx_wxid (wxid)
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
            
            print("MySQL 表结构初始化完成")
            
        except Error as e:
            print(f"MySQL初始化表失败: {e}")
            raise
    
    def execute(self, sql: str, params: tuple = ()):
        """执行SQL语句"""
        self._connect()
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            return cursor
        except Error as e:
            print(f"MySQL执行失败: {e}, SQL: {sql}")
            raise
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        self._connect()
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Error as e:
            print(f"MySQL查询失败: {e}")
            raise
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """查询多条记录"""
        self._connect()
        try:
            cursor = self._conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Error as e:
            print(f"MySQL查询失败: {e}")
            raise
    
    def insert_message(self, msg_id: str, from_wxid: str, to_wxid: str, room_wxid: str = None, 
                       content: str = None, wx_type: int = 0, timestamp: int = None, 
                       raw_msg: str = None, extra: str = None):
        MAX_RAW_MSG_LENGTH = 65535
        if raw_msg and len(raw_msg) > MAX_RAW_MSG_LENGTH:
            raw_msg = raw_msg[:MAX_RAW_MSG_LENGTH]
        
        sql = '''
            INSERT IGNORE INTO messages 
            (msg_id, from_wxid, to_wxid, room_wxid, content, wx_type, is_group, timestamp, raw_msg, extra)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        is_group = 1 if room_wxid else 0
        self.execute(sql, (msg_id, from_wxid, to_wxid, room_wxid, content, wx_type, is_group, timestamp, raw_msg, extra))
    
    def insert_contact(self, wxid: str, nickname: str = None, remark: str = None, avatar: str = None,
                      account: str = None, city: str = None, province: str = None, 
                      country: str = None, sex: int = None):
        local_time = self._get_local_time()
        existing = self.get_contact(wxid)
        
        if existing:
            update_fields = []
            update_values = []
            
            if account is not None:
                update_fields.append("account = %s")
                update_values.append(account)
            if nickname is not None:
                update_fields.append("nickname = %s")
                update_values.append(nickname)
            if remark is not None:
                update_fields.append("remark = %s")
                update_values.append(remark)
            if avatar is not None:
                update_fields.append("avatar = %s")
                update_values.append(avatar)
            if city is not None:
                update_fields.append("city = %s")
                update_values.append(city)
            if province is not None:
                update_fields.append("province = %s")
                update_values.append(province)
            if country is not None:
                update_fields.append("country = %s")
                update_values.append(country)
            if sex is not None:
                update_fields.append("sex = %s")
                update_values.append(sex)
            
            update_fields.append("update_time = %s")
            update_values.append(local_time)
            update_values.append(wxid)
            
            if update_fields:
                sql = f"UPDATE contacts SET {', '.join(update_fields)} WHERE wxid = %s"
                self.execute(sql, tuple(update_values))
        else:
            sql = '''
                INSERT INTO contacts 
                (wxid, account, nickname, remark, avatar, city, province, country, sex, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            self.execute(sql, (wxid, account or '', nickname or '', remark or '', avatar or '', 
                              city or '', province or '', country or '', sex or 0, local_time, local_time))
    
    def get_contact(self, wxid: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM contacts WHERE wxid = %s"
        return self.fetch_one(sql, (wxid,))
    
    def insert_chatroom(self, group_wxid: str, name: str = None, member_count: int = 0):
        sql = '''
            INSERT INTO groups 
            (group_wxid, name, member_count, update_time)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name = %s, member_count = %s, update_time = %s
        '''
        local_time = self._get_local_time()
        self.execute(sql, (group_wxid, name, member_count, local_time, name, member_count, local_time))
    
    def insert_group_member(self, group_wxid: str, wxid: str, account: str = None, nickname: str = None,
                           display_name: str = None, avatar: str = None, city: str = None, 
                           province: str = None, country: str = None, remark: str = None, sex: int = None):
        sql = '''
            INSERT INTO group_members 
            (group_wxid, wxid, account, nickname, display_name, avatar, city, province, country, remark, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE account = %s, nickname = %s, display_name = %s, 
                                   avatar = %s, city = %s, province = %s, country = %s, remark = %s, sex = %s
        '''
        self.execute(sql, (group_wxid, wxid, account or '', nickname or '', display_name or '', 
                          avatar or '', city or '', province or '', country or '', remark or '', sex or 0,
                          account or '', nickname or '', display_name or '', 
                          avatar or '', city or '', province or '', country or '', remark or '', sex or 0))
    
    def insert_system_event(self, event_type: str, data: str):
        sql = '''
            INSERT INTO system_events (event_type, data)
            VALUES (%s, %s)
        '''
        self.execute(sql, (event_type, data))
    
    def get_messages_by_wxid(self, wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        sql = '''
            SELECT * FROM messages 
            WHERE from_wxid = %s OR to_wxid = %s 
            ORDER BY create_time DESC 
            LIMIT %s
        '''
        return self.fetch_all(sql, (wxid, wxid, limit))
    
    def get_group_messages(self, room_wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        sql = '''
            SELECT * FROM messages 
            WHERE room_wxid = %s 
            ORDER BY create_time DESC 
            LIMIT %s
        '''
        return self.fetch_all(sql, (room_wxid, limit))
    
    def get_all_contacts(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM contacts ORDER BY nickname"
        return self.fetch_all(sql)
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM groups ORDER BY name"
        return self.fetch_all(sql)
    
    def get_group_members(self, group_wxid: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM group_members WHERE group_wxid = %s ORDER BY nickname"
        return self.fetch_all(sql, (group_wxid,))