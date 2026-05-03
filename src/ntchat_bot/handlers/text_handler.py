import json

import ntchat

from src.ntchat_bot.services import SQLiteService


def on_recv_text_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    msg_content = data["msg"]
    
    roomid = data.get("roomid", "")
    is_group = roomid != ""
    
    if from_wxid != self_wxid:
        db = SQLiteService()
        
        if is_group:
            print(f"[群消息] 群ID: {roomid}, 发送者: {from_wxid}, 内容: {msg_content}")
            
            room_info = wechat_instance.get_room_detail(roomid)
            room_name = room_info.get("nickname", "未知群") if room_info else "未知群"
            
            db.insert_chatroom(roomid, room_name)
            
            members = wechat_instance.get_room_members(roomid)
            member_nick = "未知"
            if members:
                for member in members:
                    member_wxid = member.get("wxid")
                    member_name = member.get("nickname")
                    db.insert_room_member(roomid, member_wxid, member_name)
                    if member_wxid == from_wxid:
                        member_nick = member_name or "未知"
            
            print(f"[群消息详情] 群名称: {room_name}, 发送者昵称: {member_nick}, 内容: {msg_content}")
            
            db.insert_message(
                msg_id=data.get("msg_id", ""),
                from_wxid=from_wxid,
                to_wxid=roomid,
                content=msg_content,
                msg_type=message.get("type", 0),
                roomid=roomid,
                extra=json.dumps({"sender_nick": member_nick, "room_name": room_name})
            )
            
            wechat_instance.send_text(to_wxid=roomid, content=f"@{member_nick} 收到你的消息: {msg_content}")
        else:
            print(f"[联系人消息] 发送者: {from_wxid}, 内容: {msg_content}")
            
            contact_info = wechat_instance.get_contact_detail(from_wxid)
            contact_name = contact_info.get("nickname", "未知") if contact_info else "未知"
            
            db.insert_contact(
                wxid=from_wxid,
                nickname=contact_name,
                remark=contact_info.get("remark") if contact_info else None
            )
            
            print(f"[联系人消息详情] 联系人: {contact_name}, 内容: {msg_content}")
            
            db.insert_message(
                msg_id=data.get("msg_id", ""),
                from_wxid=from_wxid,
                to_wxid=self_wxid,
                content=msg_content,
                msg_type=message.get("type", 0),
                extra=json.dumps({"contact_name": contact_name})
            )
            
            wechat_instance.send_text(to_wxid=from_wxid, content=f"你发送的消息是: {msg_content}")