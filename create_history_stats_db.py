#!/usr/bin/env python3
"""
全币数据统计系统 - 数据库创建脚本
用于按日期存储和查询历史数据
"""

import sqlite3
from datetime import datetime

def create_database():
    """创建全币数据统计数据库"""
    conn = sqlite3.connect('coin_history_stats.db')
    cursor = conn.cursor()
    
    # 创建币种历史快照表（每分钟一个快照）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coin_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,           -- 日期 YYYY-MM-DD
            snapshot_time TEXT NOT NULL,           -- 时间 HH:MM:SS
            snapshot_datetime TEXT NOT NULL,       -- 完整时间戳 YYYY-MM-DD HH:MM:SS
            
            -- 市场总览数据
            total_coins INTEGER DEFAULT 0,         -- 总币种数
            rush_up_count INTEGER DEFAULT 0,       -- 急涨数量
            rush_down_count INTEGER DEFAULT 0,     -- 急跌数量
            rising_coins INTEGER DEFAULT 0,        -- 上涨币种数
            falling_coins INTEGER DEFAULT 0,       -- 下跌币种数
            
            -- 账户比例相关
            account_ratio_avg REAL DEFAULT 0,      -- 平均账户比例
            account_ratio_max REAL DEFAULT 0,      -- 最大账户比例
            account_ratio_min REAL DEFAULT 0,      -- 最小账户比例
            
            -- 涨跌幅统计
            avg_change_24h REAL DEFAULT 0,         -- 24小时平均涨跌幅
            max_change_24h REAL DEFAULT 0,         -- 最大涨幅
            min_change_24h REAL DEFAULT 0,         -- 最大跌幅
            
            -- 元数据
            data_source TEXT DEFAULT 'api',        -- 数据来源
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- 索引字段
            UNIQUE(snapshot_datetime)
        )
    """)
    
    # 创建日期索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshot_date 
        ON coin_snapshots(snapshot_date)
    """)
    
    # 创建时间索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshot_datetime 
        ON coin_snapshots(snapshot_datetime)
    """)
    
    # 创建币种详细数据表（每分钟存储所有币种数据）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coin_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_datetime TEXT NOT NULL,       -- 快照时间
            
            -- 币种基本信息
            symbol TEXT NOT NULL,                  -- 币种符号
            rank INTEGER DEFAULT 0,                -- 排名
            
            -- 价格数据
            price REAL DEFAULT 0,                  -- 当前价格
            change_24h REAL DEFAULT 0,             -- 24小时涨跌幅
            
            -- 急涨急跌标记
            rush_up INTEGER DEFAULT 0,             -- 急涨次数
            rush_down INTEGER DEFAULT 0,           -- 急跌次数
            
            -- 账户比例
            account_ratio REAL DEFAULT 0,          -- 账户比例
            
            -- 其他数据
            volume_24h REAL DEFAULT 0,             -- 24小时成交量
            market_cap REAL DEFAULT 0,             -- 市值
            
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- 复合索引
            UNIQUE(snapshot_datetime, symbol)
        )
    """)
    
    # 创建币种详细数据索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coin_details_datetime 
        ON coin_details(snapshot_datetime)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coin_details_symbol 
        ON coin_details(symbol)
    """)
    
    # 创建日期汇总表（每天一条记录，用于快速查看某天的统计）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date TEXT NOT NULL UNIQUE,     -- 日期 YYYY-MM-DD
            
            -- 统计数据
            total_snapshots INTEGER DEFAULT 0,     -- 快照总数
            avg_total_coins INTEGER DEFAULT 0,     -- 平均币种数
            max_rush_up INTEGER DEFAULT 0,         -- 最大急涨数
            max_rush_down INTEGER DEFAULT 0,       -- 最大急跌数
            
            -- 日内极值
            highest_change REAL DEFAULT 0,         -- 最高涨幅
            lowest_change REAL DEFAULT 0,          -- 最低跌幅
            
            -- 时间范围
            first_snapshot_time TEXT,              -- 第一个快照时间
            last_snapshot_time TEXT,               -- 最后一个快照时间
            
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ 数据库创建成功: coin_history_stats.db")
    print("\n📊 已创建的表:")
    print("  1. coin_snapshots - 币种历史快照（每分钟）")
    print("  2. coin_details - 币种详细数据")
    print("  3. daily_summary - 日期汇总表")
    print("\n✅ 已创建索引用于快速查询")

if __name__ == "__main__":
    create_database()
