#!/usr/bin/env python3
"""
加密货币数据分析系统 - 完全仿照参考页面风格
"""
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# 主页面HTML - 完全仿照参考设计
MAIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币数据历史回看</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: #1e2139;
            color: #fff;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 0;
        }
        
        /* 顶部导航栏 */
        .top-nav {
            background: #2a2d47;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .nav-brand {
            display: flex;
            align-items: center;
            gap: 8px;
            background: #3b7dff;
            padding: 6px 15px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .nav-title {
            font-size: 18px;
            font-weight: 500;
            color: #fff;
            margin-left: 10px;
        }
        
        /* 控制栏 */
        .control-bar {
            background: #2a2d47;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
            border-bottom: 1px solid #3a3d5c;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-label {
            color: #8b92b8;
            font-size: 13px;
        }
        
        .control-input {
            background: #1e2139;
            border: 1px solid #3a3d5c;
            color: #fff;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 13px;
            outline: none;
        }
        
        .control-input:focus {
            border-color: #3b7dff;
        }
        
        .control-btn {
            background: #3b7dff;
            border: none;
            color: white;
            padding: 7px 18px;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .control-btn:hover {
            background: #2563eb;
        }
        
        .control-btn.secondary {
            background: #4a5178;
        }
        
        .control-btn.secondary:hover {
            background: #5a6188;
        }
        
        /* 数据统计栏 */
        .stats-bar {
            background: #2a2d47;
            padding: 12px 20px;
            display: flex;
            gap: 25px;
            flex-wrap: wrap;
            border-bottom: 1px solid #3a3d5c;
            font-size: 13px;
        }
        
        .stat-item {
            display: flex;
            gap: 5px;
        }
        
        .stat-label {
            color: #8b92b8;
        }
        
        .stat-value {
            color: #fff;
            font-weight: 500;
        }
        
        .stat-value.rise {
            color: #10b981;
        }
        
        .stat-value.fall {
            color: #ef4444;
        }
        
        /* 次级统计栏 */
        .secondary-stats {
            background: #1e2139;
            padding: 10px 20px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 13px;
        }
        
        /* 时间轴容器 - 竖直布局 */
        .timeline-container {
            background: #2a2d47;
            padding: 15px 20px;
            border-top: 1px solid #3a3d5c;
            max-height: 500px;  /* 增加高度以显示更多信息 */
            overflow-y: auto;
        }
        
        .timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            position: sticky;
            top: 0;
            background: #2a2d47;
            padding-bottom: 10px;
            border-bottom: 1px solid #3a3d5c;
        }
        
        .timeline-title {
            color: #8b92b8;
            font-size: 13px;
            font-weight: 500;
        }
        
        .timeline-info {
            color: #3b7dff;
            font-size: 12px;
        }
        
        /* 竖直时间轴轨道 */
        .timeline-track {
            position: relative;
            padding-left: 30px;
            margin-top: 10px;
        }
        
        /* 竖直线 */
        .timeline-line {
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #3a3d5c;
        }
        
        /* 竖直排列的时间点容器 */
        .timeline-points {
            display: flex;
            flex-direction: column;
            gap: 20px;  /* 增加间距以容纳更多信息 */
        }
        
        /* 时间点项 */
        .timeline-point {
            position: relative;
            display: flex;
            align-items: flex-start;  /* 改为顶部对齐，适应多行内容 */
            cursor: pointer;
            padding: 10px 12px;  /* 增加padding */
            border-radius: 4px;
            transition: all 0.3s;
            min-height: 80px;  /* 最小高度确保显示多行信息 */
        }
        
        .timeline-point:hover {
            background: rgba(59, 125, 255, 0.1);
        }
        
        /* 时间点圆圈 */
        .timeline-point::before {
            content: '';
            position: absolute;
            left: -22px;
            width: 12px;
            height: 12px;
            background: #3b7dff;
            border: 2px solid #2a2d47;
            border-radius: 50%;
            transition: all 0.3s;
            z-index: 2;
        }
        
        .timeline-point:hover::before {
            width: 16px;
            height: 16px;
            left: -24px;
            background: #2563eb;
            box-shadow: 0 0 10px rgba(59, 125, 255, 0.5);
        }
        
        .timeline-point.active::before {
            background: #10b981;
            width: 16px;
            height: 16px;
            left: -24px;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        }
        
        /* 时间标签 */
        .timeline-label {
            color: #8b92b8;
            font-size: 12px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .timeline-point:hover .timeline-label {
            color: #fff;
        }
        
        .timeline-point.active .timeline-label {
            color: #10b981;
            font-weight: 500;
        }
        
        .timeline-label-time {
            font-size: 13px;
            font-weight: 500;
        }
        
        .timeline-label-stats {
            font-size: 11px;
            opacity: 0.85;
            line-height: 1.5;
            color: #a0aec0;
            max-width: 600px;  /* 限制最大宽度 */
        }
        
        .timeline-label-stats div {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* 图表区域 */
        .chart-section {
            background: #2a2d47;
            margin: 0;
            padding: 20px;
        }
        
        .chart-title {
            color: #8b92b8;
            font-size: 14px;
            margin-bottom: 15px;
            text-align: center;
        }
        
        #mainChart {
            width: 100%;
            height: 450px;  /* 增加高度，让图表更清晰 */
        }
        
        /* 数据列表标题 */
        .data-list-header {
            background: #2a2d47;
            padding: 12px 20px;
            color: #3b7dff;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* 表格容器 */
        .table-container {
            background: #1e2139;
            overflow-x: auto;
        }
        
        /* 数据表格 */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        
        .data-table thead {
            background: #ef4444;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .data-table th {
            padding: 10px 8px;
            text-align: center;
            font-weight: 500;
            color: #fff;
            border-right: 1px solid #dc2626;
            white-space: nowrap;
        }
        
        .data-table tbody tr {
            border-bottom: 1px solid #2a2d47;
        }
        
        .data-table tbody tr:hover {
            background: #2a2d47;
        }
        
        .data-table td {
            padding: 8px 6px;
            text-align: center;
            border-right: 1px solid #2a2d47;
            white-space: nowrap;
        }
        
        /* 操作列 */
        .action-btn {
            background: #ef4444;
            border: none;
            color: white;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 11px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .action-btn:hover {
            background: #dc2626;
        }
        
        /* 币种名称 */
        .coin-symbol {
            font-weight: 600;
            color: #fff;
        }
        
        /* 数值颜色 */
        .value-positive {
            color: #ef4444;
        }
        
        .value-negative {
            color: #10b981;
        }
        
        .value-neutral {
            color: #8b92b8;
        }
        
        /* 状态标签 */
        .status-tag {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }
        
        .status-tag.rise {
            background: #dc2626;
            color: white;
        }
        
        .status-tag.fall {
            background: #10b981;
            color: white;
        }
        
        /* 优先级颜色 */
        .priority-1 { color: #ff0000; font-weight: bold; }
        .priority-2 { color: #ff6600; font-weight: bold; }
        .priority-3 { color: #ff9900; }
        .priority-4 { color: #ffcc00; }
        .priority-5 { color: #99cc00; }
        .priority-6 { color: #8b92b8; }
        
        /* 加载状态 */
        .loading {
            text-align: center;
            padding: 40px;
            color: #8b92b8;
            font-size: 14px;
        }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .control-bar {
                flex-direction: column;
                align-items: stretch;
            }
            
            .stats-bar {
                flex-direction: column;
                gap: 10px;
            }
            
            .data-table {
                font-size: 11px;
            }
            
            .data-table th,
            .data-table td {
                padding: 6px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部导航 -->
        <div class="top-nav">
            <div class="nav-brand">
                <span>📊</span> 数据回看
            </div>
            <div class="nav-title">加密货币数据历史回看</div>
        </div>
        
        <!-- 控制栏 -->
        <div class="control-bar">
            <div class="control-group">
                <span class="control-label">选项日期:</span>
                <input type="date" id="queryDate" class="control-input">
            </div>
            
            <div class="control-group">
                <span class="control-label">时间选择:</span>
                <input type="time" id="queryTime" class="control-input" value="00:00">
            </div>
            
            <div class="control-group">
                <span class="control-label">至</span>
                <input type="time" id="endTime" class="control-input" value="23:59">
            </div>
            
            <button class="control-btn" onclick="queryData()">🔍 查询</button>
            <button class="control-btn secondary" onclick="loadToday()">📊 今天</button>
            <button class="control-btn secondary" onclick="loadLatest()">📡 立即加载</button>
        </div>
        
        <!-- 主要统计栏 -->
        <div class="stats-bar">
            <div class="stat-item">
                <span class="stat-label">运算时间:</span>
                <span class="stat-value" id="calcTime">2025-12-06 13:42:42</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">急涨:</span>
                <span class="stat-value rise" id="rushUp">1</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">急跌:</span>
                <span class="stat-value fall" id="rushDown">22</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">本轮急涨:</span>
                <span class="stat-value" id="roundRushUp">1</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">本轮急跌:</span>
                <span class="stat-value" id="roundRushDown">22</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">计次:</span>
                <span class="stat-value" id="countTimes">10</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">计次得分:</span>
                <span class="stat-value" id="countScore">☆☆☆</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">状态:</span>
                <span class="stat-value" id="status">震荡无序</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">比值:</span>
                <span class="stat-value" id="ratio">10</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">差值:</span>
                <span class="stat-value" id="diff">-21</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">比价最低:</span>
                <span class="stat-value" id="priceLowest">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">比价创新高:</span>
                <span class="stat-value" id="priceNewhigh">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">24h涨≥10%:</span>
                <span class="stat-value rise" id="rise24hCount">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">24h跌≤-10%:</span>
                <span class="stat-value fall" id="fall24hCount">0</span>
            </div>
        </div>
        
        <!-- 次级统计栏 -->
        <div class="secondary-stats">
            <div class="stat-item">
                <span class="stat-label">已回调历史: 无</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">回调天数: 168 秒/0次</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">时间偏限: 2025-12-04 10:22:00 ~ 2025-12-04 18:32:00</span>
            </div>
        </div>
        
        <!-- 图表区域 -->
        <div class="chart-section">
            <div class="chart-title">急涨/急跌历史趋势图</div>
            <div id="mainChart"></div>
        </div>
        
        <!-- 时间轴 - 放在图表下方 -->
        <div class="timeline-container">
            <div class="timeline-header">
                <span class="timeline-title">历史数据时间轴</span>
                <span class="timeline-info" id="timelineInfo">加载中...</span>
            </div>
            <div class="timeline-track">
                <div class="timeline-line"></div>
                <div id="timelinePoints" class="timeline-points"></div>
            </div>
        </div>
        
        <!-- 数据列表标题 -->
        <div class="data-list-header">
            <span>📋</span> 币列表
        </div>
        
        <!-- 数据表格 -->
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>🎯操作</th>
                        <th>序号</th>
                        <th>币名</th>
                        <th>涨跌</th>
                        <th>急涨</th>
                        <th>急跌</th>
                        <th>更新时间</th>
                        <th>历史高点</th>
                        <th>高点时间</th>
                        <th>跌幅</th>
                        <th>24h%</th>
                        <th>--%</th>
                        <th>排行</th>
                        <th>当前价格</th>
                        <th>最高占比</th>
                        <th>最低占比</th>
                        <th>优先级</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody">
                    <tr>
                        <td colspan="17" class="loading">正在加载数据...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // 初始化图表
        const chart = echarts.init(document.getElementById('mainChart'));
        
        // 初始化日期
        const today = new Date();
        document.getElementById('queryDate').valueAsDate = today;
        
        // 图表配置
        function updateChart(data) {
            const option = {
                backgroundColor: 'transparent',
                grid: {
                    left: '50px',
                    right: '50px',
                    bottom: '60px',  // 增加底部空间给横轴标签
                    top: '50px',
                    containLabel: true
                },
                tooltip: {
                    trigger: 'item',  // 改为item触发，显示单个数据点
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    borderColor: '#3a3d5c',
                    borderWidth: 1,
                    textStyle: { color: '#fff', fontSize: 12 },
                    formatter: function(params) {
                        const seriesName = params.seriesName;
                        const time = data.times[params.dataIndex];
                        const value = params.value;
                        return `<div style="padding: 5px;">
                            <div style="font-weight: bold; margin-bottom: 5px;">${time}</div>
                            <div>${seriesName}: <span style="color: ${params.color}; font-weight: bold;">${value}</span></div>
                        </div>`;
                    }
                },
                legend: {
                    data: ['急涨', '急跌', '差值(急涨-急跌)', '计次'],
                    top: 10,
                    left: 'center',
                    textStyle: { color: '#8b92b8', fontSize: 13 },
                    itemWidth: 30,
                    itemHeight: 14,
                    itemGap: 20
                },
                xAxis: {
                    type: 'category',
                    data: data.times || [],
                    axisLine: { 
                        lineStyle: { color: '#3a3d5c', width: 1 }
                    },
                    axisLabel: { 
                        color: '#8b92b8',
                        fontSize: 11,
                        rotate: 0,  // 不旋转，水平显示
                        interval: 0,  // 显示所有标签
                        margin: 10
                    },
                    axisTick: {
                        show: true,
                        lineStyle: { color: '#3a3d5c' }
                    },
                    splitLine: { show: false }
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '数量',
                        nameTextStyle: { 
                            color: '#8b92b8', 
                            fontSize: 12,
                            padding: [0, 0, 0, 10]
                        },
                        axisLine: { 
                            show: true,
                            lineStyle: { color: '#3a3d5c' } 
                        },
                        axisLabel: { 
                            color: '#8b92b8', 
                            fontSize: 11 
                        },
                        splitLine: { 
                            lineStyle: { 
                                color: '#3a3d5c', 
                                type: 'dashed',
                                opacity: 0.5
                            } 
                        }
                    },
                    {
                        type: 'value',
                        name: '计次',
                        nameTextStyle: { 
                            color: '#3b7dff', 
                            fontSize: 12,
                            padding: [0, 10, 0, 0]
                        },
                        axisLine: { 
                            show: true,
                            lineStyle: { color: '#3a3d5c' } 
                        },
                        axisLabel: { 
                            color: '#3b7dff', 
                            fontSize: 11 
                        },
                        splitLine: { show: false }
                    }
                ],
                series: [
                    {
                        name: '急涨',
                        type: 'line',
                        data: data.rush_up || [],
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#ef4444'
                        },
                        itemStyle: { 
                            color: '#ef4444',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    },
                    {
                        name: '急跌',
                        type: 'line',
                        data: data.rush_down || [],
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#10b981'
                        },
                        itemStyle: { 
                            color: '#10b981',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    },
                    {
                        name: '差值(急涨-急跌)',
                        type: 'line',
                        data: data.diff || [],
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#fbbf24'
                        },
                        itemStyle: { 
                            color: '#fbbf24',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    },
                    {
                        name: '计次',
                        type: 'line',
                        yAxisIndex: 1,
                        data: data.count || [],
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#3b7dff'
                        },
                        itemStyle: { 
                            color: '#3b7dff',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    }
                ]
            };
            
            chart.setOption(option);
        }
        
        // 查询数据
        function queryData() {
            const date = document.getElementById('queryDate').value;
            const time = document.getElementById('queryTime').value;
            const datetime = date + ' ' + time;
            
            fetch('/api/query?time=' + encodeURIComponent(datetime))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('❌ ' + data.error);
                        return;
                    }
                    updateUI(data);
                    loadChartData();  // 加载所有历史数据趋势图
                })
                .catch(error => {
                    alert('查询失败: ' + error);
                });
        }
        
        // 加载今天
        function loadToday() {
            const today = new Date();
            document.getElementById('queryDate').valueAsDate = today;
            queryData();
        }
        
        // 加载最新
        function loadLatest() {
            fetch('/api/latest')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('❌ ' + data.error);
                        return;
                    }
                    updateUI(data);
                    loadChartData();  // 加载所有历史数据趋势图
                })
                .catch(error => {
                    alert('加载失败: ' + error);
                });
        }
        
        // 更新UI
        function updateUI(data) {
            document.getElementById('calcTime').textContent = data.snapshot_time;
            document.getElementById('rushUp').textContent = data.rush_up;
            document.getElementById('rushDown').textContent = data.rush_down;
            document.getElementById('roundRushUp').textContent = data.round_rush_up || data.rush_up;
            document.getElementById('roundRushDown').textContent = data.round_rush_down || data.rush_down;
            document.getElementById('countTimes').textContent = data.count;
            document.getElementById('countScore').textContent = data.count_score_display || '---';
            document.getElementById('status').textContent = data.status;
            document.getElementById('ratio').textContent = data.ratio;
            document.getElementById('diff').textContent = data.diff;
            document.getElementById('priceLowest').textContent = data.price_lowest || 0;
            document.getElementById('priceNewhigh').textContent = data.price_newhigh || 0;
            document.getElementById('rise24hCount').textContent = data.rise_24h_count || 0;
            document.getElementById('fall24hCount').textContent = data.fall_24h_count || 0;
            
            // 更新表格
            const tbody = document.getElementById('dataTableBody');
            if (data.coins && data.coins.length > 0) {
                let html = '';
                data.coins.forEach((coin, idx) => {
                    const changeClass = coin.change > 0 ? 'value-positive' : (coin.change < 0 ? 'value-negative' : 'value-neutral');
                    const change24Class = coin.change_24h > 0 ? 'value-positive' : (coin.change_24h < 0 ? 'value-negative' : 'value-neutral');
                    const priorityClass = 'priority-' + coin.priority.replace('等级', '');
                    
                    const rushUpTag = coin.rush_up > 0 ? '<span class="status-tag rise">' + coin.rush_up + '</span>' : coin.rush_up;
                    const rushDownTag = coin.rush_down > 0 ? '<span class="status-tag fall">' + coin.rush_down + '</span>' : coin.rush_down;
                    
                    html += '<tr>';
                    html += '<td><button class="action-btn">管理</button></td>';
                    html += '<td>' + (idx + 1) + '</td>';
                    html += '<td class="coin-symbol">' + coin.symbol + '</td>';
                    html += '<td class="' + changeClass + '">' + coin.change.toFixed(2) + '</td>';
                    html += '<td>' + rushUpTag + '</td>';
                    html += '<td>' + rushDownTag + '</td>';
                    html += '<td>' + coin.update_time + '</td>';
                    html += '<td>' + coin.high_price.toFixed(2) + '</td>';
                    html += '<td>' + coin.high_time + '</td>';
                    html += '<td class="value-negative">' + coin.decline.toFixed(2) + '</td>';
                    html += '<td class="' + change24Class + '">' + coin.change_24h.toFixed(2) + '</td>';
                    html += '<td>--</td>';
                    html += '<td>' + coin.rank + '</td>';
                    html += '<td>' + coin.current_price.toFixed(4) + '</td>';
                    html += '<td>' + coin.ratio1 + '</td>';
                    html += '<td>' + coin.ratio2 + '</td>';
                    html += '<td class="' + priorityClass + '">' + coin.priority + '</td>';
                    html += '</tr>';
                });
                tbody.innerHTML = html;
            } else {
                tbody.innerHTML = '<tr><td colspan="17" class="loading">暂无数据</td></tr>';
            }
        }
        
        // 加载图表数据
        function loadChartData() {
            // 加载所有历史数据点用于趋势图
            fetch('/api/chart')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                        return;
                    }
                    updateChart(data);
                })
                .catch(error => {
                    console.error('图表加载失败:', error);
                });
        }
        
        // 页面加载时自动加载最新数据
        // 加载时间轴数据 - 竖直布局
        function loadTimeline() {
            fetch('/api/timeline')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('timelineInfo').textContent = data.error;
                        return;
                    }
                    
                    document.getElementById('timelineInfo').textContent = 
                        `共 ${data.snapshots.length} 个数据点`;
                    
                    const pointsContainer = document.getElementById('timelinePoints');
                    pointsContainer.innerHTML = '';
                    
                    // 时间从上到下：最早的在上面，最新的在下面
                    data.snapshots.forEach((snapshot, index) => {
                        const point = document.createElement('div');
                        point.className = 'timeline-point';
                        point.setAttribute('data-time', snapshot.snapshot_time);
                        
                        // 最后一个（最新的）标记为激活
                        if (index === data.snapshots.length - 1) {
                            point.classList.add('active');
                        }
                        
                        const label = document.createElement('div');
                        label.className = 'timeline-label';
                        
                        // 时间显示
                        const timeSpan = document.createElement('div');
                        timeSpan.className = 'timeline-label-time';
                        timeSpan.textContent = snapshot.snapshot_time;
                        
                        // 统计信息显示 - 显示所有关键字段
                        const statsSpan = document.createElement('div');
                        statsSpan.className = 'timeline-label-stats';
                        
                        // 第一行：急涨、急跌、计次、得分
                        const line1 = `急涨:${snapshot.rush_up} 急跌:${snapshot.rush_down} 计次:${snapshot.count} ${snapshot.count_score_display || ''}`;
                        
                        // 第二行：状态、比值、差值
                        const line2 = `状态:${snapshot.status || ''} 比值:${snapshot.ratio || 0} 差值:${snapshot.diff}`;
                        
                        // 第三行：本轮、比价、24h
                        const line3 = `本轮急涨:${snapshot.round_rush_up || 0} 本轮急跌:${snapshot.round_rush_down || 0} 24h涨≥10%:${snapshot.rise_24h_count || 0} 24h跌≤-10%:${snapshot.fall_24h_count || 0}`;
                        
                        statsSpan.innerHTML = `
                            <div style="margin-bottom: 2px;">${line1}</div>
                            <div style="margin-bottom: 2px;">${line2}</div>
                            <div>${line3}</div>
                        `;
                        
                        label.appendChild(timeSpan);
                        label.appendChild(statsSpan);
                        point.appendChild(label);
                        
                        point.onclick = function() {
                            // 移除所有激活状态
                            document.querySelectorAll('.timeline-point').forEach(p => {
                                p.classList.remove('active');
                            });
                            // 激活当前点
                            this.classList.add('active');
                            // 加载数据
                            loadSnapshotData(snapshot.snapshot_time);
                        };
                        
                        pointsContainer.appendChild(point);
                    });
                })
                .catch(error => {
                    console.error('加载时间轴失败:', error);
                    document.getElementById('timelineInfo').textContent = '加载失败';
                });
        }
        
        // 加载指定快照的数据
        function loadSnapshotData(snapshotTime) {
            fetch('/api/query?time=' + encodeURIComponent(snapshotTime))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    updateUI(data);
                    updateChart(data);
                    
                    // 更新时间轴激活状态
                    document.querySelectorAll('.timeline-point').forEach(point => {
                        point.classList.remove('active');
                    });
                    event.target.classList.add('active');
                })
                .catch(error => console.error('加载数据失败:', error));
        }
        
        window.onload = function() {
            loadLatest();
            loadTimeline();
        };
        
        // 响应式调整
        window.addEventListener('resize', function() {
            chart.resize();
        });
    </script>
