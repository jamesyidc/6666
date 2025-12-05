#!/usr/bin/env python3
"""
加密货币数据服务器 - 演示版本
使用模拟数据，不需要Google Drive API
用于测试和演示界面
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from datetime import datetime
import pytz
from crypto_database import CryptoDatabase
from monitor_data_reader import MonitorDataReader
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__, static_folder='.')
CORS(app)

# 初始化数据库
db = CryptoDatabase()

# 初始化监控数据读取器
monitor_reader = MonitorDataReader()

# 初始化后台调度器
scheduler = BackgroundScheduler()

def collect_monitoring_data():
    """
    定时采集监控数据（每10分钟执行一次）
    此函数独立于网页刷新运行
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始采集监控数据...")
        
        # 读取信号数据
        signal_data = monitor_reader.get_signal_data()
        if signal_data:
            db.save_signal_data(signal_data)
            print(f"✅ 信号数据已保存: 急跌={signal_data['short']}, 急涨={signal_data['long']}")
        
        # 读取恐慌清洗数据
        panic_data = monitor_reader.get_panic_data()
        if panic_data:
            db.save_panic_data(panic_data)
            print(f"✅ 恐慌数据已保存: 指标={panic_data['panic_indicator']}")
            
    except Exception as e:
        print(f"❌ 采集数据失败: {e}")

