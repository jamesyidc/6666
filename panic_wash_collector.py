#!/usr/bin/env python3
"""
恐慌清洗指数采集器
- 每3分钟采集一次爆仓数据
- 计算恐慌清洗指数 = 24小时爆仓人数(万人) / 全网持仓量(亿美元)
- 数据源：https://history.btc123.fans/baocang/
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
        logging.FileHandler('/home/user/webapp/panic_wash_collector.log'),
        logging.StreamHandler()
    ]
)

# API基础URL
BASE_URL = "https://api.btc123.fans/bicoin.php"

class PanicWashCollector:
    def __init__(self, db_path='crypto_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS panic_wash_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_time TEXT NOT NULL,
                record_date TEXT NOT NULL,
                hour_1_amount REAL DEFAULT 0,
                hour_24_amount REAL DEFAULT 0,
                hour_24_people INTEGER DEFAULT 0,
                total_position REAL DEFAULT 0,
                panic_index REAL DEFAULT 0,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_panic_record_time 
            ON panic_wash_index(record_time)
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ 数据库初始化完成")
    
    def fetch_24h_blast_data(self):
        """获取24小时爆仓数据"""
        try:
            url = f"{BASE_URL}?from=24hbaocang"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data.get('code') == 0 and data.get('data'):
                coins_list = data['data'].get('coinsDataList', [])
                
                # 统计总爆仓金额和人数
                total_blast_amount = 0
                total_blast_people = 0
                
                for coin in coins_list:
                    total_blast_amount += coin.get('totalBlast', 0)
                    total_blast_people += coin.get('totalBlastAboutCount', 0)
                
                return {
                    'hour_24_amount': total_blast_amount,
                    'hour_24_people': total_blast_people
                }
            
            return None
            
        except Exception as e:
            logging.error(f"❌ 获取24小时爆仓数据失败: {str(e)}")
            return None
    
    def fetch_1h_blast_data(self):
        """获取1小时爆仓数据"""
        try:
            url = f"{BASE_URL}?from=1hbaocang"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data.get('code') == 0 and data.get('data'):
                coins_list = data['data'].get('coinsDataList', [])
                
                # 统计1小时总爆仓金额
                total_blast_amount = 0
                for coin in coins_list:
                    total_blast_amount += coin.get('totalBlast', 0)
                
                return total_blast_amount
            
            return 0
            
        except Exception as e:
            logging.error(f"❌ 获取1小时爆仓数据失败: {str(e)}")
            return 0
    
    def fetch_total_position(self):
        """获取全网持仓量"""
        try:
            url = f"{BASE_URL}?from=realhold"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data.get('code') == 0 and data.get('data'):
                positions = data['data']
                
                # 查找"全网总计"
                for item in positions:
                    if item.get('exchange') == '全网总计':
                        return item.get('amount', 0)
            
            return 0
            
        except Exception as e:
            logging.error(f"❌ 获取全网持仓量失败: {str(e)}")
            return 0
    
    def calculate_panic_index(self, hour_24_people, total_position):
        """
        计算恐慌清洗指数
        
        公式：恐慌清洗指数 = 24小时爆仓人数(万人) / 全网持仓量(亿美元)
        
        参数:
            hour_24_people: 24小时爆仓人数（人）
            total_position: 全网持仓量（美元）
        
        返回:
            panic_index: 恐慌清洗指数（百分比）
        """
        if total_position <= 0:
            return 0
        
        # 24小时爆仓人数转换为万人
        people_wan = hour_24_people / 10000
        
        # 全网持仓量转换为亿美元
        position_yi = total_position / 100000000
        
        # 计算恐慌清洗指数（百分比）
        panic_index = (people_wan / position_yi) if position_yi > 0 else 0
        
        return round(panic_index, 2)
    
    def collect_data(self):
        """采集完整数据"""
        try:
            logging.info("📊 开始采集恐慌清洗数据...")
            
            # 1. 获取1小时爆仓金额
            hour_1_amount = self.fetch_1h_blast_data()
            logging.info(f"  1小时爆仓金额: ${hour_1_amount:,.2f}")
            
            # 2. 获取24小时爆仓数据
            blast_24h = self.fetch_24h_blast_data()
            if not blast_24h:
                logging.error("❌ 24小时爆仓数据获取失败")
                return None
            
            hour_24_amount = blast_24h['hour_24_amount']
            hour_24_people = blast_24h['hour_24_people']
            logging.info(f"  24小时爆仓金额: ${hour_24_amount:,.2f}")
            logging.info(f"  24小时爆仓人数: {hour_24_people:,} 人")
            
            # 3. 获取全网持仓量
            total_position = self.fetch_total_position()
            logging.info(f"  全网持仓量: ${total_position:,.2f}")
            
            # 4. 计算恐慌清洗指数
            panic_index = self.calculate_panic_index(hour_24_people, total_position)
            
            # 详细计算日志
            people_wan = hour_24_people / 10000
            position_yi = total_position / 100000000
            logging.info(f"  📈 恐慌清洗指数计算:")
            logging.info(f"     爆仓人数: {hour_24_people:,} 人 = {people_wan:.4f} 万人")
            logging.info(f"     持仓量: ${total_position:,.2f} = {position_yi:.2f} 亿美元")
            logging.info(f"     恐慌指数: {people_wan:.4f} / {position_yi:.2f} = {panic_index}%")
            
            result = {
                'hour_1_amount': hour_1_amount,
                'hour_24_amount': hour_24_amount,
                'hour_24_people': hour_24_people,
                'total_position': total_position,
                'panic_index': panic_index,
                'raw_data': json.dumps({
                    'hour_1_amount': hour_1_amount,
                    'hour_24_amount': hour_24_amount,
                    'hour_24_people': hour_24_people,
                    'total_position': total_position
                })
            }
            
            logging.info(f"✅ 数据采集成功: 恐慌指数={panic_index}%")
            return result
            
        except Exception as e:
            logging.error(f"❌ 数据采集失败: {str(e)}")
            return None
    
    def save_data(self, data):
        """保存数据到数据库（使用北京时间）"""
        if not data:
            return False
        
        try:
            # 使用北京时间
            beijing_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(beijing_tz)
            record_time = now.strftime('%Y-%m-%d %H:%M:%S')
            record_date = now.strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO panic_wash_index (
                    record_time, record_date, hour_1_amount, hour_24_amount,
                    hour_24_people, total_position, panic_index, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_time,
                record_date,
                data['hour_1_amount'],
                data['hour_24_amount'],
                data['hour_24_people'],
                data['total_position'],
                data['panic_index'],
                data['raw_data']
            ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"💾 数据保存成功: {record_time}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 数据保存失败: {str(e)}")
            return False
    
    def collect_once(self):
        """执行一次完整采集"""
        data = self.collect_data()
        if data:
            self.save_data(data)
            return True
        return False
    
    def run_daemon(self, interval=180):
        """
        守护进程模式运行
        interval: 采集间隔（秒），默认180秒=3分钟
        """
        logging.info(f"🚀 恐慌清洗指数采集器启动，采集间隔: {interval}秒")
        
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
    collector = PanicWashCollector()
    
    # 立即执行一次采集
    logging.info("📊 执行首次恐慌清洗指数采集...")
    collector.collect_once()
    
    # 启动守护进程（3分钟间隔）
    collector.run_daemon(interval=180)

if __name__ == '__main__':
    main()
