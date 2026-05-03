# -*- coding: utf-8 -*-
import sys

import ntchat
from ntchat.const import notify_type

from src.ntchat_bot.handlers import (
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
    on_user_login,
    on_user_logout,
)

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

try:
    while True:
        pass
except KeyboardInterrupt:
    ntchat.exit_()
    sys.exit()