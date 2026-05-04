# -*- coding: utf-8 -*-
"""
转发消息处理器

消息格式 (type: 11061):
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
    'type': 11061
}
"""

import json

import ntchat

from src.ntchat_bot.services.sqlite_service import SQLiteService


def on_forward_message(wechat_instance: ntchat.WeChat, message):
    """处理转发消息事件"""
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
        db = SQLiteService()
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
            timestamp=timestamp,
            raw_msg=raw_msg,  # 保存完整的原始消息数据
            extra=json.dumps(extra_data, ensure_ascii=False)
        )
        
    except Exception as e:
        print(f"[错误] 处理转发消息异常: {e}, message: {message}")