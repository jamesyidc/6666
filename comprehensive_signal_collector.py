#!/usr/bin/env python3
"""
综合交易信号采集器 - 完整版
采集所有56个字段的完整数据
"""

import sqlite3
import requests
import time
import json
from datetime import datetime
import logging
import pytz

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/comprehensive_collector.log'),
        logging.StreamHandler()
    ]
)

# API基础URL
BASE_URL = "https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai"

class ComprehensiveSignalCollector:
    def __init__(self, db_path='crypto_data.db'):
        self.db_path = db_path
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        self.init_database()
    
    def init_database(self):
        """初始化数据库表 - 包含所有56个字段"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprehensive_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                beijing_time TEXT NOT NULL,
                
                -- 多空得分 (16个字段)
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
                
                -- 多空数量 (3个字段)
                long_volume REAL,
                short_volume REAL,
                long_short_ratio REAL,
                
                -- SAR趋势 (6个字段)
                sar_5m REAL,
                sar_5m_quadrant INTEGER,
                price_5m REAL,
                sar_1h REAL,
                sar_1h_quadrant INTEGER,
                price_1h REAL,
                
                -- RSI指标 (2个字段)
                rsi_5m REAL,
                rsi_1h REAL,
                
                -- 布林带 (10个字段)
                bb_upper_5m REAL,
                bb_middle_5m REAL,
                bb_lower_5m REAL,
                bb_position_5m REAL,
                bb_upper_1h REAL,
                bb_middle_1h REAL,
                bb_lower_1h REAL,
                bb_position_1h REAL,
                
                -- 其他扩展字段 (预留给MACD、KDJ等)
                macd_5m REAL,
                macd_signal_5m REAL,
                macd_hist_5m REAL,
                macd_1h REAL,
                macd_signal_1h REAL,
                macd_hist_1h REAL,
                
                kdj_k_5m REAL,
                kdj_d_5m REAL,
                kdj_j_5m REAL,
                kdj_k_1h REAL,
                kdj_d_1h REAL,
                kdj_j_1h REAL,
                
                -- 元数据
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_source TEXT,
                raw_data TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_time ON comprehensive_signals(symbol, timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_beijing_time ON comprehensive_signals(beijing_time DESC)')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_record ON comprehensive_signals(symbol, timestamp)')
        
        conn.commit()
        conn.close()
        logging.info("✅ 综合信号数据库初始化完成 (56+字段)")
    
    def fetch_comprehensive_data(self):
        """从多个API端点获取综合数据"""
        try:
            beijing_time = datetime.now(self.beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
            timestamp = int(time.time() * 1000)
            
            collected_coins = []
            
            # 1. 获取K线汇总数据 (包含多空得分、SAR、RSI等)
            try:
                summary_url = f"{BASE_URL}/api/kline/summary"
                logging.info(f"正在获取K线汇总数据...")
                resp = requests.get(summary_url, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'data' in data:
                        for coin_data in data['data']:
                            coin_record = self.parse_kline_data(coin_data, timestamp, beijing_time)
                            if coin_record:
                                collected_coins.append(coin_record)
                        logging.info(f"✅ K线数据: 获取到 {len(collected_coins)} 个币种")
            except Exception as e:
                logging.error(f"❌ 获取K线数据失败: {e}")
            
            # 2. 获取持仓数据 (多空数量)
            try:
                position_url = f"{BASE_URL}/api/positions"
                logging.info(f"正在获取持仓数据...")
                resp = requests.get(position_url, timeout=30)
                if resp.status_code == 200:
                    position_data = resp.json()
                    self.merge_position_data(collected_coins, position_data)
                    logging.info(f"✅ 持仓数据: 合并完成")
            except Exception as e:
                logging.error(f"❌ 获取持仓数据失败: {e}")
            
            # 3. 获取技术指标数据 (布林带、MACD、KDJ)
            try:
                indicators_url = f"{BASE_URL}/api/indicators"
                logging.info(f"正在获取技术指标数据...")
                resp = requests.get(indicators_url, timeout=30)
                if resp.status_code == 200:
                    indicators_data = resp.json()
                    self.merge_indicators_data(collected_coins, indicators_data)
                    logging.info(f"✅ 技术指标: 合并完成")
            except Exception as e:
                logging.error(f"❌ 获取技术指标失败: {e}")
            
            return collected_coins
            
        except Exception as e:
            logging.error(f"❌ 数据采集失败: {e}")
            return []
    
    def parse_kline_data(self, coin_data, timestamp, beijing_time):
        """解析K线数据"""
        try:
            symbol = coin_data.get('symbol', '').upper()
            if not symbol:
                return None
            
            record = {
                'symbol': symbol,
                'timestamp': timestamp,
                'beijing_time': beijing_time,
                
                # 多空得分 - 从K线数据中提取
                'long_score': coin_data.get('long_score'),
                'short_score': coin_data.get('short_score'),
                'long_score_3m_avg': coin_data.get('long_score_3m_avg'),
                'short_score_3m_avg': coin_data.get('short_score_3m_avg'),
                'long_score_1h_avg': coin_data.get('long_score_1h_avg'),
                'short_score_1h_avg': coin_data.get('short_score_1h_avg'),
                'long_score_3h_avg': coin_data.get('long_score_3h_avg'),
                'short_score_3h_avg': coin_data.get('short_score_3h_avg'),
                'long_score_12h_avg': coin_data.get('long_score_12h_avg'),
                'short_score_12h_avg': coin_data.get('short_score_12h_avg'),
                'long_score_24h_avg': coin_data.get('long_score_24h_avg'),
                'short_score_24h_avg': coin_data.get('short_score_24h_avg'),
                
                # SAR趋势
                'sar_5m': coin_data.get('sar_5m'),
                'sar_5m_quadrant': coin_data.get('sar_5m_quadrant'),
                'price_5m': coin_data.get('price_5m'),
                'sar_1h': coin_data.get('sar_1h'),
                'sar_1h_quadrant': coin_data.get('sar_1h_quadrant'),
                'price_1h': coin_data.get('price_1h'),
                
                # RSI指标
                'rsi_5m': coin_data.get('rsi_5m'),
                'rsi_1h': coin_data.get('rsi_1h'),
                
                # 布林带
                'bb_upper_5m': coin_data.get('bb_upper_5m'),
                'bb_middle_5m': coin_data.get('bb_middle_5m'),
                'bb_lower_5m': coin_data.get('bb_lower_5m'),
                'bb_position_5m': coin_data.get('bb_position_5m'),
                'bb_upper_1h': coin_data.get('bb_upper_1h'),
                'bb_middle_1h': coin_data.get('bb_middle_1h'),
                'bb_lower_1h': coin_data.get('bb_lower_1h'),
                'bb_position_1h': coin_data.get('bb_position_1h'),
                
                'data_source': 'kline_summary',
                'raw_data': json.dumps(coin_data, ensure_ascii=False)
            }
            
            return record
        except Exception as e:
            logging.error(f"解析K线数据失败: {e}")
            return None
    
    def merge_position_data(self, collected_coins, position_data):
        """合并持仓数据"""
        try:
            if 'data' not in position_data:
                return
            
            # 创建symbol到position的映射
            position_map = {}
            for pos in position_data['data']:
                symbol = pos.get('symbol', '').upper()
                position_map[symbol] = pos
            
            # 合并到已采集的数据
            for coin in collected_coins:
                symbol = coin['symbol']
                if symbol in position_map:
                    pos = position_map[symbol]
                    coin['long_volume'] = pos.get('long_volume')
                    coin['short_volume'] = pos.get('short_volume')
                    coin['long_short_ratio'] = pos.get('long_short_ratio')
        
        except Exception as e:
            logging.error(f"合并持仓数据失败: {e}")
    
    def merge_indicators_data(self, collected_coins, indicators_data):
        """合并技术指标数据"""
        try:
            if 'data' not in indicators_data:
                return
            
            # 创建symbol到indicators的映射
            indicators_map = {}
            for ind in indicators_data['data']:
                symbol = ind.get('symbol', '').upper()
                indicators_map[symbol] = ind
            
            # 合并到已采集的数据
            for coin in collected_coins:
                symbol = coin['symbol']
                if symbol in indicators_map:
                    ind = indicators_map[symbol]
                    # MACD
                    coin['macd_5m'] = ind.get('macd_5m')
                    coin['macd_signal_5m'] = ind.get('macd_signal_5m')
                    coin['macd_hist_5m'] = ind.get('macd_hist_5m')
                    coin['macd_1h'] = ind.get('macd_1h')
                    coin['macd_signal_1h'] = ind.get('macd_signal_1h')
                    coin['macd_hist_1h'] = ind.get('macd_hist_1h')
                    
                    # KDJ
                    coin['kdj_k_5m'] = ind.get('kdj_k_5m')
                    coin['kdj_d_5m'] = ind.get('kdj_d_5m')
                    coin['kdj_j_5m'] = ind.get('kdj_j_5m')
                    coin['kdj_k_1h'] = ind.get('kdj_k_1h')
                    coin['kdj_d_1h'] = ind.get('kdj_d_1h')
                    coin['kdj_j_1h'] = ind.get('kdj_j_1h')
        
        except Exception as e:
            logging.error(f"合并技术指标失败: {e}")
    
    def save_to_database(self, coins_data):
        """保存到数据库"""
        if not coins_data:
            logging.warning("⚠️  没有数据需要保存")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for coin in coins_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO comprehensive_signals (
                        symbol, timestamp, beijing_time,
                        long_score, short_score,
                        long_score_3m_avg, short_score_3m_avg,
                        long_score_1h_avg, short_score_1h_avg,
                        long_score_3h_avg, short_score_3h_avg,
                        long_score_12h_avg, short_score_12h_avg,
                        long_score_24h_avg, short_score_24h_avg,
                        long_volume, short_volume, long_short_ratio,
                        sar_5m, sar_5m_quadrant, price_5m,
                        sar_1h, sar_1h_quadrant, price_1h,
                        rsi_5m, rsi_1h,
                        bb_upper_5m, bb_middle_5m, bb_lower_5m, bb_position_5m,
                        bb_upper_1h, bb_middle_1h, bb_lower_1h, bb_position_1h,
                        macd_5m, macd_signal_5m, macd_hist_5m,
                        macd_1h, macd_signal_1h, macd_hist_1h,
                        kdj_k_5m, kdj_d_5m, kdj_j_5m,
                        kdj_k_1h, kdj_d_1h, kdj_j_1h,
                        data_source, raw_data
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    coin['symbol'], coin['timestamp'], coin['beijing_time'],
                    coin.get('long_score'), coin.get('short_score'),
                    coin.get('long_score_3m_avg'), coin.get('short_score_3m_avg'),
                    coin.get('long_score_1h_avg'), coin.get('short_score_1h_avg'),
                    coin.get('long_score_3h_avg'), coin.get('short_score_3h_avg'),
                    coin.get('long_score_12h_avg'), coin.get('short_score_12h_avg'),
                    coin.get('long_score_24h_avg'), coin.get('short_score_24h_avg'),
                    coin.get('long_volume'), coin.get('short_volume'), coin.get('long_short_ratio'),
                    coin.get('sar_5m'), coin.get('sar_5m_quadrant'), coin.get('price_5m'),
                    coin.get('sar_1h'), coin.get('sar_1h_quadrant'), coin.get('price_1h'),
                    coin.get('rsi_5m'), coin.get('rsi_1h'),
                    coin.get('bb_upper_5m'), coin.get('bb_middle_5m'), coin.get('bb_lower_5m'), coin.get('bb_position_5m'),
                    coin.get('bb_upper_1h'), coin.get('bb_middle_1h'), coin.get('bb_lower_1h'), coin.get('bb_position_1h'),
                    coin.get('macd_5m'), coin.get('macd_signal_5m'), coin.get('macd_hist_5m'),
                    coin.get('macd_1h'), coin.get('macd_signal_1h'), coin.get('macd_hist_1h'),
                    coin.get('kdj_k_5m'), coin.get('kdj_d_5m'), coin.get('kdj_j_5m'),
                    coin.get('kdj_k_1h'), coin.get('kdj_d_1h'), coin.get('kdj_j_1h'),
                    coin.get('data_source', 'unknown'), coin.get('raw_data', '')
                ))
                saved_count += 1
            except Exception as e:
                logging.error(f"❌ 保存币种 {coin['symbol']} 失败: {e}")
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ 成功保存 {saved_count}/{len(coins_data)} 条记录")
        return saved_count
    
    def collect_once(self):
        """执行一次采集"""
        logging.info("=" * 80)
        logging.info("🚀 开始综合数据采集 (56+字段)")
        logging.info("=" * 80)
        
        coins_data = self.fetch_comprehensive_data()
        saved_count = self.save_to_database(coins_data)
        
        logging.info(f"✅ 本次采集完成: {saved_count} 个币种")
        return saved_count > 0

def main():
    """主函数"""
    collector = ComprehensiveSignalCollector()
    
    if '--once' in sys.argv:
        # 单次采集
        collector.collect_once()
    else:
        # 持续采集 (每3分钟)
        while True:
            try:
                collector.collect_once()
                logging.info("⏱️  等待3分钟后下次采集...")
                time.sleep(180)  # 3分钟
            except KeyboardInterrupt:
                logging.info("👋 用户中断，退出采集")
                break
            except Exception as e:
                logging.error(f"❌ 采集异常: {e}")
                time.sleep(60)  # 出错后等待1分钟再试

if __name__ == '__main__':
    import sys
    main()
