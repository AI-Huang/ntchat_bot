"""
联系人信息事件格式 (type: 11029):
{
    'data': {
        'account': '微信号（可能为空）',
        'avatar': '头像URL',
        'city': '城市',
        'country': '国家代码（如 CN=中国）',
        'nickname': '昵称',
        'province': '省份',
        'remark': '备注名（可能为空）',
        'sex': 1,  # 1=男, 2=女
        'wxid': '用户唯一标识'
    },
    'extend': 'UUID',
    'type': 11029
}

字段说明:
- type: 事件类型标识，11029 表示联系人信息事件
- extend: UUID 扩展字段，用于追踪请求
- data.account: 用户微信号，可能为空字符串
- data.avatar: 头像图片的URL地址
- data.city: 用户所在城市
- data.country: 国家代码（ISO 3166-1 alpha-2）
- data.nickname: 用户昵称
- data.province: 用户所在省份
- data.remark: 备注名称，为空表示没有备注
- data.sex: 性别，1表示男，2表示女
- data.wxid: 用户的微信唯一标识，用于区分不同用户

触发场景:
1. 调用 get_contact_detail(wxid) 获取联系人详情时
2. 新好友添加成功后自动同步信息
3. 微信登录后系统自动同步联系人列表
"""

import ntchat

from src.ntchat_bot.services import SQLiteService


def on_contact_info(wechat_instance: ntchat.WeChat, message):
    """处理联系人信息事件"""
    try:
        data = message.get("data", {})
        
        if isinstance(data, str):
            print(f"[错误] 联系人信息事件 data 是字符串类型: {data}")
            return
        
        if not isinstance(data, dict):
            print(f"[错误] 联系人信息事件 data 不是字典类型: {type(data)}")
            return
        
        wxid = data.get("wxid")
        if not wxid:
            print(f"[错误] 联系人信息事件缺少 wxid: {data}")
            return
        
        nickname = data.get("nickname", "")
        remark = data.get("remark", "")
        avatar = data.get("avatar", "")
        city = data.get("city", "")
        province = data.get("province", "")
        country = data.get("country", "")
        sex = data.get("sex", 0)
        
        print(f"[联系人信息] wxid: {wxid}, 昵称: {nickname}, 备注: {remark}")
        
        # 保存到数据库
        db = SQLiteService()
        db.insert_contact(
            wxid=wxid,
            account=data.get("account", ""),
            nickname=nickname,
            remark=remark,
            avatar=avatar,
            city=city,
            province=province,
            country=country,
            sex=sex
        )
        
    except Exception as e:
        print(f"[错误] 处理联系人信息事件异常: {e}, message: {message}")