#!/usr/bin/env python3
"""
全币数据统计系统 - API接口
提供按日期查询、时间轴数据等功能
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

DB_PATH = 'coin_history_stats.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/history/dates', methods=['GET'])
def get_available_dates():
    """获取有数据的日期列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT summary_date, total_snapshots,
                   first_snapshot_time, last_snapshot_time,
                   max_rush_up, max_rush_down,
                   highest_change, lowest_change
            FROM daily_summary
            ORDER BY summary_date DESC
        """)
        
        dates = []
        for row in cursor.fetchall():
            dates.append({
                'date': row['summary_date'],
                'snapshots': row['total_snapshots'],
                'time_range': f"{row['first_snapshot_time']} ~ {row['last_snapshot_time']}",
                'max_rush_up': row['max_rush_up'],
                'max_rush_down': row['max_rush_down'],
                'highest_change': row['highest_change'],
                'lowest_change': row['lowest_change']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'dates': dates,
            'total': len(dates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/snapshots', methods=['GET'])
def get_snapshots_by_date():
    """获取指定日期的所有快照"""
    date = request.args.get('date')
    if not date:
        return jsonify({
            'success': False,
            'error': '缺少date参数'
        }), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM coin_snapshots
            WHERE snapshot_date = ?
            ORDER BY snapshot_time
        """, (date,))
        
        snapshots = []
        for row in cursor.fetchall():
            snapshots.append({
                'id': row['id'],
                'time': row['snapshot_time'],
                'datetime': row['snapshot_datetime'],
                'total_coins': row['total_coins'],
                'rush_up_count': row['rush_up_count'],
                'rush_down_count': row['rush_down_count'],
                'rising_coins': row['rising_coins'],
                'falling_coins': row['falling_coins'],
                'account_ratio_avg': row['account_ratio_avg'],
                'account_ratio_max': row['account_ratio_max'],
                'account_ratio_min': row['account_ratio_min'],
                'avg_change_24h': row['avg_change_24h'],
                'max_change_24h': row['max_change_24h'],
                'min_change_24h': row['min_change_24h']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'date': date,
            'snapshots': snapshots,
            'total': len(snapshots)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/snapshot/<snapshot_datetime>', methods=['GET'])
def get_snapshot_detail(snapshot_datetime):
    """获取指定快照的详细数据（包含所有币种）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取快照概览
        cursor.execute("""
            SELECT *
            FROM coin_snapshots
            WHERE snapshot_datetime = ?
        """, (snapshot_datetime,))
        
        snapshot_row = cursor.fetchone()
        if not snapshot_row:
            return jsonify({
                'success': False,
                'error': '快照不存在'
            }), 404
        
        # 获取币种详细数据
        cursor.execute("""
            SELECT *
            FROM coin_details
            WHERE snapshot_datetime = ?
            ORDER BY rank
        """, (snapshot_datetime,))
        
        coins = []
        for row in cursor.fetchall():
            coins.append({
                'symbol': row['symbol'],
                'rank': row['rank'],
                'price': row['price'],
                'change_24h': row['change_24h'],
                'rush_up': row['rush_up'],
                'rush_down': row['rush_down'],
                'account_ratio': row['account_ratio'],
                'volume_24h': row['volume_24h'],
                'market_cap': row['market_cap']
            })
        
        conn.close()
        
        # 构造返回数据
        result = {
            'success': True,
            'snapshot': {
                'datetime': snapshot_row['snapshot_datetime'],
                'date': snapshot_row['snapshot_date'],
                'time': snapshot_row['snapshot_time'],
                'total_coins': snapshot_row['total_coins'],
                'rush_up_count': snapshot_row['rush_up_count'],
                'rush_down_count': snapshot_row['rush_down_count'],
                'rising_coins': snapshot_row['rising_coins'],
                'falling_coins': snapshot_row['falling_coins'],
                'account_ratio_avg': snapshot_row['account_ratio_avg'],
                'account_ratio_max': snapshot_row['account_ratio_max'],
                'account_ratio_min': snapshot_row['account_ratio_min'],
                'avg_change_24h': snapshot_row['avg_change_24h'],
                'max_change_24h': snapshot_row['max_change_24h'],
                'min_change_24h': snapshot_row['min_change_24h']
            },
            'coins': coins,
            'coins_count': len(coins)
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/timeline', methods=['GET'])
def get_timeline_data():
    """获取时间轴数据（用于图表展示）"""
    date = request.args.get('date')
    if not date:
        return jsonify({
            'success': False,
            'error': '缺少date参数'
        }), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                snapshot_time,
                total_coins,
                rush_up_count,
                rush_down_count,
                rising_coins,
                falling_coins,
                account_ratio_avg,
                avg_change_24h
            FROM coin_snapshots
            WHERE snapshot_date = ?
            ORDER BY snapshot_time
        """, (date,))
        
        timeline = {
            'times': [],
            'total_coins': [],
            'rush_up': [],
            'rush_down': [],
            'rising': [],
            'falling': [],
            'account_ratio': [],
            'avg_change': []
        }
        
        for row in cursor.fetchall():
            timeline['times'].append(row['snapshot_time'])
            timeline['total_coins'].append(row['total_coins'])
            timeline['rush_up'].append(row['rush_up_count'])
            timeline['rush_down'].append(row['rush_down_count'])
            timeline['rising'].append(row['rising_coins'])
            timeline['falling'].append(row['falling_coins'])
            timeline['account_ratio'].append(row['account_ratio_avg'])
            timeline['avg_change'].append(row['avg_change_24h'])
        
        conn.close()
        
        return jsonify({
            'success': True,
            'date': date,
            'timeline': timeline,
            'data_points': len(timeline['times'])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/search', methods=['GET'])
def search_coin_history():
    """搜索指定币种的历史数据"""
    symbol = request.args.get('symbol')
    date = request.args.get('date')
    
    if not symbol:
        return jsonify({
            'success': False,
            'error': '缺少symbol参数'
        }), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date:
            # 搜索指定日期
            cursor.execute("""
                SELECT *
                FROM coin_details
                WHERE symbol = ? AND snapshot_datetime LIKE ?
                ORDER BY snapshot_datetime
            """, (symbol.upper(), f"{date}%"))
        else:
            # 搜索所有历史
            cursor.execute("""
                SELECT *
                FROM coin_details
                WHERE symbol = ?
                ORDER BY snapshot_datetime DESC
                LIMIT 1000
            """, (symbol.upper(),))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'datetime': row['snapshot_datetime'],
                'price': row['price'],
                'change_24h': row['change_24h'],
                'rush_up': row['rush_up'],
                'rush_down': row['rush_down'],
                'account_ratio': row['account_ratio'],
                'rank': row['rank']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'date': date,
            'history': history,
            'total': len(history)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/stats', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取总体统计
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT snapshot_date) as total_days,
                COUNT(*) as total_snapshots,
                MAX(total_coins) as max_coins,
                AVG(total_coins) as avg_coins
            FROM coin_snapshots
        """)
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_days': stats['total_days'],
                'total_snapshots': stats['total_snapshots'],
                'max_coins': stats['max_coins'],
                'avg_coins': round(stats['avg_coins'], 2)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'service': '全币数据统计系统API',
        'version': '1.0.0',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    print("=" * 60)
    print("全币数据统计系统 - API服务")
    print("=" * 60)
    print("API端口: 5002")
    print("数据库: coin_history_stats.db")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=False)
