"""
群消息事件格式说明:

群成员列表事件 (type: 11032):
{
    'data': {
        'extend': '',
        'room_wxid': '群ID@chatroom',
        'member_list': [
            {
                'account': '微信号',
                'avatar': '头像URL',
                'city': '城市',
                'country': '国家代码',
                'display_name': '群内显示名',
                'nickname': '昵称',
                'province': '省份',
                'remark': '备注',
                'sex': 1,  # 1=男, 2=女
                'wxid': '用户wxid'
            }
        ],
        'total': 成员总数
    },
    'extend': 'UUID',
    'type': 11032
}

群邀请消息 (type: 11058):
{
    'data': {
        'from_wxid': '发送者wxid',
        'is_pc': 0,
        'msgid': '消息ID',
        'raw_msg': '"昵称"邀请"昵称"加入了群聊',
        'room_name': '群名称',
        'room_wxid': '群ID@chatroom',
        'timestamp': 时间戳,
        'to_wxid': '群ID@chatroom',
        'wx_type': 10000
    },
    'type': 11058
}

群成员列表更新 (type: 11200):
{
    'data': {
        'member_list': [
            {'display_name': '群内显示名', 'nickname': '昵称', 'wxid': '用户wxid'}
        ],
        'room_wxid': '群ID@chatroom'
    },
    'type': 11200
}

群成员加入详情 (type: 11098):
{
    'data': {
        'avatar': '群头像URL',
        'is_manager': 0,
        'manager_wxid': '管理员wxid',
        'member_list': [
            {
                'avatar': '成员头像URL',
                'invite_by': '邀请人wxid',
                'nickname': '昵称',
                'wxid': '用户wxid'
            }
        ],
        'nickname': '群名称',
        'room_wxid': '群ID@chatroom',
        'total_member': 成员总数
    },
    'type': 11098
}

群成员加入事件:
{
    'data': {
        'room_wxid': '群ID@chatroom',
        'op_wxid': '操作人wxid',
        'member_list': ['成员wxid1', '成员wxid2', ...]
    },
    'type': 群成员加入类型码
}

群成员退出事件:
{
    'data': {
        'room_wxid': '群ID@chatroom',
        'op_wxid': '操作人wxid',
        'member_list': ['成员wxid1', '成员wxid2', ...]
    },
    'type': 群成员退出类型码
}
"""


import ntchat

from src.ntchat_bot.services import DatabaseServiceFactory


def on_room_member_list(wechat_instance: ntchat.WeChat, message):
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[警告] 群成员列表事件 data 是字符串: {data}")
            return
        
        if not isinstance(data, dict):
            print(f"[警告] 群成员列表事件 data 不是字典: {type(data)}")
            return
        
        room_wxid = data.get("room_wxid", "")
        if not room_wxid:
            print(f"[警告] 群成员列表事件缺少 room_wxid: {data}")
            return
        
        member_list = data.get("member_list", [])
        total = data.get("total", 0)
        
        print(f"[群成员列表] 群ID: {room_wxid}, 成员总数: {total}")
        
        db = DatabaseServiceFactory.get_service()
        
        room_info = wechat_instance.get_room_detail(room_wxid)
        if isinstance(room_info, dict):
            room_name = room_info.get("nickname", "未知群")
        else:
            room_name = "未知群"
        
        db.insert_chatroom(room_wxid, room_name, total)
        
        if isinstance(member_list, list):
            for member in member_list:
                if isinstance(member, dict):
                    wxid = member.get("wxid")
                    if wxid:
                        account = member.get("account")
                        nickname = member.get("nickname")
                        display_name = member.get("display_name")
                        avatar = member.get("avatar")
                        city = member.get("city")
                        province = member.get("province")
                        country = member.get("country")
                        remark = member.get("remark")
                        sex = member.get("sex")
                        
                        db.insert_room_member(
                            room_wxid=room_wxid,
                            wxid=wxid,
                            account=account,
                            nickname=nickname,
                            display_name=display_name,
                            avatar=avatar,
                            city=city,
                            province=province,
                            country=country,
                            remark=remark,
                            sex=sex
                        )
                        print(f"  - 成员: {wxid}, 昵称: {nickname}")
                else:
                    print(f"[警告] 成员不是字典: {member}")
        else:
            print(f"[警告] member_list 不是列表: {type(member_list)}")
            
    except Exception as e:
        print(f"[错误] 处理群成员列表事件异常: {e}")


