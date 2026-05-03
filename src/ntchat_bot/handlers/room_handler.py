import ntchat


def on_room_add_member(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    roomid = data["roomid"]
    op_wxid = data.get("op_wxid", "")
    member_list = data.get("member_list", [])
    
    room_name = wechat_instance.get_room_name(roomid)
    if not room_name:
        room_name = "未知群"
    
    print(f"[群成员加入] 群: {room_name}, 操作人: {op_wxid}, 新成员: {member_list}")


def on_room_del_member(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    roomid = data["roomid"]
    op_wxid = data.get("op_wxid", "")
    member_list = data.get("member_list", [])
    
    room_name = wechat_instance.get_room_name(roomid)
    if not room_name:
        room_name = "未知群"
    
    print(f"[群成员退出] 群: {room_name}, 操作人: {op_wxid}, 退出成员: {member_list}")