#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标API
"""

from flask import Flask, jsonify
import threading
import time
from panic_wash_simple import get_panic_wash_data_sync

app = Flask(__name__)

# 全局缓存
CACHE = {
    'data': None,
    'last_update': None,
    'updating': False
}

# 缓存有效期（秒）
CACHE_VALIDITY = 300  # 5分钟

def update_cache():
    """更新缓存"""
    global CACHE
    
    if CACHE['updating']:
        print("已经在更新中，跳过...")
        return
    
    CACHE['updating'] = True
    print(f"\n{'='*60}")
    print("开始更新恐慌清洗数据...")
    print(f"{'='*60}")
    
    try:
        # 获取数据（同步版本）
        result = get_panic_wash_data_sync()
        
        if result:
            CACHE['data'] = result
            CACHE['last_update'] = time.time()
            print(f"✅ 数据更新成功")
        else:
            print("❌ 获取数据失败")
    except Exception as e:
        print(f"❌ 更新失败: {str(e)}")
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

@app.route('/api/panic-wash')
def get_panic_wash():
    """获取恐慌清洗数据API"""
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
                'error': '暂无数据'
            }), 404
        
        return jsonify({
            'success': True,
            'data': CACHE['data']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("恐慌清洗指标监控API")
    print("="*60)
    print("访问: http://0.0.0.0:5004/api/panic-wash")
    print("="*60)
    
    # 启动后台更新线程
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    print("✅ 后台更新线程已启动")
    
    app.run(host='0.0.0.0', port=5004, debug=False)
