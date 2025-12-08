#!/bin/bash
# 全币数据统计系统启动脚本

cd /home/user/webapp

echo "=========================================="
echo "全币数据统计系统 - 启动脚本"
echo "=========================================="

# 检查数据库是否存在
if [ ! -f "coin_history_stats.db" ]; then
    echo "📊 初始化数据库..."
    python3 create_history_stats_db.py
fi

# 启动API服务（后台运行）
echo "🚀 启动API服务 (端口5001)..."
nohup python3 coin_history_api.py > coin_history_api.log 2>&1 &
API_PID=$!
echo $API_PID > coin_history_api.pid
echo "   API PID: $API_PID"

# 等待API启动
sleep 2

# 启动数据采集服务（后台运行）
echo "📡 启动数据采集服务 (每分钟采集)..."
nohup python3 coin_history_collector.py > coin_history_collector.log 2>&1 &
COLLECTOR_PID=$!
echo $COLLECTOR_PID > coin_history_collector.pid
echo "   采集服务 PID: $COLLECTOR_PID"

echo ""
echo "✅ 全币数据统计系统启动成功！"
echo "=========================================="
echo "服务状态:"
echo "  API服务: http://localhost:5001"
echo "  数据采集: 每60秒一次"
echo ""
echo "查看日志:"
echo "  tail -f coin_history_api.log"
echo "  tail -f coin_history_collector.log"
echo ""
echo "停止服务:"
echo "  ./stop_history_system.sh"
echo "=========================================="
