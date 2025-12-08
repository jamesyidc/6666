# 全币数据统计系统

## 📋 系统简介

全币数据统计系统是一个用于收集、存储和回看加密货币历史数据的完整解决方案。

### 核心功能
- ⏱️ **定时采集**: 每分钟自动采集一次全币数据
- 📅 **按日期查询**: 可以按日期查看任意一天的历史数据
- 🎬 **时间轴回看**: 支持时间轴拖动和自动播放回看
- 📊 **数据统计**: 提供丰富的统计图表和趋势分析
- 💾 **独立数据库**: 使用单独的SQLite数据库存储历史数据

---

## 🗄️ 数据库结构

### 1. coin_snapshots (币种快照表)
每分钟一个快照，记录市场整体状态：
- 总币种数、急涨/急跌数量
- 上涨/下跌币种统计
- 账户比例统计
- 24h涨跌幅统计

### 2. coin_details (币种详细数据表)
每个快照包含所有币种的详细数据：
- 币种基本信息（符号、排名、价格）
- 涨跌幅数据
- 急涨急跌标记
- 账户比例等

### 3. daily_summary (日期汇总表)
每天一条记录，用于快速查看某天的统计：
- 快照总数、平均币种数
- 最大急涨/急跌
- 日内极值等

---

## 🚀 快速启动

### 1. 初始化数据库
```bash
cd /home/user/webapp
python3 create_history_stats_db.py
```

### 2. 启动全部服务
```bash
chmod +x start_history_system.sh
./start_history_system.sh
```

服务包括：
- API服务（端口5001）
- 数据采集服务（每分钟一次）

### 3. 停止服务
```bash
chmod +x stop_history_system.sh
./stop_history_system.sh
```

### 4. 查看服务状态
```bash
# 查看API日志
tail -f coin_history_api.log

# 查看采集日志
tail -f coin_history_collector.log

# 检查进程
ps aux | grep coin_history
```

---

## 📡 API接口文档

### 基础URL
```
http://localhost:5001
```

### 1. 获取可用日期列表
```
GET /api/history/dates
```

**响应示例**:
```json
{
    "success": true,
    "dates": [
        {
            "date": "2025-12-08",
            "snapshots": 144,
            "time_range": "00:00:00 ~ 23:59:00",
            "max_rush_up": 15,
            "max_rush_down": 8
        }
    ],
    "total": 1
}
```

### 2. 获取指定日期的所有快照
```
GET /api/history/snapshots?date=2025-12-08
```

**响应示例**:
```json
{
    "success": true,
    "date": "2025-12-08",
    "snapshots": [
        {
            "id": 1,
            "time": "00:00:00",
            "datetime": "2025-12-08 00:00:00",
            "total_coins": 100,
            "rush_up_count": 5,
            "rush_down_count": 3,
            "rising_coins": 60,
            "falling_coins": 40,
            "account_ratio_avg": 2.5,
            "avg_change_24h": 1.2
        }
    ],
    "total": 144
}
```

### 3. 获取指定快照的详细数据
```
GET /api/history/snapshot/2025-12-08%2000:00:00
```

**响应示例**:
```json
{
    "success": true,
    "snapshot": {
        "datetime": "2025-12-08 00:00:00",
        "total_coins": 100,
        "rush_up_count": 5
    },
    "coins": [
        {
            "symbol": "BTC",
            "rank": 1,
            "price": 42000.5,
            "change_24h": 2.5,
            "rush_up": 1,
            "rush_down": 0,
            "account_ratio": 3.2
        }
    ],
    "coins_count": 100
}
```

### 4. 获取时间轴数据（用于图表）
```
GET /api/history/timeline?date=2025-12-08
```

### 5. 搜索指定币种的历史
```
GET /api/history/search?symbol=BTC&date=2025-12-08
```

### 6. 获取统计数据
```
GET /api/history/stats
```

### 7. 健康检查
```
GET /api/health
```

---

## 🌐 前端页面

### 访问地址
```
http://localhost:3000/coin_history_viewer.html
```

### 功能特性

#### 1. 日期选择
- 下拉菜单显示所有有数据的日期
- 显示每天的快照数量
- 一键加载选定日期的数据

