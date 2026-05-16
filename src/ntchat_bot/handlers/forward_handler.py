# -*- coding: utf-8 -*-
"""
转发消息处理器

支持的消息类型:
- 11061: 转发消息
- 11054: 公众号推送消息

消息格式:
{
    'data': {
        'from_wxid': '发送者wxid',
        'is_pc': 0,
        'msgid': '消息ID',
        'raw_msg': '<msg><appmsg>...</appmsg></msg>',  # XML格式的原始消息
        'room_wxid': '群ID@chatroom',  # 群消息时存在
        'timestamp': 时间戳,
        'to_wxid': '接收者wxid',
        'wx_sub_type': 19,  # 19表示聊天记录
        'wx_type': 49       # 49表示文件消息
    },
    'type': 11061 或 11054
}
"""

import json

import ntchat

from src.ntchat_bot.services import DatabaseServiceFactory


def on_forward_message(wechat_instance: ntchat.WeChat, message):
    """处理转发消息事件 (type: 11061)"""
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[错误] 转发消息 data 是字符串类型: {data[:100]}...")
            return
        
        msg_id = data.get("msgid")
        from_wxid = data.get("from_wxid")
        to_wxid = data.get("to_wxid")
        room_wxid = data.get("room_wxid")
        raw_msg = data.get("raw_msg", "")
        timestamp = data.get("timestamp")
        
        is_group = 1 if room_wxid else 0
        
        if is_group:
            print(f"[群转发消息] 群ID: {room_wxid}, 发送者: {from_wxid}, msgid: {msg_id}")
        else:
            print(f"[联系人转发消息] 发送者: {from_wxid}, msgid: {msg_id}")
        
        # 保存到数据库
        db = DatabaseServiceFactory.get_service()
        extra_data = {
            "wx_sub_type": data.get("wx_sub_type"),
            "is_pc": data.get("is_pc")
        }
        db.insert_message(
            msg_id=msg_id,
            from_wxid=from_wxid,
            to_wxid=to_wxid,
            room_wxid=room_wxid,
            content="",  # 转发消息的内容放在 raw_msg 中
            wx_type=data.get("wx_type", 49),
            type=message.get("type", 0),  # 保存消息类型，如 11061
            timestamp=timestamp,
            raw_msg=raw_msg,  # 保存完整的原始消息数据
            extra=json.dumps(extra_data, ensure_ascii=False)
        )
        
    except Exception as e:
        print(f"[错误] 处理转发消息异常: {e}, message: {message}")


def on_official_account_message(wechat_instance: ntchat.WeChat, message):
    """处理公众号推送消息事件 (type: 11054)
    
    公众号推送消息通常包含文章链接，消息格式与转发消息类似。
    """
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[错误] 公众号消息 data 是字符串类型: {data[:100]}...")
            return
        
        msg_id = data.get("msgid")
        from_wxid = data.get("from_wxid")
        to_wxid = data.get("to_wxid")
        room_wxid = data.get("room_wxid")
        raw_msg = data.get("raw_msg", "")
        timestamp = data.get("timestamp")
        
        is_group = 1 if room_wxid else 0
        
        if is_group:
            print(f"[群公众号消息] 群ID: {room_wxid}, 公众号: {from_wxid}, msgid: {msg_id}")
        else:
            print(f"[公众号消息] 公众号: {from_wxid}, msgid: {msg_id}")
        
        # 保存到数据库
        db = DatabaseServiceFactory.get_service()
        extra_data = {
            "wx_sub_type": data.get("wx_sub_type"),
            "is_pc": data.get("is_pc"),
            "source": "official_account"
        }
        db.insert_message(
            msg_id=msg_id,
            from_wxid=from_wxid,
            to_wxid=to_wxid,
            room_wxid=room_wxid,
            content="",  # 公众号消息内容放在 raw_msg 中
            wx_type=data.get("wx_type", 49),
            type=message.get("type", 0),  # 保存消息类型，如 11054
            timestamp=timestamp,
            raw_msg=raw_msg,  # 保存完整的原始消息数据（包含文章信息）
            extra=json.dumps(extra_data, ensure_ascii=False)
        )
        
    except Exception as e:
        print(f"[错误] 处理公众号消息异常: {e}, message: {message}")