"""可选启动函数注册中心

此模块存放仅在特定条件下执行的可选启动函数，如调试功能、测试功能等。
这些函数通过配置项（如 DEBUG_MODE）控制是否启用。
"""

from src.ntchat_bot.handlers.room_handler import on_room_member_list
from src.ntchat_bot.logger import get_logger, log_group_members
from src.ntchat_bot.settings import TEST_GROUP_ID

logger = get_logger(__name__)


def fetch_group_members_on_login(wechat_instance, room_id: str = None):
    """登录成功后主动获取指定群的成员列表

    此函数用于调试和测试，通常在 DEBUG_MODE=True 时启用。
    获取的成员列表会保存到日志文件中，并插入数据库。

    Args:
        wechat_instance: ntchat.WeChat 实例
        room_id: 要获取成员列表的群ID，默认为配置文件中的 TEST_GROUP_ID
    """
    # 使用配置文件中的 TEST_GROUP_ID 作为默认值
    if room_id is None:
        room_id = TEST_GROUP_ID

    if not room_id:
        logger.warning("TEST_GROUP_ID 未配置，跳过获取群成员列表")
        return

    try:
        logger.info(f"正在获取群 {room_id} 的成员列表...")
        members = wechat_instance.get_room_members(room_id)

        # 记录 members 变量类型和内容到日志
        logger.debug(f"members 类型: {type(members)}")
        logger.debug(f"members 内容: {members}")

        # 记录成员列表到日志文件
        log_group_members(members, room_id)

        if members:
            member_count = len(members) if isinstance(members, list) else members.get("total", 0)
            logger.info(f"获取成功，成员总数: {member_count}")
            # 构造事件消息格式，调用处理函数
            event_message = {
                "data": {
                    "group_wxid": room_id,
                    "member_list": members if isinstance(members, list) else members.get("member_list", []),
                    "total": member_count,
                    "extend": ""
                },
                "extend": "",
                "type": 11032
            }
            on_room_member_list(wechat_instance, event_message)
        else:
            logger.warning("获取失败")
    except Exception as e:
        logger.error(f"主动获取群成员列表失败: {e}")