</body>
</html>
"""

# API路由保持不变，使用之前的代码
@app.route('/')
def index():
    """主页面"""
    return render_template_string(MAIN_HTML)

@app.route('/api/query')
def api_query():
    """查询API"""
    query_time = request.args.get('time', '')
    if not query_time:
        return jsonify({'error': '请提供查询时间'})
    
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, count_score_type, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            WHERE snapshot_time LIKE ?
            ORDER BY snapshot_time DESC
            LIMIT 1
        """, (f"{query_time}%",))
        
        snapshot = cursor.fetchone()
        
        if not snapshot:
            conn.close()
            return jsonify({'error': f'未找到 {query_time} 的数据'})
        
        (snapshot_time, rush_up, rush_down, diff, count, ratio, status,
         round_rush_up, round_rush_down, price_lowest, price_newhigh,
         count_score_display, count_score_type, rise_24h_count, fall_24h_count) = snapshot
        
        cursor.execute("""
            SELECT 
                symbol, change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h, rank,
                current_price, ratio1, ratio2, priority_level
            FROM crypto_coin_data
            WHERE snapshot_time = ?
            ORDER BY index_order ASC
        """, (snapshot_time,))
        
        coins = []
        for row in cursor.fetchall():
            coins.append({
                'symbol': row[0],
                'change': row[1],
                'rush_up': row[2],
                'rush_down': row[3],
                'update_time': row[4],
                'high_price': row[5],
                'high_time': row[6],
                'decline': row[7],
                'change_24h': row[8],
                'rank': row[9],
                'current_price': row[10],
                'ratio1': row[11],
                'ratio2': row[12],
                'priority': row[13]
            })
        
        conn.close()
        
        return jsonify({
            'snapshot_time': snapshot_time,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count,
            'ratio': ratio,
            'status': status,
            'round_rush_up': round_rush_up,
            'round_rush_down': round_rush_down,
            'price_lowest': price_lowest,
            'price_newhigh': price_newhigh,
            'count_score_display': count_score_display,
            'count_score_type': count_score_type,
            'rise_24h_count': rise_24h_count,
            'fall_24h_count': fall_24h_count,
            'coins': coins
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/latest')
def api_latest():
    """获取最新数据API"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, count_score_type, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            ORDER BY snapshot_time DESC
            LIMIT 1
        """)
        
        snapshot = cursor.fetchone()
        
        if not snapshot:
            conn.close()
            return jsonify({'error': '数据库中暂无数据'})
        
        (snapshot_time, rush_up, rush_down, diff, count, ratio, status,
         round_rush_up, round_rush_down, price_lowest, price_newhigh,
         count_score_display, count_score_type, rise_24h_count, fall_24h_count) = snapshot
        
        cursor.execute("""
            SELECT 
                symbol, change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h, rank,
                current_price, ratio1, ratio2, priority_level
            FROM crypto_coin_data
            WHERE snapshot_time = ?
            ORDER BY index_order ASC
        """, (snapshot_time,))
        
        coins = []
        for row in cursor.fetchall():
            coins.append({
                'symbol': row[0],
                'change': row[1],
                'rush_up': row[2],
                'rush_down': row[3],
                'update_time': row[4],
                'high_price': row[5],
                'high_time': row[6],
                'decline': row[7],
                'change_24h': row[8],
                'rank': row[9],
                'current_price': row[10],
                'ratio1': row[11],
                'ratio2': row[12],
                'priority': row[13]
            })
        
        conn.close()
        
        return jsonify({
            'snapshot_time': snapshot_time,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count,
            'ratio': ratio,
            'status': status,
            'round_rush_up': round_rush_up,
            'round_rush_down': round_rush_down,
            'price_lowest': price_lowest,
            'price_newhigh': price_newhigh,
            'count_score_display': count_score_display,
            'count_score_type': count_score_type,
            'rise_24h_count': rise_24h_count,
            'fall_24h_count': fall_24h_count,
            'coins': coins
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/chart')
def api_chart():
    """图表数据API - 返回所有历史数据点用于趋势图"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取所有历史数据点，按时间升序排列
        cursor.execute("""
            SELECT 
                snapshot_time, rush_up, rush_down, diff, count
            FROM crypto_snapshots
            ORDER BY snapshot_time ASC
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return jsonify({'error': '无数据'})
        
        # 格式化时间标签：短格式（月-日 时:分）
        times = []
        for row in data:
            dt_str = row[0]  # 例如：'2025-12-05 14:27:33'
            # 提取月-日 时:分
            parts = dt_str.split(' ')
            date_parts = parts[0].split('-')  # ['2025', '12', '05']
            time_parts = parts[1].split(':')  # ['14', '27', '33']
            formatted_time = f"{date_parts[1]}-{date_parts[2]} {time_parts[0]}:{time_parts[1]}"
            times.append(formatted_time)
        
        rush_up = [row[1] for row in data]
        rush_down = [row[2] for row in data]
        diff = [row[3] for row in data]
        count = [row[4] for row in data]
        
        return jsonify({
            'times': times,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/timeline')
def api_timeline():
    """获取所有历史数据点API - 返回完整的统计数据"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 查询所有字段 - 倒序排列（时间晚的在上，时间早的在下）
        cursor.execute("""
            SELECT 
                id, snapshot_time, snapshot_date,
                rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down,
                price_lowest, price_newhigh, ratio_diff,
                init_rush_up, init_rush_down,
                count_score_display, count_score_type,
                rise_24h_count, fall_24h_count,
                green_count, percentage, filename
            FROM crypto_snapshots
            ORDER BY snapshot_time DESC
        """)
        
        snapshots = []
        for row in cursor.fetchall():
            snapshots.append({
                'id': row[0],
                'snapshot_time': row[1],
                'snapshot_date': row[2],
                # 主要统计
                'rush_up': row[3],
                'rush_down': row[4],
                'diff': row[5],
                'count': row[6],
                'ratio': row[7],
                'status': row[8],
                # 本轮数据
                'round_rush_up': row[9],
                'round_rush_down': row[10],
                # 比价数据
                'price_lowest': row[11],
                'price_newhigh': row[12],
                'ratio_diff': row[13],
                # 初始数据
                'init_rush_up': row[14],
                'init_rush_down': row[15],
                # 计次得分
                'count_score_display': row[16],
                'count_score_type': row[17],
                # 24小时涨跌
                'rise_24h_count': row[18],
                'fall_24h_count': row[19],
                # 其他
                'green_count': row[20],
                'percentage': row[21],
                'filename': row[22]
            })
        
        conn.close()
        
        return jsonify({
            'snapshots': snapshots,
            'total': len(snapshots)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
