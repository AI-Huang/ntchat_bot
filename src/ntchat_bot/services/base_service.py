"""
数据库服务抽象基类
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class BaseDatabaseService(ABC):
    """数据库服务抽象基类"""
    
    def _get_local_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_utc_time(self):
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    @abstractmethod
    def execute(self, sql: str, params: tuple = ()):
        pass
    
    @abstractmethod
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def _init_tables(self):
        pass
    
    @abstractmethod
    def insert_message(self, msg_id: str, from_wxid: str, to_wxid: str, room_wxid: str = None, 
                       content: str = None, wx_type: int = 0, type: int = 0, timestamp: int = None, 
                       raw_msg: str = None, extra: str = None):
        pass
    
    @abstractmethod
    def insert_contact(self, wxid: str, nickname: str = None, remark: str = None, avatar: str = None,
                      account: str = None, city: str = None, province: str = None, 
                      country: str = None, sex: int = None):
        pass
    
    @abstractmethod
    def get_contact(self, wxid: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def insert_chatroom(self, room_wxid: str, name: str = None, member_count: int = 0):
        pass
    
    @abstractmethod
    def insert_group_member(self, room_wxid: str, wxid: str, account: str = None, nickname: str = None,
                           display_name: str = None, avatar: str = None, city: str = None, 
                           province: str = None, country: str = None, remark: str = None, sex: int = None):
        pass
    
    @abstractmethod
    def insert_system_event(self, event_type: str, data: str):
        pass
    
    @abstractmethod
    def get_messages_by_wxid(self, wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_group_messages(self, room_wxid: str, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_all_contacts(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_all_rooms(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_group_members(self, room_wxid: str) -> List[Dict[str, Any]]:
        pass