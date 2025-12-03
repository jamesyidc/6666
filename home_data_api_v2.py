#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页数据API - 带缓存版本
"""

from flask import Flask, jsonify, send_file
import asyncio
import sys
import os
import threading
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# 全局缓存
CACHE = {
    'data': None,
    'last_update': None,
    'updating': False
}

# 缓存有效期（秒）
CACHE_VALIDITY = 300  # 5分钟

def parse_home_data(content):
    """解析首页数据内容"""
    lines = content.strip().split('\n')
    
    stats = {}
    coins = []
    
    in_coin_section = False
    
    for line in lines:
        line = line.strip()
        
        # 解析统计数据
        if line.startswith('透明标签_'):
            parts = line.split('=')
            if len(parts) == 2:
                key = parts[0].replace('透明标签_', '')
                value = parts[1]
                
                if '急涨总和' in key:
                    stats['rushUp'] = value.split('：')[1] if '：' in value else value
                elif '急跌总和' in key:
                    stats['rushDown'] = value.split('：')[1] if '：' in value else value
                elif '五种状态' in key:
                    stats['status'] = value.split('：')[1] if '：' in value else value
                elif '急涨急跌比值' in key:
                    stats['ratio'] = value.split('：')[1] if '：' in value else value
                elif '绿色数量' in key:
                    stats['greenCount'] = value
                elif '百分比' in key:
                    stats['percentage'] = value
        
        # 币种数据
        if '[超级列表框_首页开始]' in line:
            in_coin_section = True
            continue
        
        if '[超级列表框_首页结束]' in line:
            break
        
        if in_coin_section and '|' in line:
            parts = line.split('|')
            if len(parts) >= 16:
                coin = {
                    'index': parts[0],
                    'symbol': parts[1],
                    'change': parts[2],
                    'rushUp': parts[3],
                    'rushDown': parts[4],
                    'updateTime': parts[5],
                    'highPrice': parts[6],
                    'highTime': parts[7],
                    'decline': parts[8],
                    'change24h': parts[9],
                    'rank': parts[12],
                    'currentPrice': parts[13],
                    'ratio1': parts[14],
                    'ratio2': parts[15]
                }
                coins.append(coin)
    
    # 获取更新时间
    update_time = coins[0]['updateTime'] if coins else ''
    
    return {
        'stats': stats,
        'coins': coins,
        'updateTime': update_time
    }

def update_cache():
    """后台更新缓存"""
    global CACHE
    
    if CACHE['updating']:
        print("已经在更新中，跳过...")
        return
    
    CACHE['updating'] = True
    print(f"\n{'='*60}")
    print(f"开始更新数据缓存... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        from gdrive_home_data_reader import get_latest_file_by_sorting
        
        # 获取最新数据
        result = asyncio.run(get_latest_file_by_sorting())
        
        if result and result.get('content'):
            parsed_data = parse_home_data(result['content'])
            
            CACHE['data'] = {
                'parsed_data': parsed_data,
                'filename': result['filename'],
                'time_diff': result['time_diff']
            }
            CACHE['last_update'] = time.time()
            
            print(f"✅ 缓存更新成功")
            print(f"   文件名: {result['filename']}")
            print(f"   时间差: {result['time_diff']:.1f} 分钟")
            
            # 自动保存到数据库
            try:
                from import_history_simple import parse_filename_datetime, parse_home_data as parse_for_db, save_to_database
                
                filename = result['filename']
                content = result['content']
                record_time = parse_filename_datetime(filename)
                
                if record_time:
                    stats, coins = parse_for_db(content)
                    success, msg = save_to_database(filename, record_time, stats, coins)
                    if success:
                        print(f"   💾 已自动保存到数据库")
                    else:
                        print(f"   💾 数据库: {msg}")
            except Exception as db_error:
                print(f"   ⚠️  保存到数据库失败: {str(db_error)}")
            
            print(f"{'='*60}\n")
        else:
            print("❌ 获取数据失败")
    except Exception as e:
        print(f"❌ 更新缓存失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        CACHE['updating'] = False

def background_updater():
    """后台定时更新线程"""
    while True:
        try:
            update_cache()
            # 每5分钟更新一次
            time.sleep(300)
        except Exception as e:
            print(f"后台更新线程错误: {str(e)}")
            time.sleep(60)

@app.route('/')
def index():
    """首页 - 导航页"""
    return send_file('index.html')

@app.route('/live')
def live():
    """实时监控页面"""
    return send_file('crypto_home_v2.html')

@app.route('/history')
def history():
    """历史回看页面"""
    return send_file('history_viewer.html')

@app.route('/panic-wash')
def panic_wash():
    """恐慌清洗指标监控页面"""
    return send_file('panic_wash_monitor.html')

@app.route('/api/panic-wash')
def get_panic_wash_api():
    """恐慌清洗API - 直接返回数据"""
    try:
        from panic_wash_simple import get_panic_wash_data_sync
        data = get_panic_wash_data_sync()
        
        if data:
            return jsonify({
                'success': True,
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'error': '暂无数据'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/home-data')
def get_home_data():
    """获取首页数据API（使用缓存）"""
    try:
        # 检查缓存
        if CACHE['data'] is None:
            # 第一次请求，立即更新
            update_cache()
        elif CACHE['last_update'] and (time.time() - CACHE['last_update']) > CACHE_VALIDITY:
            # 缓存过期，触发后台更新（但立即返回旧数据）
            threading.Thread(target=update_cache, daemon=True).start()
        
        if CACHE['data'] is None:
            return jsonify({
                'success': False,
                'error': '数据尚未加载'
            }), 503
        
        cached = CACHE['data']
        
        return jsonify({
            'success': True,
            'data': cached['parsed_data'],
            'filename': cached['filename'],
            'time_diff': cached['time_diff'],
            'cached_at': datetime.fromtimestamp(CACHE['last_update']).strftime('%Y-%m-%d %H:%M:%S') if CACHE['last_update'] else None
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 历史数据API ====================

def query_history_data(start_time=None, end_time=None, limit=100):
    """查询历史数据"""
    import sqlite3
    conn = sqlite3.connect('crypto_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 构建查询条件
        where_clauses = []
        params = []
        
        if start_time:
            where_clauses.append('record_time >= ?')
            params.append(start_time)
        
        if end_time:
            where_clauses.append('record_time <= ?')
            params.append(end_time)
        
        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        # 查询统计数据
        cursor.execute(f'''
            SELECT * FROM stats_history
            WHERE {where_sql}
            ORDER BY record_time DESC
            LIMIT ?
        ''', params + [limit])
        
        stats_records = [dict(row) for row in cursor.fetchall()]
        
        # 为每条统计数据查询对应的币种数据
        for record in stats_records:
            cursor.execute('''
                SELECT * FROM coin_history
                WHERE stats_id = ?
                ORDER BY index_num
            ''', (record['id'],))
            
            record['coins'] = [dict(row) for row in cursor.fetchall()]
        
        return stats_records
        
    finally:
        conn.close()

@app.route('/api/history/dates')
def get_dates():
    """获取有数据的日期列表"""
    try:
        import sqlite3
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT DATE(record_time) as date
            FROM stats_history
            ORDER BY date DESC
        ''')
        
        dates = [row[0] for row in cursor.fetchall()]
        
        # 获取每个日期的统计信息
        date_info = []
        for date in dates:
            cursor.execute('''
                SELECT COUNT(*) as count,
                       MIN(record_time) as min_time,
                       MAX(record_time) as max_time
                FROM stats_history
                WHERE DATE(record_time) = ?
            ''', (date,))
            
            row = cursor.fetchone()
            date_info.append({
                'date': date,
                'count': row[0],
                'min_time': row[1],
                'max_time': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'dates': date_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/query')
def query_history():
    """查询历史数据"""
    try:
        from flask import request
        
        # 获取查询参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        date = request.args.get('date')  # 如果只查询某一天
        limit = int(request.args.get('limit', 100))
        
        # 如果指定了日期，自动设置时间范围
        if date:
            start_time = f"{date} 00:00:00"
            end_time = f"{date} 23:59:59"
        
        records = query_history_data(start_time, end_time, limit)
        
        return jsonify({
            'success': True,
            'count': len(records),
            'data': records,
            'query': {
                'start_time': start_time,
                'end_time': end_time,
                'limit': limit
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/stats')
def get_history_stats():
    """获取数据库统计信息"""
    try:
        import sqlite3
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM stats_history')
        stats_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM coin_history')
        coin_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(record_time), MAX(record_time) FROM stats_history')
        time_range = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(DISTINCT DATE(record_time)) FROM stats_history')
        day_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_records': stats_count,
                'total_coins': coin_count,
                'earliest': time_range[0],
                'latest': time_range[1],
                'days': day_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/import/current', methods=['POST'])
def import_current():
    """导入当前最新数据"""
    try:
        from import_history_simple import import_current_data
        asyncio.run(import_current_data())
        return jsonify({
            'success': True,
            'message': '导入成功'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============== 信号统计历史API ==============

@app.route('/signal-history')
def signal_history_page():
    """信号统计历史回看页面"""
    return send_file('signal_history_viewer.html')

@app.route('/api/signal-stats/save', methods=['POST'])
def save_signal_stats():
    """保存信号统计数据"""
    try:
        from flask import request
        import sqlite3
        
        data = request.json
        record_time = data.get('record_time')
        
        if not record_time:
            record_time = datetime.now().strftime('%Y-%m-%d %H:%M:00')
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO signal_stats_history 
            (record_time, total_count, long_count, short_count, 
             chaodi_count, dibu_count, dingbu_count, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_time,
            data.get('total', 0),
            data.get('long', 0),
            data.get('short', 0),
            data.get('chaodi', 0),
            data.get('dibu', 0),
            data.get('dingbu', 0),
            data.get('source_url', '')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '保存成功',
            'record_time': record_time
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/signal-stats/query')
def query_signal_stats():
    """查询信号统计历史数据"""
    try:
        from flask import request
        import sqlite3
        
        date = request.args.get('date')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 200, type=int)
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询
        where_clauses = []
        params = []
        
        if date:
            if start_time and end_time:
                where_clauses.append('record_time BETWEEN ? AND ?')
                params.extend([f'{date} {start_time}:00', f'{date} {end_time}:59'])
            else:
                where_clauses.append('DATE(record_time) = ?')
                params.append(date)
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ''
        
        query = f'''
            SELECT 
                record_time, total_count, long_count, short_count,
                chaodi_count, dibu_count, dingbu_count, source_url
            FROM signal_stats_history
            {where_sql}
            ORDER BY record_time DESC
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append({
                'record_time': row['record_time'],
                'total': row['total_count'],
                'long': row['long_count'],
                'short': row['short_count'],
                'chaodi': row['chaodi_count'],
                'dibu': row['dibu_count'],
                'dingbu': row['dingbu_count'],
                'source_url': row['source_url']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/signal-stats/stats')
def signal_stats_db_stats():
    """获取信号统计数据库统计信息"""
    try:
        import sqlite3
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM signal_stats_history')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(record_time), MAX(record_time) FROM signal_stats_history')
        time_range = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_records': total,
            'time_range': {
                'start': time_range[0],
                'end': time_range[1]
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("首页数据监控服务器 V2 (带缓存)")
    print("="*60)
    print("访问: http://0.0.0.0:5003/")
    print("缓存有效期: 5 分钟")
    print("="*60)
    
    # 启动后台更新线程
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    print("✅ 后台更新线程已启动\n")
    
    app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)