# 模拟数据（基于您提供的截图 - 完整29个币种）
DEMO_DATA = [
    {'index': '1', 'symbol': 'BTC', 'change': '0.2', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '126259.48', 'highTime': '2025-10-07', 'decline': '-31.16', 'change24h': '0.13', 'col10': '', 'col11': '', 'col12': '', 'rank': '12', 'currentPrice': '86500.4', 'ratio1': '69%', 'ratio2': '106.32%'},
    {'index': '2', 'symbol': 'ETH', 'change': '0.25', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '4954.59', 'highTime': '2025-08-25', 'decline': '-43.4', 'change24h': '-1.41', 'col10': '', 'col11': '', 'col12': '', 'rank': '21', 'currentPrice': '2792.22254', 'ratio1': '57.81%', 'ratio2': '105.69%'},
    {'index': '3', 'symbol': 'XRP', 'change': '0.33', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '3.8419', 'highTime': '2018-01-04', 'decline': '-47.49', 'change24h': '-1.48', 'col10': '', 'col11': '', 'col12': '', 'rank': '23', 'currentPrice': '2.00863', 'ratio1': '62.96%', 'ratio2': '109.18%'},
    {'index': '4', 'symbol': 'BNB', 'change': '0.11', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '1372.88', 'highTime': '2025-10-13', 'decline': '-39.12', 'change24h': '1.33', 'col10': '', 'col11': '', 'col12': '', 'rank': '4', 'currentPrice': '832.26901', 'ratio1': '60.42%', 'ratio2': '104.45%'},
    {'index': '5', 'symbol': 'SOL', 'change': '0.21', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '294.91', 'highTime': '2025-01-19', 'decline': '-56.95', 'change24h': '-0.2', 'col10': '', 'col11': '', 'col12': '', 'rank': '14', 'currentPrice': '126.41408', 'ratio1': '49.9%', 'ratio2': '102.87%'},
    {'index': '6', 'symbol': 'LTC', 'change': '0.18', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '413.2', 'highTime': '2021-05-10', 'decline': '-81.13', 'change24h': '0.16', 'col10': '', 'col11': '', 'col12': '', 'rank': '11', 'currentPrice': '77.64085', 'ratio1': '57.27%', 'ratio2': '103.72%'},
    {'index': '7', 'symbol': 'DOGE', 'change': '0.29', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:42', 'highPrice': '0.7402', 'highTime': '2021-05-08', 'decline': '-81.65', 'change24h': '-1.09', 'col10': '', 'col11': '', 'col12': '', 'rank': '20', 'currentPrice': '0.13521', 'ratio1': '44.02%', 'ratio2': '102.53%'},
    {'index': '8', 'symbol': 'SUI', 'change': '0.37', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '5.3537', 'highTime': '2025-01-07', 'decline': '-74.7', 'change24h': '-1.81', 'col10': '', 'col11': '', 'col12': '', 'rank': '25', 'currentPrice': '1.34877', 'ratio1': '33.88%', 'ratio2': '102.9%'},
    {'index': '9', 'symbol': 'TRX', 'change': '-0.05', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '0.4461', 'highTime': '2024-12-04', 'decline': '-37.88', 'change24h': '-0.07', 'col10': '', 'col11': '', 'col12': '', 'rank': '13', 'currentPrice': '0.2759', 'ratio1': '75.29%', 'ratio2': '100.93%'},
    {'index': '10', 'symbol': 'TON', 'change': '0.23', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '8.2833', 'highTime': '2024-06-15', 'decline': '-81.91', 'change24h': '-0.52', 'col10': '', 'col11': '', 'col12': '', 'rank': '17', 'currentPrice': '1.49166', 'ratio1': '43.98%', 'ratio2': '103.34%'},
    {'index': '11', 'symbol': 'ETC', 'change': '0.15', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '176.51', 'highTime': '2021-05-07', 'decline': '-92.7', 'change24h': '-0.41', 'col10': '', 'col11': '', 'col12': '', 'rank': '16', 'currentPrice': '12.82496', 'ratio1': '52.73%', 'ratio2': '101.21%'},
    {'index': '12', 'symbol': 'BCH', 'change': '0.37', 'rushUp': '2', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '4355.62', 'highTime': '2017-12-20', 'decline': '-87.93', 'change24h': '0.74', 'col10': '', 'col11': '', 'col12': '', 'rank': '7', 'currentPrice': '523.4507', 'ratio1': '80.43%', 'ratio2': '116.27%'},
    {'index': '13', 'symbol': 'HBAR', 'change': '0.44', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '0.5758', 'highTime': '2021-09-16', 'decline': '-77.02', 'change24h': '-1.05', 'col10': '', 'col11': '', 'col12': '', 'rank': '19', 'currentPrice': '0.13172', 'ratio1': '51.6%', 'ratio2': '106.41%'},
    {'index': '14', 'symbol': 'XLM', 'change': '0.34', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '0.9381', 'highTime': '2018-01-04', 'decline': '-75.26', 'change24h': '-0.21', 'col10': '', 'col11': '', 'col12': '', 'rank': '15', 'currentPrice': '0.2311', 'ratio1': '55.33%', 'ratio2': '105.66%'},
    {'index': '15', 'symbol': 'FIL', 'change': '0.12', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '237.61', 'highTime': '2021-04-02', 'decline': '-99.38', 'change24h': '0.29', 'col10': '', 'col11': '', 'col12': '', 'rank': '9', 'currentPrice': '1.46079', 'ratio1': '54.99%', 'ratio2': '102.31%'},
    {'index': '16', 'symbol': 'ADA', 'change': '0.41', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '3.099', 'highTime': '2021-09-02', 'decline': '-87.47', 'change24h': '0.52', 'col10': '', 'col11': '', 'col12': '', 'rank': '8', 'currentPrice': '0.38672', 'ratio1': '40.54%', 'ratio2': '104.26%'},
    {'index': '17', 'symbol': 'LINK', 'change': '0.37', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '52.9614', 'highTime': '2021-05-10', 'decline': '-77.16', 'change24h': '-0.62', 'col10': '', 'col11': '', 'col12': '', 'rank': '18', 'currentPrice': '12.04413', 'ratio1': '45.67%', 'ratio2': '103.02%'},
    {'index': '18', 'symbol': 'CRO', 'change': '0.29', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '0.9732', 'highTime': '2021-11-25', 'decline': '-89.46', 'change24h': '0.2', 'col10': '', 'col11': '', 'col12': '', 'rank': '10', 'currentPrice': '0.10215', 'ratio1': '26.48%', 'ratio2': '109.74%'},
    {'index': '19', 'symbol': 'DOT', 'change': '0.54', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '54.9467', 'highTime': '2021-11-05', 'decline': '-96.23', 'change24h': '0.79', 'col10': '', 'col11': '', 'col12': '', 'rank': '6', 'currentPrice': '2.06408', 'ratio1': '42.26%', 'ratio2': '104.39%'},
    {'index': '20', 'symbol': 'OKB', 'change': '0.4', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '258.2', 'highTime': '2025-08-22', 'decline': '-61.2', 'change24h': '1.2', 'col10': '', 'col11': '', 'col12': '', 'rank': '5', 'currentPrice': '99.75915', 'ratio1': '42.36%', 'ratio2': '106.41%'},
    {'index': '21', 'symbol': 'AAVE', 'change': '0.12', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:43', 'highPrice': '706.32', 'highTime': '2021-05-19', 'decline': '-76.11', 'change24h': '1.84', 'col10': '', 'col11': '', 'col12': '', 'rank': '3', 'currentPrice': '168.02394', 'ratio1': '52.08%', 'ratio2': '111.72%'},
    {'index': '22', 'symbol': 'UNI', 'change': '0.38', 'rushUp': '1', 'rushDown': '1', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '45.0591', 'highTime': '2021-05-03', 'decline': '-87.89', 'change24h': '-2.09', 'col10': '', 'col11': '', 'col12': '', 'rank': '26', 'currentPrice': '5.43115', 'ratio1': '52.37%', 'ratio2': '101.13%'},
    {'index': '23', 'symbol': 'NEAR', 'change': '-0.17', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '20.5368', 'highTime': '2022-01-15', 'decline': '-91.73', 'change24h': '1.95', 'col10': '', 'col11': '', 'col12': '', 'rank': '2', 'currentPrice': '1.69049', 'ratio1': '50.86%', 'ratio2': '106.13%'},
    {'index': '24', 'symbol': 'APT', 'change': '0.17', 'rushUp': '1', 'rushDown': '2', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '28', 'highTime': '2022-10-19', 'decline': '-93.24', 'change24h': '2.04', 'col10': '', 'col11': '', 'col12': '', 'rank': '1', 'currentPrice': '1.88437', 'ratio1': '34.3%', 'ratio2': '103.75%'},
    {'index': '25', 'symbol': 'CFX', 'change': '0.2', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '1.7018', 'highTime': '2021-03-27', 'decline': '-95.93', 'change24h': '-1.41', 'col10': '', 'col11': '', 'col12': '', 'rank': '22', 'currentPrice': '0.06899', 'ratio1': '36.73%', 'ratio2': '100.95%'},
    {'index': '26', 'symbol': 'CRV', 'change': '0.18', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '70.2347', 'highTime': '2020-08-14', 'decline': '-99.46', 'change24h': '-1.59', 'col10': '', 'col11': '', 'col12': '', 'rank': '24', 'currentPrice': '0.37687', 'ratio1': '43.68%', 'ratio2': '103.33%'},
    {'index': '27', 'symbol': 'STX', 'change': '0.35', 'rushUp': '0', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '3.8763', 'highTime': '2024-04-02', 'decline': '-92.7', 'change24h': '-2.14', 'col10': '', 'col11': '', 'col12': '', 'rank': '27', 'currentPrice': '0.28168', 'ratio1': '40.12%', 'ratio2': '101.22%'},
    {'index': '28', 'symbol': 'LDO', 'change': '0.46', 'rushUp': '1', 'rushDown': '0', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '155.26', 'highTime': '2021-07-01', 'decline': '-99.64', 'change24h': '-4.7', 'col10': '', 'col11': '', 'col12': '', 'rank': '29', 'currentPrice': '0.55918', 'ratio1': '41.27%', 'ratio2': '101.05%'},
    {'index': '29', 'symbol': 'TAO', 'change': '0.46', 'rushUp': '0', 'rushDown': '1', 'updateTime': '2025-12-02 18:06:44', 'highPrice': '781.87', 'highTime': '2024-04-12', 'decline': '-66.8', 'change24h': '-3.99', 'col10': '', 'col11': '', 'col12': '', 'rank': '28', 'currentPrice': '258.4338', 'ratio1': '54.2%', 'ratio2': '101.15%'},
]

DEMO_STATS = {
    'rushUp': '17',   # 从TXT文件读取: 透明标签_急涨总和=急涨: 17
    'rushDown': '4',  # 从TXT文件读取: 透明标签_急跌总和=急跌: 4
    'status': '震荡无序',
    'ratio': '3.25',  # 从TXT文件读取: 透明标签_急涨急跌比值=比值: 3.25
    'greenCount': '6',  # 从TXT文件读取: 透明标签_绿色数量=6
    'percentage': '21%',  # 从TXT文件读取: 透明标签_百分比=21%
    'count': '7',     # 从TXT文件读取: 透明标签_计次=7
    'diff': '13'      # 从TXT文件读取: 透明标签_差值结果=差值: 13
}

@app.route('/')
def index():
    """首页 - 虚拟币系统监控中心"""
    response = send_from_directory('.', 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/live')
def live_dashboard():
    """实时监控面板 - 加密货币数据"""
    response = send_from_directory('.', 'crypto_dashboard.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/signal')
def signal_monitor():
    """信号监控页面 - 新版独立模块"""
    response = send_from_directory('.', 'signal_monitor.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/signal/v3')
def signal_monitor_v3():
    """信号监控页面 v3 - 旧版本（表格+曲线图）"""
    response = send_from_directory('.', 'signal_monitor_v3.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/panic')
def panic_monitor():
    """恐慌清洗指标页面 - 新版本（独立计算）"""
    response = send_from_directory('.', 'panic_wash_new.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/panic-chart')
def panic_chart():
    """恐慌清洗指标页面（重定向到新版本）"""
    response = send_from_directory('.', 'panic_wash_new.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/monitor/signal')
def get_signal_data():
    """获取信号数据API（自动从 Google Drive 读取，失败时使用演示数据，并保存到数据库）"""
    try:
        # 自动读取数据（优先 Google Drive）
        data = monitor_reader.get_signal_data()
        
        # 保存到数据库（用于历史曲线）
        try:
            db.save_signal_data(data)
        except Exception as save_error:
            print(f"⚠️  保存信号数据到数据库失败: {save_error}")
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/panic')
def get_panic_data():
    """获取恐慌清洗数据API - 代理到新API服务"""
    import requests
    try:
        # 代理请求到新的恐慌清洗API服务（端口5002）
        response = requests.get('http://localhost:5002/api/panic-wash/latest', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        # 降级处理：返回旧版数据或错误信息
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '新版恐慌清洗指标服务未启动，请访问: http://localhost:5002'
        }), 500

@app.route('/api/monitor/signal/history')
def get_signal_history():
    """获取信号历史数据API（用于绘制曲线）"""
    try:
        # 获取查询参数
        date = request.args.get('date')  # 可选，格式：YYYY-MM-DD
        hours = request.args.get('hours', 24, type=int)  # 默认查询24小时
        
        # 查询历史数据
        history = db.get_signal_history(date=date, hours=hours)
        
        return jsonify({
            'success': True,
            'data': history,
            'count': len(history)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monitor/panic/history')
def get_panic_history_api():
    """获取恐慌清洗历史数据API - 代理到新API服务"""
    import requests
    try:
        # 代理请求到新的恐慌清洗API服务（端口5002）
        response = requests.get('http://localhost:5002/api/panic-wash/history', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        # 降级处理：返回旧版数据
        try:
            date = request.args.get('date')
            hours = request.args.get('hours', 24, type=int)
            history = db.get_panic_history(date=date, hours=hours)
            return jsonify({
                'success': True,
                'data': history,
                'count': len(history),
                'source': 'fallback_old_data'
            })
        except:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# 新版恐慌清洗API的直接代理路由（用于前端页面）
@app.route('/api/panic-wash/latest')
def proxy_panic_wash_latest():
    """代理：获取最新恐慌清洗数据"""
    import requests
    try:
        response = requests.get('http://localhost:5002/api/panic-wash/latest', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/panic-wash/history')
def proxy_panic_wash_history():
    """代理：获取恐慌清洗历史数据"""
    import requests
    try:
        response = requests.get('http://localhost:5002/api/panic-wash/history', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/panic-wash/stats')
def proxy_panic_wash_stats():
    """代理：获取恐慌清洗统计信息"""
    import requests
    try:
        response = requests.get('http://localhost:5002/api/panic-wash/stats', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/panic-wash/refresh', methods=['POST'])
def proxy_panic_wash_refresh():
    """代理：手动刷新恐慌清洗数据"""
    import requests
    try:
        response = requests.post('http://localhost:5002/api/panic-wash/refresh', timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/panic-wash/query')
def proxy_panic_wash_query():
    """代理：按日期时间查询恐慌清洗数据"""
    import requests
    from flask import request
    try:
        # 获取查询参数
        start = request.args.get('start')
        end = request.args.get('end')
        
        if not start or not end:
            return jsonify({'success': False, 'message': '请提供start和end参数'}), 400
        
        # 转发请求到5002端口
        response = requests.get(
            f'http://localhost:5002/api/panic-wash/query?start={start}&end={end}',
            timeout=10
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 信号监控页面和API代理
@app.route('/signal')
def signal_monitor_page():
    """信号监控页面"""
    return send_file('signal_monitor.html')

@app.route('/api/signal-monitor/latest')
def proxy_signal_monitor_latest():
    """代理：获取最新信号"""
    import requests
    try:
        response = requests.get('http://localhost:5003/api/signal-monitor/latest', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal-monitor/history')
def proxy_signal_monitor_history():
    """代理：获取历史信号"""
    import requests
    from flask import request
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_time = request.args.get('start_time', '00:00:00')
        end_time = request.args.get('end_time', '23:59:59')
        
        response = requests.get(
            f'http://localhost:5003/api/signal-monitor/history?start_date={start_date}&end_date={end_date}&start_time={start_time}&end_time={end_time}',
            timeout=10
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal-monitor/test')
def proxy_signal_monitor_test():
    """代理：测试信号监控API"""
    import requests
    try:
        response = requests.get('http://localhost:5003/api/signal-monitor/test', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 首页数据API代理
@app.route('/live-data')
def live_data_page():
    """实时监控数据页面"""
    response = send_from_directory('.', 'live_monitor.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/homepage/latest')
def proxy_homepage_latest():
    """代理：获取最新首页数据"""
    import requests
    try:
        response = requests.get('http://localhost:5004/api/homepage/latest', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/homepage/history')
def proxy_homepage_history():
    """代理：获取首页历史数据"""
    import requests
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_time = request.args.get('start_time', '00:00:00')
        end_time = request.args.get('end_time', '23:59:59')
        
        response = requests.get(
            f'http://localhost:5004/api/homepage/history?start_date={start_date}&end_date={end_date}&start_time={start_time}&end_time={end_time}',
            timeout=10
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/homepage/stats')
def proxy_homepage_stats():
    """代理：获取首页统计信息"""
    import requests
    try:
        response = requests.get('http://localhost:5004/api/homepage/stats', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/homepage/test')
def proxy_homepage_test():
    """代理：测试首页数据API"""
    import requests
    try:
        response = requests.get('http://localhost:5004/api/homepage/test', timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_priority_level(ratio1_str, ratio2_str):
    """
    根据最高占比和最低占比计算优先级等级
    
    等级规则:
    - 等级1: 最高占比>90 且 最低占比>120
    - 等级2: 最高占比>80 且 最低占比>120
    - 等级3: 最高占比>90 且 最低占比>110
    - 等级4: 最高占比>70 且 最低占比>120
    - 等级5: 最高占比>80 且 最低占比>110
    - 等级6: 最高占比<80 且 最低占比<110
    - 无等级: 不满足任何条件
    """
    try:
        # 去除百分号并转换为浮点数
        ratio1 = float(ratio1_str.rstrip('%'))
        ratio2 = float(ratio2_str.rstrip('%'))
        
        # 按优先级顺序检查等级
        if ratio1 > 90 and ratio2 > 120:
            return '1'
        elif ratio1 > 80 and ratio2 > 120:
            return '2'
        elif ratio1 > 90 and ratio2 > 110:
            return '3'
        elif ratio1 > 70 and ratio2 > 120:
            return '4'
        elif ratio1 > 80 and ratio2 > 110:
            return '5'
        elif ratio1 < 80 and ratio2 < 110:
            return '6'
        else:
            return '-'  # 不满足任何条件
    except (ValueError, AttributeError):
        return '-'  # 数据格式错误

@app.route('/api/crypto-data')
def get_crypto_data():
    """获取加密货币数据API - 优先从数据库读取最新快照"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    
    # 尝试从数据库读取最新快照
    latest_snapshot = None
    try:
        import sqlite3
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT snapshot_time FROM crypto_snapshots 
            ORDER BY snapshot_time DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            latest_snapshot = db.get_snapshot_by_time(row[0])
    except Exception as e:
        print(f"⚠️  从数据库读取失败: {e}")
        latest_snapshot = None
    
    # 如果数据库有数据，使用数据库数据
    if latest_snapshot and 'data' in latest_snapshot:
        snapshot_stats = latest_snapshot['stats']
        print(f"✅ 从数据库返回最新快照: {snapshot_stats['snapshot_time']}")
        
        # 为每个币种计算优先级等级
        data_with_level = []
        for coin in latest_snapshot['data']:
            coin_copy = coin.copy()
            coin_copy['priorityLevel'] = calculate_priority_level(
                coin.get('ratio1', '0%'),
                coin.get('ratio2', '0%')
            )
            data_with_level.append(coin_copy)
        
        return jsonify({
            'success': True,
            'data': data_with_level,
            'stats': {
                'rushUp': snapshot_stats['rushUp'],
                'rushDown': snapshot_stats['rushDown'],
                'diff': snapshot_stats['diff'],
                'count': snapshot_stats['count'],
                'ratio': snapshot_stats['ratio'],
                'status': snapshot_stats['status'],
                'greenCount': snapshot_stats['greenCount'],
                'percentage': snapshot_stats['percentage']
            },
            'updateTime': snapshot_stats['snapshot_time'],
            'filename': snapshot_stats.get('filename', '数据库数据'),
            'fileTimestamp': snapshot_stats['snapshot_time']
        })
    
    # 如果数据库没有数据，回退到演示数据
    print("ℹ️  数据库无数据，使用演示数据")
    file_time = datetime.now(beijing_tz)
    file_time_str = file_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 为每个币种计算优先级等级
    data_with_level = []
    for coin in DEMO_DATA:
        coin_copy = coin.copy()
        coin_copy['priorityLevel'] = calculate_priority_level(
            coin.get('ratio1', '0%'),
            coin.get('ratio2', '0%')
        )
        data_with_level.append(coin_copy)
    
    # 保存到数据库
    try:
        snapshot_id = db.save_snapshot(
            data=data_with_level,
            stats=DEMO_STATS,
            snapshot_time=file_time_str,
            filename='2025-12-02_1806.txt (演示数据)'
        )
        print(f"📊 快照ID {snapshot_id} 已保存到数据库")
    except Exception as e:
        print(f"⚠️  数据库保存失败: {e}")
    
    return jsonify({
        'success': True,
        'data': data_with_level,
        'stats': DEMO_STATS,
        'updateTime': file_time_str,
        'filename': '2025-12-02_1806.txt (演示数据)',
        'fileTimestamp': file_time_str
    })

@app.route('/api/refresh')
def refresh_data():
    """手动刷新数据 - 演示版"""
    return jsonify({
        'success': True,
        'message': '演示模式: 使用静态数据'
    })

@app.route('/api/database/stats')
def get_database_stats():
    """获取数据库统计信息"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/database/snapshots/<date>')
def get_snapshots_by_date(date):
    """查询某天的所有快照"""
    try:
        snapshots = db.get_snapshots_by_date(date)
        return jsonify({
            'success': True,
            'date': date,
            'count': len(snapshots),
            'snapshots': snapshots
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/database/snapshot/<path:snapshot_time>')
def get_snapshot_by_time(snapshot_time):
    """根据时间查询快照详情"""
    try:
        snapshot = db.get_snapshot_by_time(snapshot_time)
        if snapshot:
            return jsonify({
                'success': True,
                'snapshot': snapshot
            })
        else:
            return jsonify({
                'success': False,
                'error': '快照不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/database/coin/<symbol>')
def get_coin_history(symbol):
    """查询币种历史数据"""
    try:
        history = db.get_coin_history(symbol)
        return jsonify({
            'success': True,
            'symbol': symbol,
            'count': len(history),
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history-chart')
def get_history_chart():
    """获取历史图表数据 - 演示版（基于真实TXT数据）"""
    # 根据真实TXT文件时间(2025-12-02 20:27:36)生成历史数据
    # 最终累计: 急涨=17, 急跌=4, 计次=7
    from datetime import datetime, timedelta
    import pytz
    import random
    
    beijing_tz = pytz.timezone('Asia/Shanghai')
    
    # TXT文件时间: 2025-12-02 20:27:36 (向下取整到10分钟: 20:20)
    txt_time = datetime(2025, 12, 2, 20, 20, 0, tzinfo=beijing_tz)
    
    # 从今天早上8点开始到TXT文件时间
    start_time = txt_time.replace(hour=8, minute=0, second=0)
    
    history = []
    current = start_time
    
    # 目标最终值（TXT文件中的累计值）
    target_rush_up = 17
    target_rush_down = 4
    target_count = 7
    
    # 计算时间跨度（8:00到20:20，共12小时20分 = 740分钟 = 74个10分钟点）
    total_points = int((txt_time - start_time).total_seconds() / 600) + 1
    
    # 累加值（逐步增长到目标值）
    cumulative_rush_up = 0
    cumulative_rush_down = 0
    cumulative_count = 0
    
    # 生成每10分钟的数据点
    for i in range(total_points):
        time_str = current.strftime('%H:%M')
        
        # 逐步增加到目标值（确保最后一个点达到目标值）
        if i == total_points - 1:
            # 最后一个点：设置为目标值
            cumulative_rush_up = target_rush_up
            cumulative_rush_down = target_rush_down
            cumulative_count = target_count
        else:
            # 中间点：随机增加（确保不超过目标值）
            remaining_points = total_points - i - 1
            
            # 急涨：剩余值随机分配
            remaining_up = target_rush_up - cumulative_rush_up
            if remaining_up > 0 and remaining_points > 0:
                max_increment = min(3, remaining_up)
                if random.random() < 0.4:  # 40%概率增加
                    cumulative_rush_up += random.randint(0, max_increment)
            
            # 急跌：剩余值随机分配
            remaining_down = target_rush_down - cumulative_rush_down
            if remaining_down > 0 and remaining_points > 0:
                max_increment = min(2, remaining_down)
                if random.random() < 0.3:  # 30%概率增加
                    cumulative_rush_down += random.randint(0, max_increment)
            
            # 计次：剩余值随机分配
            remaining_count = target_count - cumulative_count
            if remaining_count > 0 and remaining_points > 0:
                if random.random() < 0.2:  # 20%概率增加
                    cumulative_count += 1
        
        # 保存数据点
        history.append({
            'time': time_str,
            'timestamp': current.strftime('%Y-%m-%d %H:%M:%S'),
            'rushUp': str(cumulative_rush_up),
            'rushDown': str(cumulative_rush_down),
            'count': str(cumulative_count)
        })
        
        current += timedelta(minutes=10)
    
    # 验证最终值
    final_up = int(history[-1]['rushUp'])
    final_down = int(history[-1]['rushDown'])
    final_count = int(history[-1]['count'])
    
    print(f"✅ 生成 {len(history)} 个历史数据点")
    print(f"时间范围: {history[0]['timestamp']} → {history[-1]['timestamp']}")
    print(f"最终累计 - 急涨: {final_up}/{target_rush_up}, 急跌: {final_down}/{target_rush_down}, 计次: {final_count}/{target_count}")
    
    # 验证单调性
    for i in range(1, len(history)):
        prev_up = int(history[i-1]['rushUp'])
        curr_up = int(history[i]['rushUp'])
        if curr_up < prev_up:
            print(f"⚠️ 警告: 急涨数据异常 {history[i-1]['time']}({prev_up}) → {history[i]['time']}({curr_up})")
    
    return jsonify({
        'success': True,
        'history': history
    })

@app.route('/api/home-data')
def get_home_data():
    """获取首页数据（从 crypto_latest_data.txt 读取）"""
    from crypto_data_parser import CryptoDataParser
    import os
    
    data_file = 'crypto_latest_data.txt'
    
    try:
        if not os.path.exists(data_file):
            return jsonify({
                'success': False,
                'error': '数据文件不存在',
                'message': '请先更新数据文件'
            }), 404
        
        # 读取文件
        with open(data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析数据
        result = CryptoDataParser.parse_txt_content(content)
        
        if not result:
            return jsonify({
                'success': False,
                'error': '解析失败'
            }), 500
        
        # 获取文件修改时间
        file_mtime = os.path.getmtime(data_file)
        import datetime as dt
        file_time = dt.datetime.fromtimestamp(file_mtime)
        
        # 返回数据
        return jsonify({
            'success': True,
            'data': result['data'],
            'stats': result['stats'],
            'updateTime': file_time.strftime('%Y-%m-%d %H:%M:%S'),
            'dataCount': len(result['data'])
        })
        
    except Exception as e:
        print(f"❌ 读取首页数据失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/home')
def home_monitor():
    """首页数据监控页面"""
    return send_file('home_monitor.html')

@app.route('/api/update-home-data', methods=['POST'])
def update_home_data():
    """手动更新首页数据"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'error': '内容不能为空'
            }), 400
        
        # 保存到文件
        with open('crypto_latest_data.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 验证数据
        from crypto_data_parser import CryptoDataParser
        result = CryptoDataParser.parse_txt_content(content)
        
        if not result:
            return jsonify({
                'success': False,
                'error': '数据格式错误，解析失败'
            }), 400
        
        print(f"✅ 数据已更新: {len(result['data'])} 个币种")
        
        return jsonify({
            'success': True,
            'message': '数据更新成功',
            'dataCount': len(result['data']),
            'stats': result['stats']
        })
        
    except Exception as e:
        print(f"❌ 更新数据失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 80)
    print("加密货币数据监控服务器 - 演示版本")
    print("=" * 80)
    print(f"启动时间: {datetime.now()}")
    print("⚠️  注意: 这是演示版本，使用模拟数据")
    print("⚠️  要使用真实数据，请运行: python3 crypto_server.py")
    print("=" * 80)
    
    # 启动后台调度器（每3分钟采集一次数据）
    scheduler.add_job(
        func=collect_monitoring_data,
        trigger='interval',
        minutes=10,
        id='collect_data',
        name='采集监控数据',
        replace_existing=True
    )
    scheduler.start()
    print("✅ 后台数据采集器已启动（每10分钟执行一次）")
    
    # 立即执行一次数据采集
    collect_monitoring_data()
    
    port = 5001
    print(f"\n服务器运行在: http://0.0.0.0:{port}")
    print(f"访问页面: http://0.0.0.0:{port}/")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 80)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\n✅ 调度器已停止")
