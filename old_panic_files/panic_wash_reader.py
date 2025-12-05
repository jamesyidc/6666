#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据读取器
从Google Drive获取最新的恐慌清洗数据
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import pytz
import re

async def get_panic_wash_data():
    """获取恐慌清洗数据"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    today = now.strftime('%Y-%m-%d')
    
    print(f"{'='*60}")
    print(f"获取恐慌清洗指标数据")
    print(f"{'='*60}")
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # 1. 访问根文件夹
            url = "https://drive.google.com/drive/folders/1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ"
            print(f"1. 访问根文件夹...")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)
            
            # 2. 进入今天的文件夹
            print(f"2. 进入 {today} 文件夹...")
            folder_selector = f'[data-tooltip*="{today}"]'
            await page.locator(folder_selector).first.dblclick()
            await asyncio.sleep(4)
            
            # 3. 查找并打开 恐慌清洗.txt
            print(f"3. 查找 恐慌清洗.txt 文件...")
            file_selector = '[data-tooltip*="恐慌清洗.txt"]'
            await page.locator(file_selector).first.click()
            await asyncio.sleep(3)
            
            # 4. 读取文件内容
            print(f"4. 读取文件内容...")
            frames = page.frames
            
            for i, frame in enumerate(frames):
                try:
                    frame_url = frame.url
                    if 'drive.google.com' in frame_url:
                        content = await frame.content()
                        
                        # 提取文本内容（可能在不同的元素中）
                        # 尝试多种选择器
                        text_selectors = [
                            'pre',
                            'div[role="textbox"]',
                            '.docs-texteventtarget-iframe',
                        ]
                        
                        for selector in text_selectors:
                            try:
                                element = await frame.query_selector(selector)
                                if element:
                                    text = await element.inner_text()
                                    if text and len(text) > 10:
                                        print(f"✅ Frame {i} 获取到数据 (长度: {len(text)})")
                                        return parse_panic_wash_data(text)
                            except:
                                continue
                        
                        # 如果上面的方法都失败，尝试直接从HTML中提取
                        if '多头主升区间' in content or '恐慌清洗指标' in content:
                            print(f"✅ Frame {i} 从HTML中提取数据")
                            return parse_panic_wash_data(content)
                            
                except Exception as e:
                    continue
            
            print("❌ 未能读取到文件内容")
            return None
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()

def parse_panic_wash_data(content):
    """解析恐慌清洗数据"""
    try:
        # 数据格式：10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
        # 查找数据行（不是标题行）
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # 跳过空行和标题行
            if not line or '恐慌清洗指标|趋势评级' in line:
                continue
            
            # 查找包含数据的行
            if '|' in line and '-' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    # 第一部分：恐慌清洗指标（例如：10.77-绿）
                    panic_indicator = parts[0].strip()
                    
                    # 第二部分：其他数据（例如：5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50）
                    other_data = parts[1].strip()
                    sub_parts = other_data.split('-')
                    
                    if len(sub_parts) >= 7:
                        data = {
                            'panic_indicator': panic_indicator,  # 10.77-绿
                            'trend_rating': sub_parts[0],  # 5
                            'market_zone': sub_parts[1],  # 多头主升区间
                            'liquidation_24h_people': sub_parts[2],  # 99305
                            'liquidation_24h_amount': sub_parts[3],  # 2.26
                            'total_position': sub_parts[4],  # 92.18
                            'update_time': f"{sub_parts[5]} {sub_parts[6]}"  # 2025-12-02 20:58:50
                        }
                        
                        print(f"\n✅ 解析成功:")
                        print(f"   恐慌清洗指标: {data['panic_indicator']}")
                        print(f"   趋势评级: {data['trend_rating']}")
                        print(f"   市场区间: {data['market_zone']}")
                        print(f"   24h爆仓人数: {data['liquidation_24h_people']}")
                        print(f"   24h爆仓金额: {data['liquidation_24h_amount']}")
                        print(f"   全网持仓量: {data['total_position']}")
                        print(f"   更新时间: {data['update_time']}")
                        
                        return data
        
        print("⚠️  未找到有效的数据行")
        return None
        
    except Exception as e:
        print(f"❌ 解析错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = asyncio.run(get_panic_wash_data())
    if result:
        print(f"\n{'='*60}")
        print("数据获取成功！")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("数据获取失败")
        print(f"{'='*60}")
