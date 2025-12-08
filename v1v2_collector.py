#!/usr/bin/env python3
"""
V1V2成交量数据采集器
数据源: https://5027-i6z1n4prnsqw4uzv0af9z-2e77fc33.sandbox.novita.ai/v1v2-data.js
"""

import requests
import sqlite3
import time
import logging
from datetime import datetime
import pytz
import re
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/v1v2_collector.log'),
        logging.StreamHandler()
    ]
)

# 数据源URL
DATA_URL = 'https://5027-i6z1n4prnsqw4uzv0af9z-2e77fc33.sandbox.novita.ai/v1v2-data.js'

# 数据库路径
DB_PATH = 'v1v2_volume.db'

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')


class V1V2Collector:
    """V1V2成交量数据采集器"""
    
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建成交量数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS v1v2_volumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                volume REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                beijing_time TEXT NOT NULL,
                update_time TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
            ON v1v2_volumes(symbol, timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_beijing_time 
            ON v1v2_volumes(beijing_time DESC)
        ''')
        
        conn.commit()
        conn.close()
        
        logging.info("✅ V1V2数据库初始化完成")
    
    def fetch_data(self):
        """从数据源获取数据"""
        try:
            response = requests.get(DATA_URL, timeout=10)
            response.raise_for_status()
            
            # 解析JavaScript变量
            content = response.text
            
            # 提取JSON数据（从 var v1v2VolumeData = {...} 中提取）
            match = re.search(r'var\s+v1v2VolumeData\s*=\s*({[\s\S]*?});', content)
            if not match:
                logging.error("❌ 无法从响应中提取数据")
                return None
            
            json_str = match.group(1)
            data = json.loads(json_str)
            
            if not data.get('success'):
                logging.error("❌ API返回失败")
                return None
            
            volumes = data.get('volumes', [])
            logging.info(f"✅ 获取到 {len(volumes)} 个币种的成交量数据")
            
            return volumes
            
        except Exception as e:
            logging.error(f"❌ 数据获取失败: {e}")
            return None
    
    def save_to_database(self, volumes):
        """保存数据到数据库"""
        if not volumes:
            return 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for item in volumes:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO v1v2_volumes 
                    (symbol, volume, timestamp, beijing_time, update_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    item['symbol'],
                    item['volume'],
                    item['timestamp'],
                    item['update_time'],
                    item['update_time']
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                    
            except Exception as e:
                logging.error(f"❌ 保存币种 {item.get('symbol')} 失败: {e}")
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ 成功保存 {saved_count}/{len(volumes)} 条记录")
        return saved_count
    
    def collect_once(self):
        """执行一次采集"""
        logging.info("=" * 80)
        logging.info("🚀 开始V1V2成交量数据采集")
        logging.info("=" * 80)
        logging.info(f"正在从API获取数据: {DATA_URL}")
        
        volumes = self.fetch_data()
        if not volumes:
            logging.error("❌ 采集失败：无法获取数据")
            return False
        
        saved_count = self.save_to_database(volumes)
        
        logging.info(f"✅ 本次采集完成: {saved_count} 个币种")
        return saved_count > 0


def main():
    """主函数"""
    import sys
    
    collector = V1V2Collector()
    
    if '--once' in sys.argv:
        # 单次采集
        collector.collect_once()
    else:
        # 持续采集（每5分钟）
        while True:
            try:
                start_time = time.time()
                collector.collect_once()
                
                # 计算到下一个5分钟的等待时间
                elapsed = time.time() - start_time
                wait_time = max(0, 300 - elapsed)  # 5分钟 = 300秒
                
                logging.info(f"⏱️  本次采集耗时 {elapsed:.2f}秒，等待 {wait_time:.2f}秒后下次采集...")
                time.sleep(wait_time)
            except KeyboardInterrupt:
                logging.info("👋 用户中断，退出采集")
                break
            except Exception as e:
                logging.error(f"❌ 采集异常: {e}")
                time.sleep(300)  # 出错后等待5分钟再试


if __name__ == '__main__':
    main()