#### 2. 时间轴控制
- **拖动滑块**: 手动浏览任意时间点
- **自动播放**: 按时间顺序自动播放
- **暂停功能**: 随时暂停查看详情
- **时间显示**: 实时显示当前查看的时间

#### 3. 数据展示

**统计卡片**:
- 快照总数
- 时间范围
- 最大急涨/急跌
- 当前快照统计

**趋势图表**:
- 急涨/急跌趋势
- 上涨/下跌币种数量
- 账户比例变化

**币种详细表格**:
- 排名、币种、价格
- 24h涨跌幅
- 急涨急跌次数
- 账户比例

#### 4. 交互功能
- 响应式设计，支持各种屏幕
- 实时数据更新
- 平滑动画过渡
- 颜色标识（涨绿跌红）

---

## 📊 数据采集说明

### 采集周期
- **频率**: 每60秒采集一次
- **时机**: 每分钟的第0秒开始采集
- **失败重试**: 出错后60秒自动重试

### 数据来源
从以下API获取数据：
```
https://3000-i6z1n4prnsqw4uzv0af9z-2e77fc33.sandbox.novita.ai/api/current_data
```

### 采集内容
- 所有币种的当前数据
- 计算市场整体统计
- 存储到数据库供回看

### 数据保留
- 所有历史数据永久保留
- 可以查看任意历史时间点
- 支持按日期快速检索

---

## 🔧 配置说明

### API端口配置
在 `coin_history_api.py` 中修改：
```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

### 采集间隔配置
在 `coin_history_collector.py` 中修改：
```python
time.sleep(60)  # 60秒 = 1分钟
```

### API地址配置
在 `coin_history_collector.py` 中修改：
```python
API_URL = "你的API地址"
```

---

## 📈 使用场景

### 1. 市场回顾
查看某一天的市场波动情况，分析关键时间点

### 2. 趋势分析
通过时间轴图表，观察急涨急跌的变化趋势

### 3. 数据对比
对比不同时间点的市场状态

### 4. 历史追溯
查找特定时间的市场数据，进行事后分析

---

## 🐛 故障排查

### 问题1: 数据采集失败
```bash
# 检查API是否可访问
curl "https://3000-i6z1n4prnsqw4uzv0af9z-2e77fc33.sandbox.novita.ai/api/current_data"

# 查看采集日志
tail -f coin_history_collector.log
```

### 问题2: API服务无响应
```bash
# 检查API进程
ps aux | grep coin_history_api

# 查看API日志
tail -f coin_history_api.log

# 重启API服务
./stop_history_system.sh
./start_history_system.sh
```

### 问题3: 前端无法加载数据
```bash
# 检查API端口是否监听
netstat -tlnp | grep 5001

# 检查数据库是否存在
ls -lh coin_history_stats.db

# 查看数据库内容
sqlite3 coin_history_stats.db "SELECT COUNT(*) FROM coin_snapshots;"
```

### 问题4: 数据库锁定
```bash
# 如果出现数据库锁定，重启服务
./stop_history_system.sh
sleep 5
./start_history_system.sh
```

---

## 📝 日志文件

系统生成以下日志文件：

| 文件名 | 说明 |
|--------|------|
| `coin_history_api.log` | API服务日志 |
| `coin_history_collector.log` | 数据采集日志 |
| `coin_history_api.pid` | API进程ID |
| `coin_history_collector.pid` | 采集进程ID |

---

## 💡 扩展建议

### 1. 添加更多统计维度
- 成交量统计
- 市值排名变化
- 更多技术指标

### 2. 导出功能
- 导出为CSV
- 导出为Excel
- 导出为JSON

### 3. 告警功能
- 急涨急跌告警
- 异常波动告警
- 自定义规则告警

### 4. 数据备份
- 定期备份数据库
- 数据迁移工具
- 云端同步

---

## 📞 技术支持

如有问题，请查看日志文件或参考以下资源：
- API文档: http://localhost:5001/api/health
- 数据库: coin_history_stats.db
- 源代码: /home/user/webapp/

---

**版本**: 1.0.0  
**更新时间**: 2025-12-08  
**作者**: Claude AI Assistant