def on_room_add_member(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    room_wxid = data["room_wxid"]
    op_wxid = data.get("op_wxid", "")
    member_list = data.get("member_list", [])
    
    room_name = wechat_instance.get_room_name(room_wxid)
    if not room_name:
        room_name = "未知群"
    
    print(f"[群成员加入] 群: {room_name}, 操作人: {op_wxid}, 新成员: {member_list}")


def on_room_del_member(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    room_wxid = data["room_wxid"]
    op_wxid = data.get("op_wxid", "")
    member_list = data.get("member_list", [])
    
    room_name = wechat_instance.get_room_name(room_wxid)
    if not room_name:
        room_name = "未知群"
    
    print(f"[群成员退出] 群: {room_name}, 操作人: {op_wxid}, 退出成员: {member_list}")


def on_room_invite_message(wechat_instance: ntchat.WeChat, message):
    """处理群邀请消息 (type: 11058)"""
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[警告] 群邀请消息 data 是字符串: {data}")
            return
        
        if not isinstance(data, dict):
            print(f"[警告] 群邀请消息 data 不是字典: {type(data)}")
            return
        
        from_wxid = data.get("from_wxid", "")
        room_wxid = data.get("room_wxid", "")
        room_name = data.get("room_name", "未知群")
        raw_msg = data.get("raw_msg", "")
        msg_id = data.get("msgid", "")
        
        print(f"[群邀请消息] 群: {room_name}({room_wxid}), 发送者: {from_wxid}, 消息: {raw_msg}")
        
        # 保存到数据库
        db = DatabaseServiceFactory.get_service()
        db.insert_message(
            msg_id=msg_id,
            from_wxid=from_wxid,
            to_wxid=room_wxid,
            room_wxid=room_wxid,
            content=raw_msg,
            wx_type=data.get("wx_type", 10000),
            type=message.get("type", 0),
            timestamp=data.get("timestamp"),
            extra='{"event_type": "room_invite"}'
        )
        
    except Exception as e:
        print(f"[错误] 处理群邀请消息异常: {e}")


def on_room_member_update(wechat_instance: ntchat.WeChat, message):
    """处理群成员列表更新 (type: 11200)"""
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[警告] 群成员列表更新 data 是字符串: {data}")
            return
        
        if not isinstance(data, dict):
            print(f"[警告] 群成员列表更新 data 不是字典: {type(data)}")
            return
        
        room_wxid = data.get("room_wxid", "")
        member_list = data.get("member_list", [])
        
        print(f"[群成员列表更新] 群ID: {room_wxid}")
        
        if isinstance(member_list, list):
            for member in member_list:
                if isinstance(member, dict):
                    wxid = member.get("wxid")
                    nickname = member.get("nickname")
                    display_name = member.get("display_name")
                    print(f"  - 成员: {wxid}, 昵称: {nickname}, 群内名称: {display_name}")
                    
                    # 更新群成员信息
                    db = DatabaseServiceFactory.get_service()
                    db.insert_group_member(
                        room_wxid=room_wxid,
                        wxid=wxid,
                        nickname=nickname,
                        display_name=display_name
                    )
                else:
                    print(f"[警告] 成员不是字典: {member}")
        else:
            print(f"[警告] member_list 不是列表: {type(member_list)}")
            
    except Exception as e:
        print(f"[错误] 处理群成员列表更新异常: {e}")


def on_room_member_join_detail(wechat_instance: ntchat.WeChat, message):
    """处理群成员加入详情 (type: 11098)"""
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[警告] 群成员加入详情 data 是字符串: {data}")
            return
        
        if not isinstance(data, dict):
            print(f"[警告] 群成员加入详情 data 不是字典: {type(data)}")
            return
        
        room_wxid = data.get("room_wxid", "")
        room_name = data.get("nickname", "未知群")
        total_member = data.get("total_member", 0)
        manager_wxid = data.get("manager_wxid", "")
        member_list = data.get("member_list", [])
        
        print(f"[群成员加入详情] 群: {room_name}({room_wxid}), 成员总数: {total_member}, 管理员: {manager_wxid}")
        
        # 更新群信息
        db = DatabaseServiceFactory.get_service()
        db.insert_chatroom(room_wxid, room_name, total_member)
        
        if isinstance(member_list, list):
            for member in member_list:
                if isinstance(member, dict):
                    wxid = member.get("wxid")
                    nickname = member.get("nickname")
                    avatar = member.get("avatar")
                    invite_by = member.get("invite_by", "")
                    print(f"  - 新成员: {wxid}, 昵称: {nickname}, 被邀请人: {invite_by}")
                    
                    db.insert_group_member(
                        room_wxid=room_wxid,
                        wxid=wxid,
                        nickname=nickname,
                        avatar=avatar
                    )
                else:
                    print(f"[警告] 成员不是字典: {member}")
        else:
            print(f"[警告] member_list 不是列表: {type(member_list)}")
            
    except Exception as e:
        print(f"[错误] 处理群成员加入详情异常: {e}")