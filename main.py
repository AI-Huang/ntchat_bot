# -*- coding: utf-8 -*-
import sys
import time

import ntchat
from ntchat.const import notify_type

from src.ntchat_bot.handlers import (
    on_contact_info,
    on_forward_message,
    on_official_account_message,
    on_recv_card_msg,
    on_recv_emoji_msg,
    on_recv_file_msg,
    on_recv_friend_request,
    on_recv_image_msg,
    on_recv_link_msg,
    on_recv_location_msg,
    on_recv_revoke_msg,
    on_recv_text_msg,
    on_recv_video_msg,
    on_recv_voice_msg,
    on_room_add_member,
    on_room_del_member,
    on_room_invite_message,
    on_room_member_join_detail,
    on_room_member_list,
    on_room_member_update,
    on_user_login,
    on_user_logout,
)
from src.ntchat_bot.logger import get_logger
from src.ntchat_bot.registry import fetch_group_members_on_login
from src.ntchat_bot.settings import DEBUG_MODE

# 获取日志记录器
logger = get_logger(__name__)

wechat = ntchat.WeChat()
wechat.open(smart=False)

# 注册消息回调
wechat.msg_register(notify_type.MT_RECV_TEXT_MSG)(on_recv_text_msg)
wechat.msg_register(notify_type.MT_RECV_IMAGE_MSG)(on_recv_image_msg)
wechat.msg_register(notify_type.MT_RECV_VOICE_MSG)(on_recv_voice_msg)
wechat.msg_register(notify_type.MT_RECV_VIDEO_MSG)(on_recv_video_msg)
wechat.msg_register(notify_type.MT_RECV_EMOJI_MSG)(on_recv_emoji_msg)
wechat.msg_register(notify_type.MT_RECV_LOCATION_MSG)(on_recv_location_msg)
wechat.msg_register(notify_type.MT_RECV_LINK_MSG)(on_recv_link_msg)
wechat.msg_register(notify_type.MT_RECV_FILE_MSG)(on_recv_file_msg)
wechat.msg_register(notify_type.MT_RECV_CARD_MSG)(on_recv_card_msg)
wechat.msg_register(notify_type.MT_ROOM_ADD_MEMBER_NOTIFY_MSG)(on_room_add_member)
wechat.msg_register(notify_type.MT_ROOM_DEL_MEMBER_NOTIFY_MSG)(on_room_del_member)
wechat.msg_register(notify_type.MT_RECV_FRIEND_MSG)(on_recv_friend_request)
wechat.msg_register(notify_type.MT_RECV_REVOKE_MSG)(on_recv_revoke_msg)
wechat.msg_register(notify_type.MT_USER_LOGIN_MSG)(on_user_login)
wechat.msg_register(notify_type.MT_USER_LOGOUT_MSG)(on_user_logout)
# 注册群成员列表事件
wechat.msg_register(11032)(on_room_member_list)
# 注册联系人信息事件
wechat.msg_register(11029)(on_contact_info)

# 注册转发消息事件
wechat.msg_register(11061)(on_forward_message)
# 注册公众号推送消息事件 (type: 11054)
wechat.msg_register(11054)(on_official_account_message)

# 注册群邀请消息事件 (type: 11058)
wechat.msg_register(11058)(on_room_invite_message)
# 注册群成员列表更新事件 (type: 11200)
wechat.msg_register(11200)(on_room_member_update)
# 注册群成员加入详情事件 (type: 11098)
wechat.msg_register(11098)(on_room_member_join_detail)

try:
    # 等待登录成功
    print("等待微信登录...")
    while True:
        status = wechat.login_status
        if status:
            logger.info("微信登录成功")
            break
        time.sleep(1)
    
    # 仅在 DEBUG_MODE=True 时主动获取群成员列表
    if DEBUG_MODE:
        fetch_group_members_on_login(wechat)
    
    while True:
        time.sleep(1)
# except KeyboardInterrupt:
#     ntchat.exit_()
#     sys.exit()
except Exception as e:
    logger.error(f"发生异常: {e}")
    ntchat.exit_()