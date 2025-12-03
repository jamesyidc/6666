#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据读取器 V3
从Google Drive共享链接读取实时数据
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import pytz
import re

async def get_panic_wash_data_from_gdrive():
    """从Google Drive读取恐慌清洗数据"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    today = now.strftime('%Y-%m-%d')
    
    print(f"{'='*70}")
    print(f"📡 从Google Drive获取恐慌清洗指标数据")
    print(f"{'='*70}")
    print(f"⏰ 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 目标文件夹: {today}")
    print(f"{'='*70}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # 1. 访问根文件夹
            url = "https://drive.google.com/drive/folders/1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ"
            print(f"1️⃣  访问Google Drive根文件夹...")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # 2. 查找今天日期的文件夹
            print(f"2️⃣  查找文件夹: {today}...")
            
            # 尝试多种选择器
            folder_selectors = [
                f'[data-tooltip*="{today}"]',
                f'div[data-tooltip="{today}"]',
                f'[aria-label*="{today}"]',
            ]
            
            folder_found = False
            for selector in folder_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"   ✅ 找到文件夹 (使用选择器: {selector})")
                        await elements[0].dblclick()
                        folder_found = True
                        break
                except:
                    continue
            
            if not folder_found:
                print(f"   ❌ 未找到 {today} 文件夹")
                return None
            
            await asyncio.sleep(4)
            
            # 3. 查找并打开 恐慌清洗.txt
            print(f"3️⃣  查找文件: 恐慌清洗.txt...")
            
            file_selectors = [
                '[data-tooltip*="恐慌清洗.txt"]',
                '[aria-label*="恐慌清洗.txt"]',
                'div[data-tooltip="恐慌清洗.txt"]',
            ]
            
            file_found = False
            for selector in file_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"   ✅ 找到文件 (使用选择器: {selector})")
                        await elements[0].click()
                        file_found = True
                        break
                except:
                    continue
            
            if not file_found:
                print(f"   ❌ 未找到 恐慌清洗.txt 文件")
                return None
            
            await asyncio.sleep(3)
            
            # 4. 尝试读取预览内容
            print(f"4️⃣  读取文件内容...")
            
            # 方法1: 尝试从预览面板读取
            preview_selectors = [
                '.preview-content',
                '.docs-text-content',
                'pre',
                '[role="textbox"]',
            ]
            
            for selector in preview_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        text = await element.inner_text()
                        if text and len(text) > 10:
                            print(f"   ✅ 从预览面板获取数据 (长度: {len(text)})")
                            parsed = parse_panic_wash_content(text)
                            if parsed:
                                return parsed
                except:
                    continue
            
            # 方法2: 从页面HTML中提取
            print(f"   🔄 尝试从页面HTML提取...")
            content = await page.content()
            
            # 查找包含数据的部分
            if '恐慌清洗指标' in content or '多头主升区间' in content:
                parsed = parse_panic_wash_content(content)
                if parsed:
                    print(f"   ✅ 从HTML提取成功")
                    return parsed
            
            # 方法3: 尝试打开文件到新标签页
            print(f"   🔄 尝试在新标签页打开文件...")
            try:
                # 右键点击文件
                await elements[0].click(button='right')
                await asyncio.sleep(1)
                
                # 点击"在新标签页中打开"
                open_button = await page.locator('text="在新标签页中打开"').first
                if open_button:
                    await open_button.click()
                    await asyncio.sleep(3)
                    
                    # 切换到新标签页
                    pages = context.pages
                    if len(pages) > 1:
                        new_page = pages[-1]
                        await new_page.wait_for_load_state('networkidle')
                        content = await new_page.content()
                        parsed = parse_panic_wash_content(content)
                        if parsed:
                            print(f"   ✅ 从新标签页提取成功")
                            return parsed
            except:
                pass
            
            print("   ❌ 所有读取方法均失败")
            return None
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()

def parse_panic_wash_content(content):
    """
    解析恐慌清洗数据内容
    格式: 10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
    """
    try:
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', content)
        
        # 查找数据行（包含数字和竖线分隔符的行）
        pattern = r'(\d+\.?\d*-[^|]+)\|(\d+)-([^-]+)-(\d+)-([\d.]+)-([\d.]+)-(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
        
        matches = re.findall(pattern, text)
        
        if matches:
            # 取第一个匹配（最新的数据）
            match = matches[0]
            
            data = {
                'panic_indicator': match[0],  # 10.77-绿
                'trend_rating': match[1],     # 5
                'market_zone': match[2],      # 多头主升区间
                'liquidation_24h_people': match[3],  # 99305
                'liquidation_24h_amount': match[4],  # 2.26
                'total_position': match[5],   # 92.18
                'update_time': match[6]       # 2025-12-02 20:58:50
            }
            
            print(f"\n{'='*70}")
            print(f"✅ 成功解析数据:")
            print(f"{'='*70}")
            print(f"📊 恐慌指标: {data['panic_indicator']}")
            print(f"📈 趋势评级: {data['trend_rating']}")
            print(f"🎯 市场区间: {data['market_zone']}")
            print(f"👥 24h爆仓人数: {data['liquidation_24h_people']}")
            print(f"💸 24h爆仓金额: {data['liquidation_24h_amount']}")
            print(f"💰 全网持仓量: {data['total_position']}亿")
            print(f"⏰ 更新时间: {data['update_time']}")
            print(f"{'='*70}\n")
            
            return data
        
        # 如果上面的方法失败，尝试按行解析
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if '|' in line and '-' in line and not line.startswith('恐慌清洗指标'):
                # 尝试解析这一行
                parts = line.split('|')
                if len(parts) >= 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    # 右边部分用 - 分割
                    right_parts = right.split('-')
                    if len(right_parts) >= 7:
                        data = {
                            'panic_indicator': left,
                            'trend_rating': right_parts[0],
                            'market_zone': right_parts[1],
                            'liquidation_24h_people': right_parts[2],
                            'liquidation_24h_amount': right_parts[3],
                            'total_position': right_parts[4],
                            'update_time': f"{right_parts[5]} {right_parts[6]}"
                        }
                        
                        print(f"\n{'='*70}")
                        print(f"✅ 成功解析数据 (按行方式):")
                        print(f"{'='*70}")
                        for key, value in data.items():
                            print(f"   {key}: {value}")
                        print(f"{'='*70}\n")
                        
                        return data
        
        return None
        
    except Exception as e:
        print(f"❌ 解析错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    # 测试数据读取
    result = asyncio.run(get_panic_wash_data_from_gdrive())
    
    if result:
        print('\n' + '='*70)
        print('✅ 数据获取成功！')
        print('='*70)
    else:
        print('\n' + '='*70)
        print('❌ 数据获取失败')
        print('='*70)
