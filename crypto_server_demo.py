#!/usr/bin/env python3
"""
加密货币数据服务器 - 演示版本
使用模拟数据，不需要Google Drive API
用于测试和演示界面
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.')
CORS(app)

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
    'rushUp': '0',    # 清空后从0开始
    'rushDown': '0',  # 清空后从0开始
    'status': '震荡无序',
    'ratio': '0',
    'greenCount': '27',
    'percentage': '93%',
    'count': '0',     # 清空后从0开始
    'diff': '0'       # 清空后从0开始
}

@app.route('/')
def index():
    """首页"""
    response = send_from_directory('.', 'crypto_dashboard.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/crypto-data')
def get_crypto_data():
    """获取加密货币数据API - 演示版"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    # 模拟文件时间：当前时间减去1分钟（这样+1分钟后刚好是当前时间）
    file_time = datetime.now(beijing_tz)
    file_time_str = file_time.strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'success': True,
        'data': DEMO_DATA,
        'stats': DEMO_STATS,
        'updateTime': file_time_str,  # 这是文件时间戳（前端会+1分钟）
        'filename': '2025-12-02_1806.txt (演示数据)',
        'fileTimestamp': file_time_str  # 明确的文件时间戳字段
    })

@app.route('/api/refresh')
def refresh_data():
    """手动刷新数据 - 演示版"""
    return jsonify({
        'success': True,
        'message': '演示模式: 使用静态数据'
    })

@app.route('/api/history-chart')
def get_history_chart():
    """获取历史图表数据 - 演示版（从当前时刻开始，清空所有历史）"""
    # 清空历史数据，只返回一个初始点（当前时刻）
    from datetime import datetime
    import pytz
    
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    # 从当前时刻开始，累加值全部为0
    history = []
    
    # 添加当前时刻作为起始点
    history.append({
        'time': now.strftime('%H:%M'),
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        'rushUp': '0',      # 清空后从0开始
        'rushDown': '0',    # 清空后从0开始
        'count': '0'        # 清空后从0开始
    })
    
    print(f"✅ 历史数据已清空，重新开始统计")
    print(f"起始时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"初始值 - 急涨: 0, 急跌: 0, 计次: 0")
    
    return jsonify({
        'success': True,
        'history': history
    })

if __name__ == '__main__':
    print("=" * 80)
    print("加密货币数据监控服务器 - 演示版本")
    print("=" * 80)
    print(f"启动时间: {datetime.now()}")
    print("⚠️  注意: 这是演示版本，使用模拟数据")
    print("⚠️  要使用真实数据，请运行: python3 crypto_server.py")
    print("=" * 80)
    
    port = 5001
    print(f"\n服务器运行在: http://0.0.0.0:{port}")
    print(f"访问页面: http://0.0.0.0:{port}/")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
