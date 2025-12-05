#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据读取器 V5
使用Playwright自动从Google Drive读取最新数据
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import time

def get_panic_wash_data_sync():
    """
    从Google Drive读取最新的恐慌清洗数据（同步方法）
    """
    folder_url = "https://drive.google.com/drive/folders/1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ"
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            # 1. 访问文件夹
            page.goto(folder_url, timeout=60000)
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            # 2. 进入今天的文件夹
            page.locator(f'[role="row"]:has-text("{today}")').first.dblclick(timeout=10000)
            time.sleep(5)
            
            # 3. 打开恐慌清洗.txt
            page.locator('[role="row"]:has-text("恐慌清洗.txt")').first.dblclick(timeout=10000)
            time.sleep(8)
            
            # 4. 读取内容
            content = None
            frames = page.frames
            
            for frame in frames:
                try:
                    text = frame.inner_text('body', timeout=5000)
                    if '|' in text and '多头' in text:
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if '|' in line and '-' in line and ('红' in line or '黄' in line or '绿' in line):
                                if len(line) < 200 and line.count('|') >= 1:
                                    content = line
                                    break
                        if content:
                            break
                except:
                    continue
            
            browser.close()
            
            if content:
                # 解析数据: 10.5-绿|4-多头主升区间-103676-3.17-98.71-2025-12-03 18:04:42
                parts = content.split('|')
                
                panic_indicator = parts[0]  # 10.5-绿
                panic_parts = panic_indicator.split('-')
                panic_value = panic_parts[0] if len(panic_parts) > 0 else ""
                panic_color = panic_parts[1] if len(panic_parts) > 1 else ""
                
                remaining = parts[1] if len(parts) > 1 else ""
                detail_parts = remaining.split('-')
                
                data = {
                    'panic_indicator': panic_indicator,
                    'panic_color': panic_color,
                    'trend_rating': detail_parts[0] if len(detail_parts) > 0 else "",
                    'market_zone': detail_parts[1] if len(detail_parts) > 1 else "",
                    'liquidation_24h_people': detail_parts[2] if len(detail_parts) > 2 else "",
                    'liquidation_24h_amount': detail_parts[3] if len(detail_parts) > 3 else "",
                    'total_position': detail_parts[4] if len(detail_parts) > 4 else "",
                    'update_time': '-'.join(detail_parts[5:]) if len(detail_parts) > 5 else "",
                    'success': True
                }
                
                print(f"✅ 成功从Google Drive读取数据: {data['panic_indicator']} @ {data['update_time']}")
                return data
            else:
                print("❌ 未能读取到文件内容")
                return None
                
    except Exception as e:
        print(f"❌ Google Drive读取失败: {str(e)}")
        return None

if __name__ == '__main__':
    print("="*70)
    print("🧪 测试Google Drive数据读取")
    print("="*70)
    
    data = get_panic_wash_data_sync()
    
    if data:
        print("\n✅ 数据获取成功:")
        print(f"📊 恐慌指标: {data['panic_indicator']}")
        print(f"📈 趋势评级: {data['trend_rating']}")
        print(f"🎯 市场区间: {data['market_zone']}")
        print(f"💰 全网持仓量: {data['total_position']}亿")
        print(f"⏰ 更新时间: {data['update_time']}")
    else:
        print("\n❌ 数据获取失败")
