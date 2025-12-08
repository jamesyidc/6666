#!/usr/bin/env python3
"""
V1V2成交量数据API服务
提供成交量数据接口
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = 'v1v2_volume.db'

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
        'service': 'V1V2成交量数据API',
        'success': True,
        'version': '1.0.0',
        'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/v1v2/latest', methods=['GET'])
def get_latest_volumes():
    """获取所有币种的最新成交量数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取每个币种的最新记录
        cursor.execute('''
            SELECT * FROM v1v2_volumes 
            WHERE timestamp IN (
                SELECT MAX(timestamp) 
                FROM v1v2_volumes 
                GROUP BY symbol
            )
            ORDER BY volume DESC
        ''')
        
        rows = cursor.fetchall()
        
        volumes = []
        total_volume = 0
        
        for row in rows:
            volume_data = {
                'id': row['id'],
                'symbol': row['symbol'],
                'volume': row['volume'],
                'timestamp': row['timestamp'],
                'beijing_time': row['beijing_time'],
                'update_time': row['update_time']
            }
            volumes.append(volume_data)
            total_volume += row['volume']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(volumes),
            'total_volume': total_volume,
            'update_time': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S'),
            'data': volumes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1v2/symbol/<symbol>', methods=['GET'])
def get_volume_by_symbol(symbol):
    """获取指定币种的最新成交量"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM v1v2_volumes 
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
        
        volume_data = dict(row)
        
        return jsonify({
            'success': True,
            'data': volume_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1v2/history/<symbol>', methods=['GET'])
def get_volume_history(symbol):
    """获取指定币种的历史成交量数据"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM v1v2_volumes 
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


@app.route('/api/v1v2/stats', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 总币种数
        cursor.execute('SELECT COUNT(DISTINCT symbol) FROM v1v2_volumes')
        total_symbols = cursor.fetchone()[0]
        
        # 总记录数
        cursor.execute('SELECT COUNT(*) FROM v1v2_volumes')
        total_records = cursor.fetchone()[0]
        
        # 最新更新时间
        cursor.execute('SELECT MAX(beijing_time) FROM v1v2_volumes')
        latest_update = cursor.fetchone()[0]
        
        # 总成交量（最新一次）
        cursor.execute('''
            SELECT SUM(volume) FROM v1v2_volumes
            WHERE timestamp IN (
                SELECT MAX(timestamp) FROM v1v2_volumes GROUP BY symbol
            )
        ''')
        total_volume = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_symbols': total_symbols,
            'total_records': total_records,
            'latest_update': latest_update,
            'total_volume': total_volume
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1v2/dates', methods=['GET'])
def get_available_dates():
    """获取所有有数据的日期列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT DATE(beijing_time) as date
            FROM v1v2_volumes
            ORDER BY date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        dates = [row[0] for row in rows]
        
        return jsonify({
            'success': True,
            'count': len(dates),
            'data': dates
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1v2/timeline', methods=['GET'])
def get_timeline():
    """获取历史时间轴（所有独特的时间点）"""
    try:
        date = request.args.get('date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date:
            # 按日期筛选
            cursor.execute('''
                SELECT DISTINCT beijing_time as time, timestamp
                FROM v1v2_volumes
                WHERE DATE(beijing_time) = ?
                ORDER BY timestamp DESC
            ''', (date,))
        else:
            # 所有时间点
            cursor.execute('''
                SELECT DISTINCT beijing_time as time, timestamp
                FROM v1v2_volumes
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


@app.route('/api/v1v2/snapshot/<snapshot_time>', methods=['GET'])
def get_snapshot(snapshot_time):
    """获取特定时间点的所有币种数据快照"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM v1v2_volumes
            WHERE beijing_time = ?
            ORDER BY volume DESC
        ''', (snapshot_time,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({
                'success': False,
                'error': f'没有找到时间 {snapshot_time} 的数据'
            }), 404
        
        data = [dict(row) for row in rows]
        
        return jsonify({
            'success': True,
            'count': len(data),
            'snapshot_time': snapshot_time,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 静态文件路由
@app.route('/v1v2')
@app.route('/v1v2/')
def v1v2_index():
    """V1V2成交量系统首页"""
    return send_from_directory('.', 'v1v2_viewer.html')


if __name__ == '__main__':
    print("=" * 60)
    print("V1V2成交量数据API服务")
    print("=" * 60)
    print(f"API端口: 5004")
    print(f"数据库: {DB_PATH}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5004, debug=False)
