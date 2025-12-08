#!/usr/bin/env python3
"""
币种多空评分数据API服务
提供56字段数据接口
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = 'crypto_data.db'

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# 禁用响应缓存
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'service': '币种多空评分数据API',
        'success': True,
        'version': '1.0.0',
        'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/coin-scores/latest', methods=['GET'])
def get_latest_scores():
    """获取所有币种的最新评分数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取每个币种的最新记录
        cursor.execute('''
            SELECT * FROM coin_scores 
            WHERE timestamp IN (
                SELECT MAX(timestamp) 
                FROM coin_scores 
                GROUP BY symbol
            )
            ORDER BY symbol
        ''')
        
        rows = cursor.fetchall()
        
        coins = []
        for row in rows:
            coin = {
                'id': row['id'],
                'symbol': row['symbol'],
                'timestamp': row['timestamp'],
                'beijing_time': row['beijing_time'],
                
                # 多空得分
                'long_score': row['long_score'],
                'short_score': row['short_score'],
                'long_score_3m_avg': row['long_score_3m_avg'],
                'short_score_3m_avg': row['short_score_3m_avg'],
                'long_score_1h_avg': row['long_score_1h_avg'],
                'short_score_1h_avg': row['short_score_1h_avg'],
                'long_score_3h_avg': row['long_score_3h_avg'],
                'short_score_3h_avg': row['short_score_3h_avg'],
                'long_score_12h_avg': row['long_score_12h_avg'],
                'short_score_12h_avg': row['short_score_12h_avg'],
                'long_score_24h_avg': row['long_score_24h_avg'],
                'short_score_24h_avg': row['short_score_24h_avg'],
                
                # 持仓量
                'long_volume': row['long_volume'],
                'short_volume': row['short_volume'],
                'long_short_ratio': row['long_short_ratio'],
                
                # SAR 5分钟
                'sar_5m': row['sar_5m'],
                'sar_5m_quadrant': row['sar_5m_quadrant'],
                'price_5m': row['price_5m'],
                'sar_5m_trend': row['sar_5m_trend'],
                'sar_5m_duration': row['sar_5m_duration'],
                
                # SAR 1小时
                'sar_1h': row['sar_1h'],
                'sar_1h_quadrant': row['sar_1h_quadrant'],
                'price_1h': row['price_1h'],
                'sar_1h_trend': row['sar_1h_trend'],
                'sar_1h_duration': row['sar_1h_duration'],
                
                # RSI
                'rsi_5m': row['rsi_5m'],
                'rsi_1h': row['rsi_1h'],
                
                # 布林带 5分钟
                'bb_upper_5m': row['bb_upper_5m'],
                'bb_middle_5m': row['bb_middle_5m'],
                'bb_lower_5m': row['bb_lower_5m'],
                'bb_position_5m': row['bb_position_5m'],
                
                # 布林带 1小时
                'bb_upper_1h': row['bb_upper_1h'],
                'bb_middle_1h': row['bb_middle_1h'],
                'bb_lower_1h': row['bb_lower_1h'],
                'bb_position_1h': row['bb_position_1h'],
                
                # 统计
                'long_count': row['long_count'],
                'short_count': row['short_count']
            }
            coins.append(coin)
        
        conn.close()
        
        # 统计多空数量
        long_count = sum(1 for c in coins if c.get('sar_5m_trend') == '多头')
        short_count = sum(1 for c in coins if c.get('sar_5m_trend') == '空头')
        
        return jsonify({
            'success': True,
            'count': len(coins),
            'long_count': long_count,
            'short_count': short_count,
            'update_time': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S'),
            'data': coins
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coin-scores/symbol/<symbol>', methods=['GET'])
def get_coin_by_symbol(symbol):
    """获取指定币种的最新数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM coin_scores 
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': f'币种 {symbol} 不存在'
            }), 404
        
        coin = dict(row)
        
        return jsonify({
            'success': True,
            'data': coin
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coin-scores/history/<symbol>', methods=['GET'])
def get_coin_history(symbol):
    """获取指定币种的历史数据"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM coin_scores 
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({
                'success': False,
                'error': f'币种 {symbol} 没有历史数据'
            }), 404
        
        history = [dict(row) for row in rows]
        
        return jsonify({
            'success': True,
            'count': len(history),
            'data': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coin-scores/stats', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 总币种数
        cursor.execute('SELECT COUNT(DISTINCT symbol) FROM coin_scores')
        total_coins = cursor.fetchone()[0]
        
        # 总记录数
        cursor.execute('SELECT COUNT(*) FROM coin_scores')
        total_records = cursor.fetchone()[0]
        
        # 最新更新时间
        cursor.execute('SELECT MAX(beijing_time) FROM coin_scores')
        latest_update = cursor.fetchone()[0]
        
        # 多空趋势统计
        cursor.execute('''
            SELECT sar_5m_trend, COUNT(*) 
            FROM coin_scores 
            WHERE timestamp IN (
                SELECT MAX(timestamp) 
                FROM coin_scores 
                GROUP BY symbol
            )
            GROUP BY sar_5m_trend
        ''')
        trend_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_coins': total_coins,
            'total_records': total_records,
            'latest_update': latest_update,
            'trend_stats': trend_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coin-scores/timeline', methods=['GET'])
def get_timeline():
    """获取历史时间轴（所有快照时间点）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有唯一的时间点
        cursor.execute('''
            SELECT DISTINCT beijing_time, timestamp
            FROM coin_scores
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        timeline = [{'time': row[0], 'timestamp': row[1]} for row in rows]
        
        return jsonify({
            'success': True,
            'count': len(timeline),
            'data': timeline
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coin-scores/snapshot/<snapshot_time>', methods=['GET'])
def get_snapshot(snapshot_time):
    """获取指定时间点的快照数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM coin_scores 
            WHERE beijing_time = ?
            ORDER BY symbol
        ''', (snapshot_time,))
        
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({
                'success': False,
                'error': f'没有找到时间 {snapshot_time} 的数据'
            }), 404
        
        coins = []
        for row in rows:
            coin = dict(row)
            coins.append(coin)
        
        conn.close()
        
        # 统计多空数量
        long_count = sum(1 for c in coins if c.get('sar_5m_trend') == '多头')
        short_count = sum(1 for c in coins if c.get('sar_5m_trend') == '空头')
        
        return jsonify({
            'success': True,
            'snapshot_time': snapshot_time,
            'count': len(coins),
            'long_count': long_count,
            'short_count': short_count,
            'data': coins
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("币种多空评分数据API服务")
    print("=" * 60)
    print(f"API端口: 5003")
    print(f"数据库: {DB_PATH}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5003, debug=False)
