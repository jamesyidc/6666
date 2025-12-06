#!/usr/bin/env python3
"""
交易信号采集器
- 每3分钟从filtered-signals API采集做多/做空信号数量
- 存储到数据库，支持历史查询
- 生成12小时曲线图
"""

import sqlite3
import requests
import time
import json
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/signal_collector.log'),
        logging.StreamHandler()
    ]
)

# API基础URL
BASE_URL = "https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai"

class SignalCollector:
    def __init__(self, db_path='crypto_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_time TEXT NOT NULL,
                record_date TEXT NOT NULL,
                long_signals INTEGER DEFAULT 0,
                short_signals INTEGER DEFAULT 0,
                total_signals INTEGER DEFAULT 0,
                long_ratio REAL DEFAULT 0,
                short_ratio REAL DEFAULT 0,
                today_new_high INTEGER DEFAULT 0,
                today_new_low INTEGER DEFAULT 0,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引加速查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_record_time 
            ON trading_signals(record_time)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_record_date 
            ON trading_signals(record_date)
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ 数据库初始化完成")
    
    def fetch_signals(self):
        """从API获取信号数据"""
        try:
            # 1. 获取首页统计数据
            summary_url = f"{BASE_URL}/api/kline/summary"
            summary_resp = requests.get(summary_url, timeout=30)
            summary_data = summary_resp.json()
            
            today_new_high = 0
            today_new_low = 0
            
            if summary_data.get('data') and len(summary_data['data']) > 0:
                first_record = summary_data['data'][0]
                today_new_high = first_record.get('today_rise_count', 0)
                today_new_low = first_record.get('today_crash_count', 0)
            
            # 2. 获取过滤后的信号数据
            signals_url = f"{BASE_URL}/api/filtered-signals/stats"
            params = {
                'limit': 200,
                'rsi_short_threshold': 0,
                'rsi_long_threshold': 100,
                '_t': int(time.time() * 1000)
            }
            
            signals_resp = requests.get(signals_url, params=params, timeout=30)
            signals_data = signals_resp.json()
            
            # 3. 统计做多做空信号
            long_signals = 0
            short_signals = 0
            
            if signals_data.get('data'):
                for signal in signals_data['data']:
                    signal_type = signal.get('signal_type', '').lower()
                    if 'long' in signal_type or '做多' in signal_type:
                        long_signals += 1
                    elif 'short' in signal_type or '做空' in signal_type:
                        short_signals += 1
            
            total_signals = long_signals + short_signals
            long_ratio = (long_signals / total_signals * 100) if total_signals > 0 else 0
            short_ratio = (short_signals / total_signals * 100) if total_signals > 0 else 0
            
            result = {
                'long_signals': long_signals,
                'short_signals': short_signals,
                'total_signals': total_signals,
                'long_ratio': round(long_ratio, 2),
                'short_ratio': round(short_ratio, 2),
                'today_new_high': today_new_high,
                'today_new_low': today_new_low,
                'raw_data': json.dumps(signals_data.get('data', [])[:10])  # 保存前10条原始数据
            }
            
            logging.info(f"✅ 信号采集成功: 做多={long_signals}, 做空={short_signals}, 总计={total_signals}")
            return result
            
        except Exception as e:
            logging.error(f"❌ 信号采集失败: {str(e)}")
            return None
    
    def save_signal(self, signal_data):
        """保存信号数据到数据库"""
        if not signal_data:
            return False
        
        try:
            now = datetime.now()
            record_time = now.strftime('%Y-%m-%d %H:%M:%S')
            record_date = now.strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trading_signals (
                    record_time, record_date, long_signals, short_signals,
                    total_signals, long_ratio, short_ratio,
                    today_new_high, today_new_low, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_time,
                record_date,
                signal_data['long_signals'],
                signal_data['short_signals'],
                signal_data['total_signals'],
                signal_data['long_ratio'],
                signal_data['short_ratio'],
                signal_data['today_new_high'],
                signal_data['today_new_low'],
                signal_data['raw_data']
            ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"💾 数据保存成功: {record_time}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 数据保存失败: {str(e)}")
            return False
    
    def collect_once(self):
        """执行一次采集"""
        signal_data = self.fetch_signals()
        if signal_data:
            self.save_signal(signal_data)
            return True
        return False
    
    def run_daemon(self, interval=180):
        """
        守护进程模式运行
        interval: 采集间隔（秒），默认180秒=3分钟
        """
        logging.info(f"🚀 信号采集守护进程启动，采集间隔: {interval}秒")
        
        while True:
            try:
                self.collect_once()
                logging.info(f"⏳ 等待 {interval} 秒后进行下一次采集...")
                time.sleep(interval)
            except KeyboardInterrupt:
                logging.info("⛔ 收到停止信号，退出采集")
                break
            except Exception as e:
                logging.error(f"❌ 采集过程出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再试

def main():
    collector = SignalCollector()
    
    # 立即执行一次采集
    logging.info("📊 执行首次信号采集...")
    collector.collect_once()
    
    # 启动守护进程（3分钟间隔）
    collector.run_daemon(interval=180)

if __name__ == '__main__':
    main()
