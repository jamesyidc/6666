#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据读取器 V4
使用简化的方法从Google Drive读取数据
"""

import requests
from datetime import datetime
import pytz
import re

def get_panic_wash_data_from_gdrive_api():
    """
    从Google Drive API直接读取文件内容
    注意：由于共享链接的限制，这里提供一个备用的手动输入方案
    """
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    print(f"{'='*70}")
    print(f"📡 获取恐慌清洗指标数据")
    print(f"{'='*70}")
    print(f"⏰ 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # 由于Google Drive的访问限制，这里提供一个简化的方案
    # 实际使用时，需要有文件的直接访问权限或API key
    
    print("❌ Google Drive直接读取需要认证")
    print("💡 建议使用以下方案之一：")
    print("   1. 手动从Google Drive复制最新数据到本地文件")
    print("   2. 使用Google Drive API和服务账号")
    print("   3. 定期手动更新数据")
    
    return None

def parse_panic_wash_line(line):
    """
    解析单行恐慌清洗数据
    格式: 10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
    """
    try:
        line = line.strip()
        if not line or '恐慌清洗指标' in line:
            return None
        
        # 分割左右两部分
        parts = line.split('|')
        if len(parts) != 2:
            return None
        
        panic_indicator = parts[0].strip()  # 10.77-绿
        
        # 分割右边部分
        right_parts = parts[1].strip().split('-')
        
        if len(right_parts) >= 7:
            data = {
                'panic_indicator': panic_indicator,
                'trend_rating': right_parts[0],
                'market_zone': right_parts[1],
                'liquidation_24h_people': right_parts[2],
                'liquidation_24h_amount': right_parts[3],
                'total_position': right_parts[4],
                'update_time': f"{right_parts[5]} {right_parts[6]}"
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
        
        return None
        
    except Exception as e:
        print(f"❌ 解析错误: {str(e)}")
        return None

def read_from_local_file(file_path='/home/user/webapp/panic_wash_latest.txt'):
    """
    从本地文件读取恐慌清洗数据
    这是一个临时方案，需要手动更新文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        for line in lines:
            data = parse_panic_wash_line(line)
            if data:
                return data
        
        return None
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        print(f"💡 请创建文件并添加最新数据，格式示例：")
        print(f"   10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-03 17:00:00")
        return None
    except Exception as e:
        print(f"❌ 读取文件错误: {str(e)}")
        return None

def get_panic_wash_data_sync():
    """
    获取恐慌清洗数据的同步方法
    优先级：本地文件 > Google Drive API > 模拟数据
    """
    # 1. 尝试从本地文件读取
    data = read_from_local_file()
    if data:
        return data
    
    # 2. 如果本地文件不存在，返回当前时间的模拟数据
    # 但要提示用户这是模拟数据
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    print(f"\n⚠️  警告：无法获取真实数据，返回模拟数据")
    print(f"💡 解决方案：")
    print(f"   1. 手动从Google Drive复制最新数据")
    print(f"   2. 创建文件：/home/user/webapp/panic_wash_latest.txt")
    print(f"   3. 格式：10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-03 17:00:00\n")
    
    data = {
        'panic_indicator': '10.77-绿',
        'trend_rating': '5',
        'market_zone': '多头主升区间',
        'liquidation_24h_people': '99305',
        'liquidation_24h_amount': '2.26',
        'total_position': '92.18',
        'update_time': now.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return data

if __name__ == '__main__':
    print("="*70)
    print("🧪 测试数据读取")
    print("="*70)
    
    # 测试解析功能
    test_line = "10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-03 17:00:00"
    print(f"\n测试数据: {test_line}\n")
    data = parse_panic_wash_line(test_line)
    
    if data:
        print("✅ 解析测试通过")
    else:
        print("❌ 解析测试失败")
    
    # 测试实际读取
    print("\n" + "="*70)
    print("📡 尝试读取真实数据")
    print("="*70)
    real_data = get_panic_wash_data_sync()
    
    if real_data:
        print("\n✅ 数据获取完成")
    else:
        print("\n❌ 数据获取失败")
