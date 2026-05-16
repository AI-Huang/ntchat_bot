"""
消息格式说明:

群消息格式 (type: 11046):
{
    'data': {
        'at_user_list': [],
        'from_wxid': '发送者wxid',
        'is_pc': 0,
        'msg': '消息内容',
        'msgid': '消息ID',
        'room_wxid': '群ID@chatroom',
        'timestamp': 时间戳,
        'to_wxid': '接收者ID',
        'wx_type': 1  # 1=文本消息
    },
    'type': 11046
}

联系人消息格式 (type: 11045):
{
    'data': {
        'from_wxid': '发送者wxid',
        'is_pc': 0,
        'msg': '消息内容',
        'msgid': '消息ID',
        'timestamp': 时间戳,
        'to_wxid': '自己的wxid',
        'wx_type': 1
    },
    'type': 11045
}

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

wx_type 类型说明:
- 1: 文本消息
- 3: 图片消息
- 34: 语音消息
- 43: 视频消息
- 47: 表情消息
- 49: 文件消息

message type 事件类型说明:
- 11045: 联系人消息
- 11046: 群消息
- 11032: 群成员列表事件
"""

import json

import ntchat

from src.ntchat_bot.services import DatabaseServiceFactory
from src.ntchat_bot.settings import DEBUG_MODE


def get_contact_info(wechat_instance, data, from_wxid): # 获取联系人信息
    contact_info = wechat_instance.get_contact_detail(from_wxid)

    if isinstance(contact_info, str):
        print(f"[警告] get_contact_detail 返回字符串: {contact_info}")
        contact_nickname = "未知"
        contact_remark = None
    elif isinstance(contact_info, dict):
        contact_nickname = contact_info.get("nickname", "未知")
        contact_remark = contact_info.get("remark")
    else:
        print(f"[警告] get_contact_detail 返回未知类型: {type(contact_info)}")
        contact_nickname = "未知"
        contact_remark = None

    return contact_nickname, contact_remark


def get_room_name(wechat_instance, room_wxid):  # 获取群名称
    room_info = wechat_instance.get_room_detail(room_wxid)

    if isinstance(room_info, str):
        print(f"[警告] get_room_detail 返回字符串: {room_info}")
        room_name = "未知群"
    elif isinstance(room_info, dict):
        room_name = room_info.get("nickname", "未知群")
    else:
        print(f"[警告] get_room_detail 返回未知类型: {type(room_info)}")
        room_name = "未知群"

    return room_name


def save_group_message(db, wechat_instance, data, room_wxid, msg_content):

    try:
        room_name = get_room_name(wechat_instance, room_wxid)
        print(
            f"[群消息详情] 群名称: {room_name}, 发送者: {data['from_wxid']}, 内容: {msg_content}"
        )

        contact_nickname, contact_remark = get_contact_info(
            wechat_instance, data, data["from_wxid"])
        db.insert_message(msg_id=data.get("msgid", ""),
                          from_wxid=data["from_wxid"],
                          to_wxid=data["to_wxid"],
                          content=msg_content,
                          wx_type=data.get("wx_type", 0),
                          type=data.get("type", 0),
                          room_wxid=room_wxid,
                          extra=json.dumps({
                              "room_name": room_name,
                              "contact_nickname": contact_nickname,
                              "contact_remark": contact_remark
                          }))

        return room_name, data["from_wxid"]
    except Exception as e:
        print(f"[错误] save_group_message 异常: {e}")
        raise




def save_contact_message(db, wechat_instance, data, self_wxid, msg_content):

    try:

        contact_nickname, contact_remark = get_contact_info(
            wechat_instance, data, data["from_wxid"])
        db.insert_contact(wxid=data["from_wxid"],
                          nickname=contact_nickname,
                          remark=contact_remark)

        print(f"[联系人消息详情] 联系人: {contact_nickname}, 内容: {msg_content}")

        db.insert_message(msg_id=data.get("msgid", ""),
                          from_wxid=data["from_wxid"],
                          to_wxid=data["to_wxid"],
                          content=msg_content,
                          wx_type=data.get("wx_type", 0),
                          extra=json.dumps(
                              {"contact_nickname": contact_nickname}))

        return contact_nickname
    except Exception as e:
        print(f"[错误] save_contact_message 异常: {e}")
        raise


def echo_group_message(wechat_instance, room_wxid, from_wxid, msg_content):
    wechat_instance.send_text(to_wxid=room_wxid, content=f"收到群 {room_wxid} 中的 {from_wxid} 发送的消息: {msg_content}")


def echo_contact_message(wechat_instance, from_wxid, msg_content):
    wechat_instance.send_text(to_wxid=from_wxid, content=f"你发送的消息是: {msg_content}")


def on_recv_text_msg(wechat_instance: ntchat.WeChat, message):
    try:
        data = message.get("data", {})

        if isinstance(data, str):
            print(f"[错误] data 是字符串类型，无法处理: {data}")
            return

        if not isinstance(data, dict):
            print(f"[错误] data 不是字典类型: {type(data)}")
            return

        from_wxid = data.get("from_wxid", "")
        if not from_wxid:
            print(f"[错误] 缺少 from_wxid: {data}")
            return

        msg_content = data.get("msg", "")
        if not msg_content:
            print(f"[错误] 缺少消息内容: {data}")
            return

        self_wxid = wechat_instance.get_login_info().get("wxid", "")
        if not self_wxid:
            print("[错误] 无法获取登录用户 wxid")
            return

        room_wxid = data.get("room_wxid", "")
        is_group = room_wxid != ""

        if from_wxid != self_wxid:
            db = DatabaseServiceFactory.get_service()

            if is_group:
                print(f"[群消息] 群ID: {room_wxid}, 发送者: {from_wxid}, 内容: {msg_content}")
                room_name, _ = save_group_message(db, wechat_instance, data, room_wxid, msg_content)
                if DEBUG_MODE:
                    echo_group_message(wechat_instance, room_wxid, from_wxid, msg_content)
            else:
                print(f"[联系人消息] 发送者: {from_wxid}, 内容: {msg_content}")
                _ = save_contact_message(db, wechat_instance, data, self_wxid, msg_content)
                if DEBUG_MODE:
                    echo_contact_message(wechat_instance, from_wxid, msg_content)
    except Exception as e:
        print(f"[错误] 处理消息时发生异常: {e}, message: {message}")