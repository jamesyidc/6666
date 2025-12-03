#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据读取器 V2
使用gdrive_home_data_reader复用已有的Google Drive访问逻辑
"""

import asyncio
import sys
import os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def get_panic_wash_data():
    """获取恐慌清洗数据"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    today = now.strftime('%Y-%m-%d')
    
    print(f"{'='*60}")
    print(f"获取恐慌清洗指标数据 V2")
    print(f"{'='*60}")
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标文件夹: {today}")
    print(f"目标文件: 恐慌清洗.txt")
    print(f"{'='*60}\n")
    
    try:
        # 复用 gdrive_home_data_reader 的访问逻辑
        from gdrive_home_data_reader import get_page_with_retry
        
        # 根文件夹URL
        folder_url = "https://drive.google.com/drive/folders/1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ"
        
        print(f"1. 访问Google Drive根文件夹...")
        page = await get_page_with_retry(folder_url)
        
        if not page:
            print("❌ 无法访问Google Drive")
            return None
        
        try:
            print(f"2. 等待页面加载...")
            await asyncio.sleep(3)
            
            # 查找今天日期的文件夹
            print(f"3. 查找文件夹: {today}")
            
            # 尝试多种选择器
            folder_selectors = [
                f'[data-tooltip="{today}"]',
                f'div[data-name="{today}"]',
                f'div:has-text("{today}")',
            ]
            
            folder_found = False
            for selector in folder_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"✅ 找到文件夹（选择器: {selector}）")
                        await elements[0].dblclick(timeout=5000)
                        folder_found = True
                        break
                except:
                    continue
            
            if not folder_found:
                print(f"❌ 未找到文件夹: {today}")
                return None
            
            print(f"4. 等待文件夹内容加载...")
            await asyncio.sleep(4)
            
            # 查找恐慌清洗.txt文件
            print(f"5. 查找文件: 恐慌清洗.txt")
            
            file_selectors = [
                '[data-tooltip*="恐慌清洗.txt"]',
                'div[data-name*="恐慌清洗"]',
                'div:has-text("恐慌清洗.txt")',
            ]
            
            file_found = False
            for selector in file_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"✅ 找到文件（选择器: {selector}）")
                        await elements[0].click(timeout=5000)
                        file_found = True
                        break
                except:
                    continue
            
            if not file_found:
                print(f"❌ 未找到文件: 恐慌清洗.txt")
                return None
            
            print(f"6. 等待文件预览加载...")
            await asyncio.sleep(3)
            
            # 尝试从预览区域读取文本
            print(f"7. 读取文件内容...")
            
            # 尝试多种方式读取内容
            content = None
            
            # 方法1: 尝试从预览框架读取
            frames = page.frames
            for frame in frames:
                try:
                    frame_content = await frame.content()
                    if '多头主升区间' in frame_content or '恐慌清洗指标' in frame_content:
                        print(f"✅ 从Frame中找到数据")
                        content = frame_content
                        break
                    
                    # 尝试从文本元素读取
                    text_elements = await frame.locator('pre, div[role="textbox"]').all()
                    for elem in text_elements:
                        text = await elem.inner_text()
                        if text and len(text) > 10:
                            print(f"✅ 从文本元素读取到数据（长度: {len(text)}）")
                            content = text
                            break
                    
                    if content:
                        break
                except:
                    continue
            
            # 方法2: 尝试从主页面读取
            if not content:
                try:
                    page_content = await page.content()
                    if '多头主升区间' in page_content or '恐慌清洗指标' in page_content:
                        print(f"✅ 从主页面中找到数据")
                        content = page_content
                except:
                    pass
            
            if not content:
                print("❌ 未能读取到文件内容")
                return None
            
            # 解析数据
            result = parse_panic_wash_data(content)
            return result
            
        finally:
            # 关闭浏览器
            try:
                await page.context.browser.close()
            except:
                pass
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def parse_panic_wash_data(content):
    """解析恐慌清洗数据"""
    try:
        # 数据格式：10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
        # 查找数据行（不是标题行）
        lines = content.split('\n')
        
        print(f"\n开始解析数据（总行数: {len(lines)}）...")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 跳过空行和标题行
            if not line or '恐慌清洗指标|趋势评级' in line:
                continue
            
            # 查找包含数据的行
            # 格式：数字-颜色|数字-文字-数字-数字-数字-日期 时间
            if '|' in line and '-' in line:
                # 移除HTML标签
                import re
                line_clean = re.sub(r'<[^>]+>', '', line)
                line_clean = line_clean.strip()
                
                if not line_clean:
                    continue
                
                parts = line_clean.split('|')
                if len(parts) >= 2:
                    # 第一部分：恐慌清洗指标（例如：10.77-绿）
                    panic_indicator = parts[0].strip()
                    
                    # 检查是否是有效的指标（应该是数字开头）
                    if not panic_indicator[0].isdigit():
                        continue
                    
                    # 第二部分：其他数据（例如：5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50）
                    other_data = parts[1].strip()
                    sub_parts = other_data.split('-')
                    
                    if len(sub_parts) >= 7:
                        try:
                            data = {
                                'panic_indicator': panic_indicator,  # 10.77-绿
                                'trend_rating': sub_parts[0],  # 5
                                'market_zone': sub_parts[1],  # 多头主升区间
                                'liquidation_24h_people': sub_parts[2],  # 99305
                                'liquidation_24h_amount': sub_parts[3],  # 2.26
                                'total_position': sub_parts[4],  # 92.18
                                'update_time': f"{sub_parts[5]} {sub_parts[6]}"  # 2025-12-02 20:58:50
                            }
                            
                            print(f"\n✅ 解析成功（第{i+1}行）:")
                            print(f"   恐慌清洗指标: {data['panic_indicator']}")
                            print(f"   趋势评级: {data['trend_rating']}")
                            print(f"   市场区间: {data['market_zone']}")
                            print(f"   24h爆仓人数: {data['liquidation_24h_people']}")
                            print(f"   24h爆仓金额: {data['liquidation_24h_amount']}")
                            print(f"   全网持仓量: {data['total_position']}")
                            print(f"   更新时间: {data['update_time']}")
                            
                            return data
                        except Exception as e:
                            print(f"⚠️  解析第{i+1}行失败: {e}")
                            continue
        
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
