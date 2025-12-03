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
    """首页"""
    return send_file('crypto_home_v2.html')

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
