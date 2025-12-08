#!/usr/bin/env python3
"""
全币数据统计系统 - 数据采集脚本
每分钟采集一次API数据，存储到数据库
"""

import sqlite3
import requests
import json
from datetime import datetime
import time
import sys

# API地址（使用本地app_new.py的API）
API_URL = "http://localhost:5000/api/latest"

def get_current_data():
    """从API获取当前数据"""
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API返回错误状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}")
        return None

def parse_and_store_data(data):
    """解析并存储数据到数据库"""
    if not data or 'coins' not in data:
        print("❌ 数据格式错误")
        return False
    
    conn = sqlite3.connect('coin_history_stats.db')
    cursor = conn.cursor()
    
    try:
        # 获取当前时间
        now = datetime.now()
        snapshot_date = now.strftime('%Y-%m-%d')
        snapshot_time = now.strftime('%H:%M:%S')
        snapshot_datetime = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 解析币种数据
        coins = data.get('coins', [])
        total_coins = len(coins)
        
        # 从顶层数据获取急涨急跌总数
        rush_up_count = data.get('rush_up', 0)
        rush_down_count = data.get('rush_down', 0)
        
        # 统计涨跌币种数
        rising_coins = 0
        falling_coins = 0
        
        changes_24h = []
        
        for coin in coins:
            # 统计涨跌
            change_24h = coin.get('change_24h', 0)
            if change_24h > 0:
                rising_coins += 1
            elif change_24h < 0:
                falling_coins += 1
            changes_24h.append(change_24h)
        
        # 计算统计值
        avg_change_24h = sum(changes_24h) / len(changes_24h) if changes_24h else 0
        max_change_24h = max(changes_24h) if changes_24h else 0
        min_change_24h = min(changes_24h) if changes_24h else 0
        
        # 账户比例（从API数据中没有这个字段，设为0或从币种数据中计算）
        account_ratio_avg = 0.0
        account_ratio_max = 0.0
        account_ratio_min = 0.0
        
        # 插入快照数据
        cursor.execute("""
            INSERT OR REPLACE INTO coin_snapshots (
                snapshot_date, snapshot_time, snapshot_datetime,
                total_coins, rush_up_count, rush_down_count,
                rising_coins, falling_coins,
                account_ratio_avg, account_ratio_max, account_ratio_min,
                avg_change_24h, max_change_24h, min_change_24h,
                data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_date, snapshot_time, snapshot_datetime,
            total_coins, rush_up_count, rush_down_count,
            rising_coins, falling_coins,
            account_ratio_avg, account_ratio_max, account_ratio_min,
            avg_change_24h, max_change_24h, min_change_24h,
            'api'
        ))
        
        snapshot_id = cursor.lastrowid
        
        # 插入币种详细数据
        for coin in coins:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO coin_details (
                        snapshot_datetime, symbol, rank,
                        price, change_24h, rush_up, rush_down,
                        account_ratio, volume_24h, market_cap
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot_datetime,
                    coin.get('symbol', ''),
                    coin.get('rank', 0),
                    coin.get('current_price', 0),
                    coin.get('change_24h', 0),
                    coin.get('rush_up', 0),
                    coin.get('rush_down', 0),
                    0,  # account_ratio not available in this API
                    0,  # volume_24h not available in this API
                    0   # market_cap not available in this API
                ))
            except Exception as e:
                print(f"⚠️  插入币种数据失败 ({coin.get('symbol', 'UNKNOWN')}): {str(e)}")
        
        # 更新日期汇总
        cursor.execute("""
            INSERT OR IGNORE INTO daily_summary (summary_date) VALUES (?)
        """, (snapshot_date,))
        
        cursor.execute("""
            UPDATE daily_summary SET
                total_snapshots = total_snapshots + 1,
                avg_total_coins = (
                    SELECT AVG(total_coins) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                max_rush_up = (
                    SELECT MAX(rush_up_count) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                max_rush_down = (
                    SELECT MAX(rush_down_count) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                highest_change = (
                    SELECT MAX(max_change_24h) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                lowest_change = (
                    SELECT MIN(min_change_24h) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                first_snapshot_time = (
                    SELECT MIN(snapshot_time) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                last_snapshot_time = (
                    SELECT MAX(snapshot_time) FROM coin_snapshots 
                    WHERE snapshot_date = ?
                ),
                updated_at = CURRENT_TIMESTAMP
            WHERE summary_date = ?
        """, (snapshot_date, snapshot_date, snapshot_date, snapshot_date, snapshot_date, snapshot_date, snapshot_date, snapshot_date))
        
        conn.commit()
        
        print(f"✅ [{snapshot_datetime}] 数据采集成功")
        print(f"   币种数: {total_coins}, 急涨: {rush_up_count}, 急跌: {rush_down_count}")
        print(f"   上涨: {rising_coins}, 下跌: {falling_coins}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据存储失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def collect_once():
    """执行一次数据采集"""
    print(f"\n🔄 开始采集数据... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    data = get_current_data()
    if data:
        success = parse_and_store_data(data)
        return success
    return False

def main():
    """主函数 - 每分钟采集一次"""
    print("=" * 60)
    print("全币数据统计系统 - 数据采集服务")
    print("=" * 60)
    print(f"API地址: {API_URL}")
    print(f"采集间隔: 60秒")
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 先执行一次立即采集
    collect_once()
    
    # 开始定时采集
    while True:
        try:
            # 等待到下一分钟的开始
            now = datetime.now()
            seconds_to_next_minute = 60 - now.second
            print(f"\n⏱️  等待 {seconds_to_next_minute} 秒到下一分钟...")
            time.sleep(seconds_to_next_minute)
            
            # 采集数据
            collect_once()
            
        except KeyboardInterrupt:
            print("\n\n👋 收到停止信号，退出采集服务...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            print("⏱️  60秒后重试...")
            time.sleep(60)

if __name__ == "__main__":
    main()
