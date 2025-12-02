#!/usr/bin/env python3
"""
虚拟币系统监控 - Google Drive数据读取模块
"""

import re
from datetime import datetime
import pytz
from typing import Dict, Optional
import urllib.request
import urllib.parse

class MonitorDataReader:
    def __init__(self):
        """初始化数据读取器"""
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        # Google Drive共享文件夹ID
        self.folder_id = '1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ'
    
    def get_today_folder_url(self) -> str:
        """获取今天日期的文件夹名称（北京时间）"""
        now = datetime.now(self.beijing_tz)
        today = now.strftime('%Y-%m-%d')
        return today
    
    def read_signal_data(self, content: str) -> Optional[Dict]:
        """
        解析信号.txt内容
        格式: 126|0|0|0|2025-12-02 20:56:01
        字段: 做空|变化|做多|变化|时间
        """
        try:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                
                # 解析数据行
                parts = line.split('|')
                if len(parts) >= 5:
                    return {
                        'short': parts[0].strip(),
                        'short_change': parts[1].strip(),
                        'long': parts[2].strip(),
                        'long_change': parts[3].strip(),
                        'update_time': parts[4].strip()
                    }
            
            return None
        except Exception as e:
            print(f"❌ 解析信号数据失败: {e}")
            return None
    
    def read_panic_data(self, content: str) -> Optional[Dict]:
        """
        解析恐慌清洗.txt内容
        格式: 10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
        字段: 恐慌清洗指标|趋势评级-市场区间-24h爆仓人数-24h爆仓金额-全网持仓量-时间
        """
        try:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                
                # 解析数据行
                parts = line.split('|')
                if len(parts) >= 2:
                    # 第一部分: 恐慌清洗指标
                    panic_indicator = parts[0].strip()
                    
                    # 第二部分: 其他数据（用-分隔）
                    # 格式: 5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
                    other_data = parts[1].strip()
                    
                    # 使用正则表达式提取最后的时间部分
                    import re
                    time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})$', other_data)
                    if time_match:
                        update_time = time_match.group(1)
                        # 去掉时间后的剩余部分
                        data_without_time = other_data[:time_match.start()].rstrip('-')
                        
                        # 分割剩余数据
                        other_parts = data_without_time.split('-')
                        
                        if len(other_parts) >= 5:
                            return {
                                'panic_indicator': panic_indicator,
                                'trend_rating': other_parts[0].strip(),
                                'market_zone': other_parts[1].strip(),
                                'liquidation_24h_count': other_parts[2].strip(),
                                'liquidation_24h_amount': other_parts[3].strip(),
                                'total_position': other_parts[4].strip(),
                                'update_time': update_time
                            }
            
            return None
        except Exception as e:
            print(f"❌ 解析恐慌清洗数据失败: {e}")
            return None
    
    def get_demo_signal_data(self) -> Dict:
        """获取演示信号数据"""
        now = datetime.now(self.beijing_tz)
        return {
            'short': '126',
            'short_change': '0',
            'long': '0',
            'long_change': '0',
            'update_time': now.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_demo_panic_data(self) -> Dict:
        """获取演示恐慌清洗数据"""
        now = datetime.now(self.beijing_tz)
        return {
            'panic_indicator': '10.77-绿',
            'trend_rating': '5',
            'market_zone': '多头主升区间',
            'liquidation_24h_count': '99305',
            'liquidation_24h_amount': '2.26',
            'total_position': '92.18',
            'update_time': now.strftime('%Y-%m-%d %H:%M:%S')
        }

if __name__ == '__main__':
    reader = MonitorDataReader()
    
    print("测试数据解析:")
    print("\n1. 信号数据:")
    signal_content = "126|0|0|0|2025-12-02 20:56:01"
    signal_data = reader.read_signal_data(signal_content)
    print(signal_data)
    
    print("\n2. 恐慌清洗数据:")
    panic_content = "10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50"
    panic_data = reader.read_panic_data(panic_content)
    print(panic_data)
