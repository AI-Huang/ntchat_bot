import ntchat


def on_recv_image_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    image_path = data["image_path"]
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群图片消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 图片路径: {image_path}")
        else:
            print(f"[联系人图片消息] 发送者: {from_wxid}, 图片路径: {image_path}")


def on_recv_voice_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    voice_path = data["voice_path"]
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群语音消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 语音路径: {voice_path}")
        else:
            print(f"[联系人语音消息] 发送者: {from_wxid}, 语音路径: {voice_path}")


def on_recv_video_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    video_path = data["video_path"]
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群视频消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 视频路径: {video_path}")
        else:
            print(f"[联系人视频消息] 发送者: {from_wxid}, 视频路径: {video_path}")


def on_recv_emoji_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群表情消息] 群ID: {room_wxid}, 发送者: {from_wxid}")
        else:
            print(f"[联系人表情消息] 发送者: {from_wxid}")


def on_recv_location_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    location = data.get("location", "")
    latitude = data.get("latitude", "")
    longitude = data.get("longitude", "")
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群位置消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 位置: {location}, 坐标: {latitude},{longitude}")
        else:
            print(f"[联系人位置消息] 发送者: {from_wxid}, 位置: {location}, 坐标: {latitude},{longitude}")


def on_recv_link_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    title = data.get("title", "")
    description = data.get("description", "")
    url = data.get("url", "")
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群链接消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 标题: {title}, 描述: {description}, 链接: {url}")
        else:
            print(f"[联系人链接消息] 发送者: {from_wxid}, 标题: {title}, 描述: {description}, 链接: {url}")


def on_recv_file_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    file_path = data["file_path"]
    file_name = data.get("file_name", "")
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群文件消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 文件名: {file_name}, 文件路径: {file_path}")
        else:
            print(f"[联系人文件消息] 发送者: {from_wxid}, 文件名: {file_name}, 文件路径: {file_path}")


def on_recv_card_msg(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    from_wxid = data["from_wxid"]
    self_wxid = wechat_instance.get_login_info()["wxid"]
    card_wxid = data.get("card_wxid", "")
    card_name = data.get("card_name", "")
    
    room_wxid = data.get("room_wxid", "")
    is_group = room_wxid != ""
    
    if from_wxid != self_wxid:
        if is_group:
            print(f"[群名片消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 名片ID: {card_wxid}, 名片名称: {card_name}")
        else:
            print(f"[联系人名片消息] 发送者: {from_wxid}, 名片ID: {card_wxid}, 名片名称: {card_name}")