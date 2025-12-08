#!/bin/bash
# 全币数据统计系统停止脚本

cd /home/user/webapp

echo "=========================================="
echo "全币数据统计系统 - 停止脚本"
echo "=========================================="

# 停止API服务
if [ -f "coin_history_api.pid" ]; then
    API_PID=$(cat coin_history_api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        echo "🛑 停止API服务 (PID: $API_PID)..."
        kill $API_PID
        rm coin_history_api.pid
        echo "   ✅ API服务已停止"
    else
        echo "   ⚠️  API服务未运行"
        rm coin_history_api.pid
    fi
else
    echo "   ⚠️  找不到API PID文件"
fi

# 停止数据采集服务
if [ -f "coin_history_collector.pid" ]; then
    COLLECTOR_PID=$(cat coin_history_collector.pid)
    if kill -0 $COLLECTOR_PID 2>/dev/null; then
        echo "🛑 停止数据采集服务 (PID: $COLLECTOR_PID)..."
        kill $COLLECTOR_PID
        rm coin_history_collector.pid
        echo "   ✅ 采集服务已停止"
    else
        echo "   ⚠️  采集服务未运行"
        rm coin_history_collector.pid
    fi
else
    echo "   ⚠️  找不到采集服务 PID文件"
fi

echo ""
echo "✅ 全币数据统计系统已停止"
echo "=========================================="
