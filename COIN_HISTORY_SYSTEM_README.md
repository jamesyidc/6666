# 全币数据统计系统 - 使用文档

## 📋 系统概述

全币数据统计系统是一个自动化的加密货币数据采集、存储和可视化系统。系统每分钟自动采集一次数据，支持按日期查询历史数据，提供时间轴回放功能。

### ✨ 核心功能

1. **自动数据采集**：每分钟自动从API采集一次全币种数据
2. **历史数据存储**：独立数据库保存所有历史快照
3. **按日期查询**：快速查询任意日期的所有历史数据
4. **时间轴回放**：可视化时间轴，支持播放和手动拖动
5. **详细币种信息**：每个快照包含所有币种的详细数据（价格、涨跌、急涨急跌、账户比例等）

---

## 🏗️ 系统架构

```
全币数据统计系统
├── 数据采集层
│   └── coin_history_collector.py (每分钟采集一次)
├── 数据存储层
│   └── coin_history_stats.db (SQLite数据库)
│       ├── coin_snapshots (快照汇总表)
│       ├── coin_details (币种详细数据表)
│       └── daily_summary (日期汇总表)
├── API服务层
│   └── coin_history_api.py (Flask REST API)
└── 前端展示层
    └── coin_history_viewer.html (可视化界面)
```

---

## 🚀 快速启动

### 一键启动（推荐）

```bash
cd /home/user/webapp
./start_coin_history_system.sh
```

### 手动启动

```bash
cd /home/user/webapp

# 1. 创建数据库（首次运行）
python3 create_history_stats_db.py

# 2. 启动API服务
nohup python3 coin_history_api.py > api_service.log 2>&1 &

# 3. 启动数据采集服务
nohup python3 coin_history_collector.py > coin_collector.log 2>&1 &
```

---

## 📊 数据库结构

### 1. coin_snapshots（快照汇总表）

每分钟一条记录，保存该时刻的汇总数据：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| snapshot_datetime | TEXT | 快照时间（YYYY-MM-DD HH:MM:SS） |
| snapshot_date | TEXT | 快照日期（YYYY-MM-DD） |
| snapshot_time | TEXT | 快照时间（HH:MM:SS） |
| total_coins | INTEGER | 总币种数 |
| rush_up_count | INTEGER | 急涨币种数 |
| rush_down_count | INTEGER | 急跌币种数 |
| rising_coins | INTEGER | 上涨币种数 |
| falling_coins | INTEGER | 下跌币种数 |
| account_ratio_avg | REAL | 平均账户比例 |
| account_ratio_max | REAL | 最大账户比例 |
| account_ratio_min | REAL | 最小账户比例 |
| avg_change_24h | REAL | 平均24小时涨跌幅 |
| max_change_24h | REAL | 最大24小时涨跌幅 |
| min_change_24h | REAL | 最小24小时涨跌幅 |

### 2. coin_details（币种详细数据表）

每个快照的每个币种一条记录：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| snapshot_datetime | TEXT | 快照时间 |
| symbol | TEXT | 币种符号（如BTC、ETH） |
| rank | INTEGER | 排名 |
| price | REAL | 当前价格 |
| change_24h | REAL | 24小时涨跌幅 |
| rush_up | INTEGER | 急涨标记 |
| rush_down | INTEGER | 急跌标记 |
| account_ratio | REAL | 账户比例 |
| volume_24h | REAL | 24小时交易量 |
| market_cap | REAL | 市值 |

### 3. daily_summary（日期汇总表）

每天一条记录，汇总当日数据：

| 字段 | 类型 | 说明 |
|------|------|------|
| summary_date | TEXT | 日期（主键） |
| total_snapshots | INTEGER | 当日快照总数 |
| avg_total_coins | REAL | 平均币种数 |
| max_rush_up | INTEGER | 最大急涨数 |
| max_rush_down | INTEGER | 最大急跌数 |
| highest_change | REAL | 最高涨幅 |
| lowest_change | REAL | 最低跌幅 |
| first_snapshot_time | TEXT | 首次快照时间 |
| last_snapshot_time | TEXT | 最后快照时间 |

---

## 🔌 API接口文档

### 基础信息

- **API地址**：`http://localhost:5002` 或 `https://5002-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai`
- **响应格式**：JSON

### 接口列表

#### 1. 健康检查

```
GET /api/health
```

响应示例：
```json
{
    "success": true,
    "service": "全币数据统计系统API",
    "version": "1.0.0",
    "timestamp": "2025-12-08 12:00:00"
}
```

#### 2. 获取可用日期列表

```
GET /api/history/dates
```

响应示例：
```json
{
    "success": true,
    "dates": [
        {
            "date": "2025-12-08",
            "snapshots": 142,
            "time_range": "00:00:00 ~ 23:59:00",
            "max_rush_up": 45,
            "max_rush_down": 38,
            "highest_change": 15.2,
            "lowest_change": -8.3
        }
    ],
    "total": 1
}
```

#### 3. 获取指定日期的快照列表

```
GET /api/history/snapshots?date=2025-12-08
```

响应示例：
```json
{
    "success": true,
    "date": "2025-12-08",
    "snapshots": [...],
    "total": 142
}
```

#### 4. 获取快照详细数据

```
GET /api/history/snapshot/{snapshot_datetime}
```

示例：`GET /api/history/snapshot/2025-12-08%2012:30:00`

响应包含该快照的汇总数据和所有币种的详细数据。

