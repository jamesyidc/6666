#!/bin/bash
# 全币数据统计系统 - 启动脚本

echo "============================================================"
echo "全币数据统计系统 - 启动脚本"
echo "============================================================"

cd /home/user/webapp

# 检查数据库是否存在
if [ ! -f "coin_history_stats.db" ]; then
    echo "❌ 数据库不存在，正在创建..."
    python3 create_history_stats_db.py
fi

# 检查并启动API服务（端口5002）
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ API服务已在运行 (端口5002)"
else
    echo "🚀 启动API服务 (端口5002)..."
    nohup python3 coin_history_api.py > api_service.log 2>&1 &
    API_PID=$!
    sleep 2
    if ps -p $API_PID > /dev/null; then
        echo "✅ API服务已启动 (PID: $API_PID)"
    else
        echo "❌ API服务启动失败，查看日志: api_service.log"
    fi
fi

# 检查并启动数据采集服务
if pgrep -f "coin_history_collector.py" > /dev/null; then
    echo "✅ 数据采集服务已在运行"
else
    echo "🚀 启动数据采集服务 (1分钟间隔)..."
    nohup python3 coin_history_collector.py > coin_collector.log 2>&1 &
    COLLECTOR_PID=$!
    sleep 2
    if ps -p $COLLECTOR_PID > /dev/null; then
        echo "✅ 数据采集服务已启动 (PID: $COLLECTOR_PID)"
    else
        echo "❌ 数据采集服务启动失败，查看日志: coin_collector.log"
    fi
fi

echo ""
echo "============================================================"
echo "🎉 全币数据统计系统已启动"
echo "============================================================"
echo "📊 API服务地址: http://localhost:5002"
echo "🌐 公网访问地址: https://5002-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai"
echo "📈 前端页面: http://localhost:3000/coin_history_viewer.html"
echo ""
echo "📝 日志文件:"
echo "  - API服务: api_service.log"
echo "  - 数据采集: coin_collector.log"
echo ""
echo "🔍 查看运行状态:"
echo "  - ps aux | grep 'coin_history_api\\|coin_history_collector'"
echo ""
echo "🛑 停止服务:"
echo "  - pkill -f coin_history_api.py"
echo "  - pkill -f coin_history_collector.py"
echo "============================================================"
