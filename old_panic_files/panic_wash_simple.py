#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据读取器 - 简化版
直接返回模拟数据用于测试
"""

from datetime import datetime
import pytz

def get_panic_wash_data_sync():
    """
    获取恐慌清洗数据（同步版本，用于快速测试）
    TODO: 实际部署时需要实现真实的Google Drive读取
    """
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    # 返回模拟数据用于展示
    data = {
        'panic_indicator': '10.77-绿',
        'trend_rating': '5',
        'market_zone': '多头主升区间',
        'liquidation_24h_people': '99305',
        'liquidation_24h_amount': '2.26',
        'total_position': '92.18',
        'update_time': now.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"✅ 返回模拟数据（更新时间: {data['update_time']}）")
    return data

def parse_panic_wash_data(content):
    """解析恐慌清洗数据"""
    try:
        import re
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            line_clean = re.sub(r'<[^>]+>', '', line).strip()
            
            if not line_clean or '恐慌清洗指标|趋势评级' in line_clean:
                continue
            
            if '|' in line_clean and '-' in line_clean:
                parts = line_clean.split('|')
                if len(parts) >= 2:
                    panic_indicator = parts[0].strip()
                    
                    if not panic_indicator or not panic_indicator[0].isdigit():
                        continue
                    
                    other_data = parts[1].strip()
                    sub_parts = other_data.split('-')
                    
                    if len(sub_parts) >= 7:
                        data = {
                            'panic_indicator': panic_indicator,
                            'trend_rating': sub_parts[0],
                            'market_zone': sub_parts[1],
                            'liquidation_24h_people': sub_parts[2],
                            'liquidation_24h_amount': sub_parts[3],
                            'total_position': sub_parts[4],
                            'update_time': f"{sub_parts[5]} {sub_parts[6]}"
                        }
                        return data
        
        return None
    except Exception as e:
        print(f"解析错误: {e}")
        return None

if __name__ == '__main__':
    result = get_panic_wash_data_sync()
    if result:
        print('\n数据获取成功！')
        for key, value in result.items():
            print(f'  {key}: {value}')
    else:
        print('\n数据获取失败')
