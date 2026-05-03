import ntchat


def on_recv_text_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    msg_content = data["msg"]
    
    roomid = data.get("roomid", "")
    is_group = roomid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群消息] 群ID: {roomid}, 发送者: {from_wxid}, 内容: {msg_content}")
            
            room_info = wechat_instance.get_room_detail(roomid)
            room_name = room_info.get("nickname", "未知群") if room_info else "未知群"
            
            members = wechat_instance.get_room_members(roomid)
            member_nick = "未知"
            if members:
                for member in members:
                    if member.get("wxid") == from_wxid:
                        member_nick = member.get("nickname", "未知")
                        break
            
            print(f"[群消息详情] 群名称: {room_name}, 发送者昵称: {member_nick}, 内容: {msg_content}")
            
            wechat_instance.send_text(to_wxid=roomid, content=f"@{member_nick} 收到你的消息: {msg_content}")
        else:
            print(f"[联系人消息] 发送者: {from_wxid}, 内容: {msg_content}")
            
            contact_info = wechat_instance.get_contact_detail(from_wxid)
            contact_name = contact_info.get("nickname", "未知") if contact_info else "未知"
            
            print(f"[联系人消息详情] 联系人: {contact_name}, 内容: {msg_content}")
            
            wechat_instance.send_text(to_wxid=from_wxid, content=f"你发送的消息是: {msg_content}")