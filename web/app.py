import os

# 添加项目路径到 Python 路径
import sys
from typing import Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ntchat_bot.services import DatabaseServiceFactory

app = FastAPI(title="WeChat Bot Message Statistics", description="消息统计 API")

# 配置模板路径
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

@app.get("/", response_class=HTMLResponse, tags=["首页"])
async def index(request: Request):
    """首页，展示消息统计图表"""
    template_path = os.path.join(templates_dir, "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/api/messages/minute", response_model=List[Dict], tags=["消息统计"])
async def get_messages_per_minute(
    hours: Optional[int] = Query(24, description="查询最近多少小时的数据"),
    start_time: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD HH:MM:SS)")
):
    """获取每分钟消息数量统计"""
    db = DatabaseServiceFactory.get_service()
    
    if start_time and end_time:
        sql = '''
            SELECT 
                DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:00') as minute,
                COUNT(*) as count
            FROM messages
            WHERE create_time >= %s AND create_time <= %s
            GROUP BY minute
            ORDER BY minute
        '''
        data = db.fetch_all(sql, (start_time, end_time))
    else:
        sql = '''
            SELECT 
                DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:00') as minute,
                COUNT(*) as count
            FROM messages
            WHERE create_time >= NOW() - INTERVAL %s HOUR
            GROUP BY minute
            ORDER BY minute
        '''
        data = db.fetch_all(sql, (hours,))
    
    return [{"minute": row['minute'], "count": row['count']} for row in data]

@app.get("/api/messages/hour", response_model=List[Dict], tags=["消息统计"])
async def get_messages_per_hour(
    days: Optional[int] = Query(7, description="查询最近多少天的数据"),
    start_time: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD HH:MM:SS)")
):
    """获取每小时消息数量统计"""
    db = DatabaseServiceFactory.get_service()
    
    if start_time and end_time:
        sql = '''
            SELECT 
                DATE_FORMAT(create_time, '%Y-%m-%d %H:00:00') as hour,
                COUNT(*) as count
            FROM messages
            WHERE create_time >= %s AND create_time <= %s
            GROUP BY hour
            ORDER BY hour
        '''
        data = db.fetch_all(sql, (start_time, end_time))
    else:
        sql = '''
            SELECT 
                DATE_FORMAT(create_time, '%Y-%m-%d %H:00:00') as hour,
                COUNT(*) as count
            FROM messages
            WHERE create_time >= NOW() - INTERVAL %s DAY
            GROUP BY hour
            ORDER BY hour
        '''
        data = db.fetch_all(sql, (days,))
    
    return [{"hour": row['hour'], "count": row['count']} for row in data]

@app.get("/api/messages/total", response_model=Dict, tags=["消息统计"])
async def get_total_messages():
    """获取消息总数和今日消息数"""
    db = DatabaseServiceFactory.get_service()
    
    total_sql = "SELECT COUNT(*) as total FROM messages"
    total_result = db.fetch_one(total_sql)
    total = total_result['total'] if total_result else 0
    
    today_sql = "SELECT COUNT(*) as today FROM messages WHERE DATE(create_time) = CURDATE()"
    today_result = db.fetch_one(today_sql)
    today = today_result['today'] if today_result else 0
    
    return {"total": total, "today": today}

@app.get("/api/messages/group", response_model=List[Dict], tags=["消息统计"])
async def get_messages_by_group(
    limit: Optional[int] = Query(10, description="返回前 N 个群聊")
):
    """获取群聊消息排行"""
    db = DatabaseServiceFactory.get_service()
    
    sql = '''
        SELECT 
            r.room_wxid,
            r.name as room_name,
            COUNT(*) as message_count
        FROM messages m
        LEFT JOIN rooms r ON m.room_wxid = r.room_wxid
        WHERE m.room_wxid IS NOT NULL
        GROUP BY m.room_wxid, r.name
        ORDER BY message_count DESC
        LIMIT %s
    '''
    data = db.fetch_all(sql, (limit,))
    
    return [{"room_wxid": row['room_wxid'], "room_name": row['room_name'], "message_count": row['message_count']} for row in data]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)