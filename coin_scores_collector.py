#!/usr/bin/env python3
"""
币种多空评分数据采集器
从 coin-scores-data.js 采集完整的56字段数据
"""

import sqlite3
import requests
import time
import json
import re
from datetime import datetime
import logging
import pytz

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/coin_scores_collector.log'),
        logging.StreamHandler()
    ]
)

# API URL
API_URL = "https://5026-i6z1n4prnsqw4uzv0af9z-2e77fc33.sandbox.novita.ai/coin-scores-data.js"

class CoinScoresCollector:
    def __init__(self, db_path='crypto_data.db'):
        self.db_path = db_path
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        self.init_database()
    
    def init_database(self):
        """初始化数据库表 - 完整56字段"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                beijing_time TEXT NOT NULL,
                
                -- 多空得分 (12个字段)
                long_score REAL,
                short_score REAL,
                long_score_3m_avg REAL,
                short_score_3m_avg REAL,
                long_score_1h_avg REAL,
                short_score_1h_avg REAL,
                long_score_3h_avg REAL,
                short_score_3h_avg REAL,
                long_score_12h_avg REAL,
                short_score_12h_avg REAL,
                long_score_24h_avg REAL,
                short_score_24h_avg REAL,
                
                -- 多空持仓量 (3个字段)
                long_volume REAL,
                short_volume REAL,
                long_short_ratio REAL,
                
                -- SAR指标 - 5分钟 (6个字段)
                sar_5m REAL,
                sar_5m_quadrant INTEGER,
                price_5m REAL,
                sar_5m_trend TEXT,
                sar_5m_duration INTEGER,
                
                -- SAR指标 - 1小时 (5个字段)
                sar_1h REAL,
                sar_1h_quadrant INTEGER,
                price_1h REAL,
                sar_1h_trend TEXT,
                sar_1h_duration INTEGER,
                
                -- RSI指标 (2个字段)
                rsi_5m REAL,
                rsi_1h REAL,
                
                -- 布林带 - 5分钟 (4个字段)
                bb_upper_5m REAL,
                bb_middle_5m REAL,
                bb_lower_5m REAL,
                bb_position_5m REAL,
                
                -- 布林带 - 1小时 (4个字段)
                bb_upper_1h REAL,
                bb_middle_1h REAL,
                bb_lower_1h REAL,
                bb_position_1h REAL,
                
                -- 统计计数 (2个字段)
                long_count INTEGER,
                short_count INTEGER,
                
                -- 元数据
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_source TEXT DEFAULT 'coin-scores-data.js',
                
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_time ON coin_scores(symbol, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_beijing_time ON coin_scores(beijing_time DESC)')
        
        conn.commit()
        conn.close()
        logging.info("✅ 数据库初始化完成 (56字段)")
    
    def fetch_data(self):
        """从API获取数据"""
        try:
            logging.info(f"正在从API获取数据: {API_URL}")
            response = requests.get(API_URL, timeout=30)
            
            if response.status_code != 200:
                logging.error(f"❌ API请求失败: {response.status_code}")
                return None
            
            # 解析JSONP响应
            content = response.text
            # 提取 CoinScoresData({...}) 中的JSON部分
            match = re.search(r'CoinScoresData\((.*)\)', content, re.DOTALL)
            if not match:
                logging.error("❌ 无法解析JSONP响应")
                return None
            
            json_data = match.group(1)
            data = json.loads(json_data)
            
            if not data.get('success'):
                logging.error(f"❌ API返回失败: {data}")
                return None
            
            logging.info(f"✅ 获取到 {data.get('count', 0)} 个币种数据")
            return data
            
        except Exception as e:
            logging.error(f"❌ 获取数据失败: {e}")
            return None
    
    def save_to_database(self, api_data):
        """保存数据到数据库"""
        if not api_data or 'data' not in api_data:
            logging.warning("⚠️  没有数据需要保存")
            return 0
        
        coins_data = api_data['data']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for coin in coins_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO coin_scores (
                        symbol, timestamp, beijing_time,
                        long_score, short_score,
                        long_score_3m_avg, short_score_3m_avg,
                        long_score_1h_avg, short_score_1h_avg,
                        long_score_3h_avg, short_score_3h_avg,
                        long_score_12h_avg, short_score_12h_avg,
                        long_score_24h_avg, short_score_24h_avg,
                        long_volume, short_volume, long_short_ratio,
                        sar_5m, sar_5m_quadrant, price_5m, sar_5m_trend, sar_5m_duration,
                        sar_1h, sar_1h_quadrant, price_1h, sar_1h_trend, sar_1h_duration,
                        rsi_5m, rsi_1h,
                        bb_upper_5m, bb_middle_5m, bb_lower_5m, bb_position_5m,
                        bb_upper_1h, bb_middle_1h, bb_lower_1h, bb_position_1h,
                        long_count, short_count
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                ''', (
                    coin.get('symbol'),
                    coin.get('timestamp'),
                    coin.get('beijing_time'),
                    coin.get('long_score'),
                    coin.get('short_score'),
                    coin.get('long_score_3m_avg'),
                    coin.get('short_score_3m_avg'),
                    coin.get('long_score_1h_avg'),
                    coin.get('short_score_1h_avg'),
                    coin.get('long_score_3h_avg'),
                    coin.get('short_score_3h_avg'),
                    coin.get('long_score_12h_avg'),
                    coin.get('short_score_12h_avg'),
                    coin.get('long_score_24h_avg'),
                    coin.get('short_score_24h_avg'),
                    coin.get('long_volume'),
                    coin.get('short_volume'),
                    coin.get('long_short_ratio'),
                    coin.get('sar_5m'),
                    coin.get('sar_5m_quadrant'),
                    coin.get('price_5m'),
                    coin.get('sar_5m_trend'),
                    coin.get('sar_5m_duration'),
                    coin.get('sar_1h'),
                    coin.get('sar_1h_quadrant'),
                    coin.get('price_1h'),
                    coin.get('sar_1h_trend'),
                    coin.get('sar_1h_duration'),
                    coin.get('rsi_5m'),
                    coin.get('rsi_1h'),
                    coin.get('bb_upper_5m'),
                    coin.get('bb_middle_5m'),
                    coin.get('bb_lower_5m'),
                    coin.get('bb_position_5m'),
                    coin.get('bb_upper_1h'),
                    coin.get('bb_middle_1h'),
                    coin.get('bb_lower_1h'),
                    coin.get('bb_position_1h'),
                    coin.get('long_count'),
                    coin.get('short_count')
                ))
                saved_count += 1
            except Exception as e:
                logging.error(f"❌ 保存币种 {coin.get('symbol')} 失败: {e}")
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ 成功保存 {saved_count}/{len(coins_data)} 条记录")
        return saved_count
    
    def collect_once(self):
        """执行一次采集"""
        logging.info("=" * 80)
        logging.info("🚀 开始币种评分数据采集 (56字段)")
        logging.info("=" * 80)
        
        api_data = self.fetch_data()
        if not api_data:
            logging.error("❌ 采集失败：无法获取数据")
            return False
        
        saved_count = self.save_to_database(api_data)
        
        logging.info(f"✅ 本次采集完成: {saved_count} 个币种")
        return saved_count > 0

def main():
    """主函数"""
    import sys
    from datetime import datetime
    
    collector = CoinScoresCollector()
    
    if '--once' in sys.argv:
        # 单次采集
        collector.collect_once()
    else:
        # 持续采集 (严格每1分钟)
        while True:
            try:
                start_time = time.time()
                collector.collect_once()
                
                # 计算到下一个整分钟的等待时间
                elapsed = time.time() - start_time
                wait_time = max(0, 60 - elapsed)
                
                logging.info(f"⏱️  本次采集耗时 {elapsed:.2f}秒，等待 {wait_time:.2f}秒后下次采集...")
                time.sleep(wait_time)
            except KeyboardInterrupt:
                logging.info("👋 用户中断，退出采集")
                break
            except Exception as e:
                logging.error(f"❌ 采集异常: {e}")
                time.sleep(60)  # 出错后等待1分钟再试

if __name__ == '__main__':
    main()
