import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.ntchat_bot.settings import DATABASE_PATH

from .base_service import BaseDatabaseService


class SQLiteService(BaseDatabaseService):
    _instance = None
    _conn = None
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super(SQLiteService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        
        if db_path is None:
            db_path = str(DATABASE_PATH)
        
        self.db_path = db_path
        self._initialized = True
        self._init_tables()
    
    def _connect(self):
        if SQLiteService._conn is None:
            # 启用 WAL 模式支持并发读写
            SQLiteService._conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30  # 增加超时时间
            )
            SQLiteService._conn.row_factory = sqlite3.Row
            # 启用 WAL 模式
            SQLiteService._conn.execute("PRAGMA journal_mode=WAL;")
            SQLiteService._conn.execute("PRAGMA synchronous=NORMAL;")
            SQLiteService._conn.execute("PRAGMA cache_size=-10000;")
    
    def _close(self):
        if SQLiteService._conn is not None:
            SQLiteService._conn.close()
            SQLiteService._conn = None
    
    def _init_tables(self):
        self._connect()
        try:
            cursor = SQLiteService._conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    msg_id TEXT UNIQUE,
                    from_wxid TEXT,
                    to_wxid TEXT,
                    room_wxid TEXT,
                    content TEXT,
                    raw_msg TEXT,
                    wx_type INTEGER,
                    is_group INTEGER DEFAULT 0,
                    timestamp INTEGER,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    extra TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_wxid TEXT PRIMARY KEY,
                    name TEXT,
                    member_count INTEGER DEFAULT 0,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    group_wxid TEXT,
                    wxid TEXT,
                    account TEXT,
                    nickname TEXT,
                    display_name TEXT,
                    avatar TEXT,
                    city TEXT,
                    province TEXT,
                    country TEXT,
                    remark TEXT,
                    sex INTEGER,
                    PRIMARY KEY (group_wxid, wxid)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    data TEXT,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            SQLiteService._conn.commit()
        except Exception as e:
            print(f"初始化表失败: {e}")
    
    def _execute_with_retry(self, sql: str, params: tuple = (), max_retries: int = 3) -> sqlite3.Cursor:
        """带重试机制的执行方法，处理数据库锁定问题"""
        for retry in range(max_retries):
            self._connect()
            try:
                cursor = SQLiteService._conn.cursor()
                cursor.execute(sql, params)
                SQLiteService._conn.commit()
                return cursor
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    if retry < max_retries - 1:
                        time.sleep(0.1 * (retry + 1))
                        continue
                    else:
                        raise
                else:
                    raise
            except Exception:
                raise
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._execute_with_retry(sql, params)
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        self._connect()
        try:
            cursor = SQLiteService._conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.1)
                return self.fetch_one(sql, params)
            raise
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        self._connect()
        try:
            cursor = SQLiteService._conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.1)
                return self.fetch_all(sql, params)
            raise
    
    def _get_local_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def insert_message(self, msg_id: str, from_wxid: str, to_wxid: str, room_wxid: str = None, 
                       content: str = None, wx_type: int = 0, timestamp: int = None, 
                       raw_msg: str = None, extra: str = None):
        # raw_msg 最大长度限制为 64KB
        MAX_RAW_MSG_LENGTH = 65535
        if raw_msg and len(raw_msg) > MAX_RAW_MSG_LENGTH:
            raw_msg = raw_msg[:MAX_RAW_MSG_LENGTH]
        
        sql = '''
            INSERT OR IGNORE INTO messages 
            (msg_id, from_wxid, to_wxid, room_wxid, content, wx_type, is_group, timestamp, raw_msg, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                update_fields.append("account = ?")
                update_values.append(account)
            if nickname is not None:
                update_fields.append("nickname = ?")
                update_values.append(nickname)
            if remark is not None:
                update_fields.append("remark = ?")
                update_values.append(remark)
            if avatar is not None:
                update_fields.append("avatar = ?")
                update_values.append(avatar)
            if city is not None:
                update_fields.append("city = ?")
                update_values.append(city)
            if province is not None:
                update_fields.append("province = ?")
                update_values.append(province)
            if country is not None:
                update_fields.append("country = ?")
                update_values.append(country)
            if sex is not None:
                update_fields.append("sex = ?")
                update_values.append(sex)
            
            update_fields.append("update_time = ?")
            update_values.append(local_time)
            update_values.append(wxid)
            
            if update_fields:
                sql = f"UPDATE contacts SET {', '.join(update_fields)} WHERE wxid = ?"
                self.execute(sql, tuple(update_values))
        else:
            sql = '''
                INSERT INTO contacts 
                (wxid, account, nickname, remark, avatar, city, province, country, sex, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.execute(sql, (wxid, account or '', nickname or '', remark or '', avatar or '', 
                              city or '', province or '', country or '', sex or 0, local_time, local_time))
    
    def get_contact(self, wxid: str) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM contacts WHERE wxid = ?"
        return self.fetch_one(sql, (wxid,))
    
    def insert_chatroom(self, group_wxid: str, name: str = None, member_count: int = 0):
        sql = '''
            INSERT OR REPLACE INTO groups 
            (group_wxid, name, member_count, update_time)
            VALUES (?, ?, ?, ?)
        '''
        local_time = self._get_local_time()
        self.execute(sql, (group_wxid, name, member_count, local_time))
    
    def insert_group_member(self, group_wxid: str, wxid: str, account: str = None, nickname: str = None,
                           display_name: str = None, avatar: str = None, city: str = None, 
                           province: str = None, country: str = None, remark: str = None, sex: int = None):
        sql = '''
            INSERT OR REPLACE INTO group_members 
            (group_wxid, wxid, account, nickname, display_name, avatar, city, province, country, remark, sex)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute(sql, (group_wxid, wxid, account or '', nickname or '', display_name or '', 
                          avatar or '', city or '', province or '', country or '', remark or '', sex or 0))
    
    def insert_system_event(self, event_type: str, data: str):
        sql = '''
            INSERT INTO system_events (event_type, data)
            VALUES (?, ?)
        '''
        self.execute(sql, (event_type, data))
    
    def get_messages_by_wxid(self, wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        sql = '''
            SELECT * FROM messages 
            WHERE from_wxid = ? OR to_wxid = ? 
            ORDER BY create_time DESC 
            LIMIT ?
        '''
        return self.fetch_all(sql, (wxid, wxid, limit))
    
    def get_group_messages(self, room_wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        sql = '''
            SELECT * FROM messages 
            WHERE room_wxid = ? 
            ORDER BY create_time DESC 
            LIMIT ?
        '''
        return self.fetch_all(sql, (room_wxid, limit))
    
    def get_all_contacts(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM contacts ORDER BY nickname"
        return self.fetch_all(sql)
    
    def get_all_groups(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM groups ORDER BY name"
        return self.fetch_all(sql)
    
    def get_group_members(self, group_wxid: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM group_members WHERE group_wxid = ? ORDER BY nickname"
        return self.fetch_all(sql, (group_wxid,))