#### 5. 获取时间轴数据

```
GET /api/history/timeline?date=2025-12-08
```

用于图表展示，返回一天内所有时间点的数据数组。

#### 6. 搜索币种历史

```
GET /api/history/search?symbol=BTC&date=2025-12-08
```

查询指定币种在指定日期（可选）的历史数据。

#### 7. 获取统计数据

```
GET /api/history/stats
```

返回系统整体统计信息（总天数、总快照数等）。

---

## 🌐 前端使用说明

### 访问地址

- **本地访问**：`http://localhost:3000/coin_history_viewer.html`
- **公网访问**：通过沙盒提供的公网地址访问

### 功能说明

1. **日期选择**：下拉菜单选择要查看的日期
2. **加载数据**：点击"🔍 加载数据"按钮加载选中日期的数据
3. **刷新日期**：点击"🔄 刷新日期"更新可用日期列表
4. **时间轴回放**：
   - 拖动滑块：手动选择时间点
   - 点击"▶️ 播放"：自动播放，每秒切换一个快照
   - 点击"⏸️ 暂停"：暂停播放
5. **数据展示**：
   - 顶部统计卡片：快照总数、时间范围、最大急涨/急跌
   - 时间轴图表：急涨/急跌趋势图
   - 当前统计：实时更新当前时刻的统计数据
   - 币种详细表格：显示所有币种的详细信息

---

## 📝 日志管理

### 日志文件位置

- **API服务日志**：`/home/user/webapp/api_service.log`
- **数据采集日志**：`/home/user/webapp/coin_collector.log`

### 查看日志

```bash
# 查看API服务日志（实时）
tail -f /home/user/webapp/api_service.log

# 查看数据采集日志（实时）
tail -f /home/user/webapp/coin_collector.log

# 查看最近50行
tail -50 /home/user/webapp/coin_collector.log
```

---

## 🛠️ 维护操作

### 查看运行状态

```bash
# 查看所有相关进程
ps aux | grep 'coin_history_api\|coin_history_collector'

# 检查端口占用
lsof -i :5002
```

### 停止服务

```bash
# 停止API服务
pkill -f coin_history_api.py

# 停止数据采集服务
pkill -f coin_history_collector.py

# 停止所有服务
pkill -f "coin_history_api.py\|coin_history_collector.py"
```

### 重启服务

```bash
# 停止所有服务
pkill -f "coin_history_api.py\|coin_history_collector.py"

# 等待几秒
sleep 3

# 重新启动
./start_coin_history_system.sh
```

### 清空数据库（谨慎操作）

```bash
# 备份数据库
cp coin_history_stats.db coin_history_stats.db.backup

# 删除并重新创建数据库
rm coin_history_stats.db
python3 create_history_stats_db.py
```

---

## 📈 数据采集说明

### 采集频率

- **间隔时间**：60秒（1分钟）
- **采集方式**：从本地API获取数据（http://localhost:5000/api/latest）
- **自动重试**：采集失败时自动重试

### 数据来源

系统从`app_new.py`提供的API获取数据，该API返回当前所有币种的实时数据。

### 数据完整性

- 每个快照包含完整的币种列表
- 自动计算汇总数据（急涨急跌数、涨跌币种数、平均值等）
- 自动提取账户比例数据（从ratio1字段）

---

## ⚠️ 注意事项

1. **数据依赖**：系统依赖`app_new.py`的API服务（端口5000），请确保该服务正常运行
2. **磁盘空间**：每天约产生140+个快照，每个快照29个币种，注意磁盘空间
3. **数据库文件**：`coin_history_stats.db`是SQLite文件，可以直接复制备份
4. **时区问题**：所有时间使用服务器本地时间
5. **并发访问**：SQLite支持并发读，但写入时会锁定，数据采集和API查询不会冲突

---

## 🔧 故障排查

### 问题1：数据未采集

**检查步骤**：
1. 确认采集进程是否运行：`ps aux | grep coin_history_collector`
2. 查看采集日志：`tail -50 coin_collector.log`
3. 检查API是否可访问：`curl http://localhost:5000/api/latest`

### 问题2：API无响应

**检查步骤**：
1. 确认API进程是否运行：`ps aux | grep coin_history_api`
2. 查看API日志：`tail -50 api_service.log`
3. 检查端口是否被占用：`lsof -i :5002`

### 问题3：前端无法加载数据

**检查步骤**：
1. 打开浏览器开发者工具查看网络请求
2. 确认API地址是否正确
3. 检查是否有CORS错误

### 问题4：数据库损坏

**恢复步骤**：
```bash
# 检查数据库完整性
sqlite3 coin_history_stats.db "PRAGMA integrity_check;"

# 导出数据
sqlite3 coin_history_stats.db ".dump" > backup.sql

# 重建数据库
rm coin_history_stats.db
python3 create_history_stats_db.py
sqlite3 coin_history_stats.db < backup.sql
```

---

## 📞 技术支持

如有问题，请查看：
- 系统日志文件
- API文档
- 数据库结构说明

---

## 📜 更新日志

### v1.0.0 (2025-12-08)

- ✅ 初始版本发布
- ✅ 实现每分钟自动数据采集
- ✅ 完整的REST API接口
- ✅ 可视化前端界面
- ✅ 时间轴回放功能
- ✅ 账户比例数据支持
- ✅ 按日期查询历史数据

---

**系统状态**: ✅ 运行中  
**最后更新**: 2025-12-08  
**版本**: v1.0.0
