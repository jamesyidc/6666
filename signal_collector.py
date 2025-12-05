#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟币系统信号数据采集器
从 Google Drive 定期读取信号数据并存储到数据库
"""

import sqlite3
import time
from datetime import datetime, timedelta
import pytz
import sys
import os
import random

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# 数据库配置
DB_PATH = 'signal_data.db'

# Google Drive 配置
GOOGLE_DRIVE_FOLDER_ID = "1-IfqZxMVVCSg3ct6XVMyFtAbuCV3huQ"

# 采集间隔（秒）
COLLECTION_INTERVAL = 180  # 3分钟


def get_beijing_time():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def get_today_folder_name():
    """获取今天的文件夹名称（北京时间）"""
    beijing_now = get_beijing_time()
    
    # 如果是0点到0点5分之间，使用昨天的日期
    if beijing_now.hour == 0 and beijing_now.minute < 5:
        beijing_now = beijing_now - timedelta(days=1)
    
    return beijing_now.strftime('%Y-%m-%d')


def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signal_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_count INTEGER NOT NULL,
            short_change INTEGER NOT NULL,
            long_count INTEGER NOT NULL,
            long_change INTEGER NOT NULL,
            record_time TEXT NOT NULL,
            folder_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(record_time)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_record_time ON signal_data(record_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_folder_date ON signal_data(folder_date)')
    
    conn.commit()
    conn.close()


def parse_signal_line(line):
    """解析信号数据行: 做空|变化|做多|变化|时间"""
    try:
        parts = line.strip().split('|')
        if len(parts) >= 5:
            def safe_int(s):
                s = s.strip()
                if s.lstrip('-').isdigit():
                    return int(s)
                return 0
            
            return {
                'short_count': safe_int(parts[0]),
                'short_change': safe_int(parts[1]),
                'long_count': safe_int(parts[2]),
                'long_change': safe_int(parts[3]),
                'record_time': parts[4].strip()
            }
    except Exception as e:
        print(f"解析行失败: {line}, 错误: {e}")
    return None


def save_signal_to_db(signal_data, folder_date):
    """保存信号数据到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO signal_data 
            (short_count, short_change, long_count, long_change, record_time, folder_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            signal_data['short_count'],
            signal_data['short_change'],
            signal_data['long_count'],
            signal_data['long_change'],
            signal_data['record_time'],
            folder_date
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False


def fetch_signal_from_google_drive(folder_date):
    """
    从Google Drive获取信号数据
    
    TODO: 实现实际的Google Drive API调用
    当前返回模拟数据用于测试
    
    实际实现步骤：
    1. 使用Google Drive API列出文件夹内容
    2. 找到对应日期的文件夹
    3. 读取"信号.txt"文件
    4. 解析最后一行数据
    """
    
    # 模拟数据 - 实际应该从Google Drive读取
    # 格式: 做空|变化|做多|变化|时间
    beijing_now = get_beijing_time()
    time_str = beijing_now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 生成模拟数据（在实际场景中应该从Google Drive读取）
    short_count = random.randint(100, 150)
    long_count = random.randint(80, 120)
    short_change = random.randint(-10, 10)
    long_change = random.randint(-10, 10)
    
    signal_line = f"{short_count}|{short_change}|{long_count}|{long_change}|{time_str}"
    
    print(f"[模拟数据] {signal_line}")
    print(f"[提示] 实际使用时需要配置Google Drive API并从以下位置读取:")
    print(f"       文件夹ID: {GOOGLE_DRIVE_FOLDER_ID}")
    print(f"       日期文件夹: {folder_date}")
    print(f"       文件名: 信号.txt")
    
    return parse_signal_line(signal_line)


def collect_data_once():
    """执行一次数据采集"""
    try:
        folder_date = get_today_folder_name()
        beijing_time = get_beijing_time()
        
        print(f"\n{'='*70}")
        print(f"[{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}] 开始数据采集")
        print(f"目标文件夹: {folder_date}")
        print(f"{'='*70}")
        
        # 从Google Drive获取信号数据
        signal_data = fetch_signal_from_google_drive(folder_date)
        
        if signal_data:
            # 保存到数据库
            if save_signal_to_db(signal_data, folder_date):
                print(f"✓ 数据采集成功")
                print(f"  做空: {signal_data['short_count']} (变化: {signal_data['short_change']:+d})")
                print(f"  做多: {signal_data['long_count']} (变化: {signal_data['long_change']:+d})")
                print(f"  时间: {signal_data['record_time']}")
            else:
                print("✗ 数据保存失败")
        else:
            print("✗ 未获取到有效数据")
        
        # 计算下次采集时间
        next_time = beijing_time + timedelta(seconds=COLLECTION_INTERVAL)
        print(f"\n下次采集时间: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
    except Exception as e:
        print(f"✗ 数据采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_collector():
    """运行数据采集器（持续模式）"""
    print("="*70)
    print("虚拟币系统信号数据采集器")
    print("="*70)
    print(f"启动时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"数据库: {DB_PATH}")
    print(f"采集间隔: {COLLECTION_INTERVAL}秒 ({COLLECTION_INTERVAL//60}分钟)")
    print(f"Google Drive Folder ID: {GOOGLE_DRIVE_FOLDER_ID}")
    print("="*70)
    print("\n提示: 按 Ctrl+C 停止采集\n")
    
    # 初始化数据库
    init_database()
    
    # 立即执行一次采集
    collect_data_once()
    
    # 持续采集
    try:
        while True:
            time.sleep(COLLECTION_INTERVAL)
            collect_data_once()
    except KeyboardInterrupt:
        print("\n\n采集器已停止")
        sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 只执行一次采集（用于测试）
        init_database()
        collect_data_once()
    else:
        # 持续运行
        run_collector()
