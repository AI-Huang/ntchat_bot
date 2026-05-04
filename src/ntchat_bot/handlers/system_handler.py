import ntchat


def on_recv_friend_request(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    verify_content = data.get("verify_content", "")
    
    print(f"[好友请求] 请求者ID: {from_wxid}, 请求内容: {verify_content}")


def on_recv_revoke_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if is_group:
        room_name = wechat_instance.get_room_name(room_wxid)
        if not room_name:
            room_name = "未知群"
        print(f"[群撤回消息] 群: {room_name}, 撤回者: {from_wxid}")
    else:
        print(f"[联系人撤回消息] 撤回者: {from_wxid}")


def on_user_login(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    wxid = data["wxid"]
    name = data.get("nickname", "")
    print(f"[登录成功] 微信ID: {wxid}, 昵称: {name}")


def on_user_logout(wechat_instance: ntchat.WeChat, message):
    print("[退出登录] 用户已退出微信")