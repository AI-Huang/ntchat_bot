"""
群消息事件格式说明:

群成员列表事件 (type: 11032):
{
    'data': {
        'extend': '',
        'group_wxid': '群ID@chatroom',
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

群成员加入事件:
{
    'data': {
        'group_wxid': '群ID@chatroom',
        'op_wxid': '操作人wxid',
        'member_list': ['成员wxid1', '成员wxid2', ...]
    },
    'type': 群成员加入类型码
}

群成员退出事件:
{
    'data': {
        'group_wxid': '群ID@chatroom',
        'op_wxid': '操作人wxid',
        'member_list': ['成员wxid1', '成员wxid2', ...]
    },
    'type': 群成员退出类型码
}
"""


import ntchat

from src.ntchat_bot.services import SQLiteService


def on_room_member_list(wechat_instance: ntchat.WeChat, message):
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[警告] 群成员列表事件 data 是字符串: {data}")
            return
        
        if not isinstance(data, dict):
            print(f"[警告] 群成员列表事件 data 不是字典: {type(data)}")
            return
        
        group_wxid = data.get("group_wxid", "")
        if not group_wxid:
            print(f"[警告] 群成员列表事件缺少 group_wxid: {data}")
            return
        
        member_list = data.get("member_list", [])
        total = data.get("total", 0)
        
        print(f"[群成员列表] 群ID: {group_wxid}, 成员总数: {total}")
        
        db = SQLiteService()
        
        room_info = wechat_instance.get_room_detail(group_wxid)
        if isinstance(room_info, dict):
            room_name = room_info.get("nickname", "未知群")
        else:
            room_name = "未知群"
        
        db.insert_chatroom(group_wxid, room_name, total)
        
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
                            group_wxid=group_wxid,
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
    group_wxid = data["group_wxid"]
    op_wxid = data.get("op_wxid", "")
    member_list = data.get("member_list", [])
    
    room_name = wechat_instance.get_room_name(group_wxid)
    if not room_name:
        room_name = "未知群"
    
    print(f"[群成员加入] 群: {room_name}, 操作人: {op_wxid}, 新成员: {member_list}")


def on_room_del_member(wechat_instance: ntchat.WeChat, message):
    data = message["data"]
    group_wxid = data["group_wxid"]
    op_wxid = data.get("op_wxid", "")
    member_list = data.get("member_list", [])
    
    room_name = wechat_instance.get_room_name(group_wxid)
    if not room_name:
        room_name = "未知群"
    
    print(f"[群成员退出] 群: {room_name}, 操作人: {op_wxid}, 退出成员: {member_list}")