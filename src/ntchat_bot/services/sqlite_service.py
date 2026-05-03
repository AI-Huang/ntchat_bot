import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.ntchat_bot.settings import DATABASE_PATH


class SQLiteService:
    _instance = None
    
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
        self.conn = None
        self._initialized = True
        self._init_tables()
    
    def _connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def _close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
    
    def _init_tables(self):
        self._connect()
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    msg_id TEXT UNIQUE,
                    from_wxid TEXT,
                    to_wxid TEXT,
                    roomid TEXT,
                    content TEXT,
                    msg_type INTEGER,
                    is_group INTEGER DEFAULT 0,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    extra TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    wxid TEXT PRIMARY KEY,
                    nickname TEXT,
                    remark TEXT,
                    avatar TEXT,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chatrooms (
                    roomid TEXT PRIMARY KEY,
                    name TEXT,
                    member_count INTEGER DEFAULT 0,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_time TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS room_members (
                    roomid TEXT,
                    wxid TEXT,
                    nickname TEXT,
                    PRIMARY KEY (roomid, wxid)
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
            
            self.conn.commit()
        finally:
            self._close()
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        self._connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor
        finally:
            self._close()
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        self._connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            self._close()
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        self._connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            self._close()
    
    def insert_message(self, msg_id: str, from_wxid: str, to_wxid: str, content: str, 
                       msg_type: int, roomid: str = None, extra: str = None):
        sql = '''
            INSERT OR REPLACE INTO messages 
            (msg_id, from_wxid, to_wxid, roomid, content, msg_type, is_group, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        is_group = 1 if roomid else 0
        self.execute(sql, (msg_id, from_wxid, to_wxid, roomid, content, msg_type, is_group, extra))
    
    def insert_contact(self, wxid: str, nickname: str = None, remark: str = None, avatar: str = None):
        sql = '''
            INSERT OR REPLACE INTO contacts 
            (wxid, nickname, remark, avatar, update_time)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.execute(sql, (wxid, nickname, remark, avatar, datetime.now().isoformat()))
    
    def insert_chatroom(self, roomid: str, name: str = None, member_count: int = 0):
        sql = '''
            INSERT OR REPLACE INTO chatrooms 
            (roomid, name, member_count, update_time)
            VALUES (?, ?, ?, ?)
        '''
        self.execute(sql, (roomid, name, member_count, datetime.now().isoformat()))
    
    def insert_room_member(self, roomid: str, wxid: str, nickname: str = None):
        sql = '''
            INSERT OR REPLACE INTO room_members (roomid, wxid, nickname)
            VALUES (?, ?, ?)
        '''
        self.execute(sql, (roomid, wxid, nickname))
    
    def delete_room_member(self, roomid: str, wxid: str):
        sql = 'DELETE FROM room_members WHERE roomid = ? AND wxid = ?'
        self.execute(sql, (roomid, wxid))
    
    def insert_system_event(self, event_type: str, data: str):
        sql = 'INSERT INTO system_events (event_type, data) VALUES (?, ?)'
        self.execute(sql, (event_type, data))
    
    def get_message_by_id(self, msg_id: str) -> Optional[Dict[str, Any]]:
        sql = 'SELECT * FROM messages WHERE msg_id = ?'
        return self.fetch_one(sql, (msg_id,))
    
    def get_messages_by_wxid(self, wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        sql = 'SELECT * FROM messages WHERE from_wxid = ? ORDER BY create_time DESC LIMIT ?'
        return self.fetch_all(sql, (wxid, limit))
    
    def get_messages_by_roomid(self, roomid: str, limit: int = 100) -> List[Dict[str, Any]]:
        sql = 'SELECT * FROM messages WHERE roomid = ? ORDER BY create_time DESC LIMIT ?'
        return self.fetch_all(sql, (roomid, limit))
    
    def get_contact(self, wxid: str) -> Optional[Dict[str, Any]]:
        sql = 'SELECT * FROM contacts WHERE wxid = ?'
        return self.fetch_one(sql, (wxid,))
    
    def get_all_contacts(self) -> List[Dict[str, Any]]:
        sql = 'SELECT * FROM contacts ORDER BY update_time DESC'
        return self.fetch_all(sql)
    
    def get_chatroom(self, roomid: str) -> Optional[Dict[str, Any]]:
        sql = 'SELECT * FROM chatrooms WHERE roomid = ?'
        return self.fetch_one(sql, (roomid,))
    
    def get_all_chatrooms(self) -> List[Dict[str, Any]]:
        sql = 'SELECT * FROM chatrooms ORDER BY update_time DESC'
        return self.fetch_all(sql)
    
    def get_room_members(self, roomid: str) -> List[Dict[str, Any]]:
        sql = 'SELECT * FROM room_members WHERE roomid = ?'
        return self.fetch_all(sql, (roomid,))
    
    def get_system_events(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        if event_type:
            sql = 'SELECT * FROM system_events WHERE event_type = ? ORDER BY create_time DESC LIMIT ?'
            return self.fetch_all(sql, (event_type, limit))
        else:
            sql = 'SELECT * FROM system_events ORDER BY create_time DESC LIMIT ?'
            return self.fetch_all(sql, (limit,))
    
    def get_stats(self) -> Dict[str, int]:
        contacts_count = self.fetch_one('SELECT COUNT(*) as count FROM contacts')['count']
        chatrooms_count = self.fetch_one('SELECT COUNT(*) as count FROM chatrooms')['count']
        messages_count = self.fetch_one('SELECT COUNT(*) as count FROM messages')['count']
        
        return {
            'contacts_count': contacts_count,
            'chatrooms_count': chatrooms_count,
            'messages_count': messages_count
        }