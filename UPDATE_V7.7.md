# v7.7 更新日志 - 信号历史曲线和10分钟自动更新

## 更新时间
2025-12-02 21:23:00

## 更新概述
实现了信号监控的历史曲线图功能，并添加10分钟自动更新机制。系统现在能够自动保存历史数据并以可视化曲线展示做空/做多信号的变化趋势。

---

## 🎯 核心功能

### 1. 历史数据自动保存
- ✅ **自动存储**：每次调用信号API时自动将数据保存到数据库
- ✅ **数据表设计**：
  - `signal_history` - 存储做空/做多信号历史
  - `panic_history` - 存储恐慌清洗指标历史
- ✅ **唯一约束**：基于时间戳防止重复数据
- ✅ **时间索引**：支持按日期和时间范围快速查询

### 2. 历史数据查询API
**新增API端点**：
- `GET /api/monitor/signal/history` - 查询信号历史数据
- `GET /api/monitor/panic/history` - 查询恐慌清洗历史数据

**查询参数**：
- `date` (可选) - 指定日期（格式：YYYY-MM-DD）
- `hours` (可选) - 查询最近N小时数据（默认：24小时）

**示例**：
```bash
# 查询最近24小时数据
curl http://localhost:5001/api/monitor/signal/history?hours=24

# 查询指定日期数据
curl http://localhost:5001/api/monitor/signal/history?date=2025-12-02
```

### 3. 信号监控 v2.0 页面
**全新升级的监控页面**，包含：

#### 🎨 界面设计
- **双卡片布局**：做空信号（红色）+ 做多信号（蓝色）
- **历史曲线图**：Chart.js 实现的平滑曲线
- **响应式设计**：完美适配手机和桌面
- **渐变背景**：紫色渐变提升视觉效果

#### 📊 曲线图特性
- **双曲线显示**：同时显示做空和做多信号
- **颜色区分**：
  - 做空信号：红色曲线（#f5576c）
  - 做多信号：蓝色曲线（#00f2fe）
- **填充渐变**：曲线下方带透明填充
- **平滑过渡**：tension: 0.4 实现曲线平滑
- **交互提示**：鼠标悬停显示详细数据
- **时间格式化**：X轴仅显示时:分（HH:MM）

#### ⏱️ 10分钟自动更新
- **倒计时显示**：实时显示距离下次更新的时间
- **格式**：X分Y秒（例如：9分30秒）
- **颜色提示**：绿色文字，醒目易见
- **自动更新**：倒计时归零自动刷新数据
- **更新间隔**：600秒（10分钟）

---

## 📁 新增/修改文件

### 1. `crypto_database.py` (修改)
**新增数据表**：

#### signal_history 表
```sql
CREATE TABLE signal_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time TEXT NOT NULL,        -- 快照时间 (YYYY-MM-DD HH:MM:SS)
    snapshot_date TEXT NOT NULL,        -- 快照日期 (YYYY-MM-DD)
    short_value INTEGER,                -- 做空信号值
    short_change INTEGER,               -- 做空变化
    long_value INTEGER,                 -- 做多信号值
    long_change INTEGER,                -- 做多变化
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_time)
)
```

#### panic_history 表
```sql
CREATE TABLE panic_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    panic_indicator TEXT,               -- 恐慌清洗指标
    trend_rating TEXT,                  -- 趋势评级
    market_zone TEXT,                   -- 市场区间
    liquidation_24h_count TEXT,         -- 24h爆仓人数
    liquidation_24h_amount TEXT,        -- 24h爆仓金额
    total_position TEXT,                -- 全网持仓量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_time)
)
```

**新增方法**：
- `save_signal_data(signal_data)` - 保存信号数据
- `save_panic_data(panic_data)` - 保存恐慌清洗数据
- `get_signal_history(date, hours)` - 查询信号历史
- `get_panic_history(date, hours)` - 查询恐慌清洗历史

### 2. `crypto_server_demo.py` (修改)
**修改内容**：

#### 导入更新
```python
from flask import Flask, jsonify, send_from_directory, request  # 添加 request
```

#### API端点更新
```python
@app.route('/api/monitor/signal')
def get_signal_data():
    """获取信号数据并自动保存到数据库"""
    data = monitor_reader.get_signal_data()
    db.save_signal_data(data)  # 自动保存
    return jsonify({'success': True, 'data': data})

@app.route('/api/monitor/signal/history')
def get_signal_history():
    """查询历史信号数据"""
    date = request.args.get('date')
    hours = request.args.get('hours', 24, type=int)
    history = db.get_signal_history(date=date, hours=hours)
    return jsonify({'success': True, 'data': history, 'count': len(history)})
```

#### 路由更新
```python
@app.route('/signal')
def signal_monitor():
    """信号监控页面 v2 - 包含历史曲线图"""
    return send_from_directory('.', 'signal_monitor_v2.html')

@app.route('/signal/v1')
def signal_monitor_v1():
    """信号监控页面 v1 - 旧版本（无曲线图）"""
    return send_from_directory('.', 'signal_monitor.html')
```

### 3. `signal_monitor_v2.html` (新增)
**全新的监控页面**，包含：

#### HTML结构
- 头部：标题 + 副标题
- 主内容区：
  - 2个数据卡片（做空/做多）
  - 1个曲线图卡片
- 更新时间显示
- 倒计时显示

#### JavaScript功能
```javascript
// 初始化图表
function initChart() { ... }

// 加载当前数据
async function loadCurrentData() { ... }

// 加载历史数据
async function loadHistoryData() { ... }

// 更新曲线图
function updateChart(historyData) { ... }

// 倒计时更新
function updateCountdown() { ... }
```

#### 样式特性
- 渐变背景：紫色渐变（#667eea → #764ba2）
- 卡片阴影：0 10px 40px rgba(0,0,0,0.2)
- 曲线图高度：400px（桌面）/ 300px（移动）
- 响应式断点：900px

---

## 🔄 工作流程

### 数据流程
```
用户访问页面
    ↓
页面初始化
    ↓
调用 /api/monitor/signal (获取当前数据)
    ├→ 数据自动保存到 signal_history 表
    └→ 更新卡片显示
    ↓
调用 /api/monitor/signal/history (获取历史数据)
    ├→ 从数据库查询最近24小时数据
    └→ 更新曲线图
    ↓
启动倒计时 (600秒)
    ├→ 每秒更新显示
    └→ 归零时重新获取数据
```

### 更新机制
1. **初次加载**：
   - 获取当前信号数据
   - 查询历史数据（24小时）
   - 绘制曲线图
   - 启动倒计时

2. **自动更新**（每10分钟）：
   - 倒计时归零触发
   - 重新获取当前数据
   - 重新查询历史数据
   - 更新曲线图
   - 重置倒计时为600秒

3. **倒计时更新**（每秒）：
   - nextUpdateTime--
   - 更新显示（X分Y秒）
   - 检查是否归零

---

## 📊 数据示例

### 信号数据 API 响应
```json
{
  "success": true,
  "data": {
    "short": "126",
    "short_change": "0",
    "long": "0",
    "long_change": "0",
    "update_time": "2025-12-02 21:22:31"
  }
}
```

### 历史数据 API 响应
```json
{
  "success": true,
  "count": 15,
  "data": [
    {
      "time": "2025-12-02 21:22:18",
      "short": 126,
      "short_change": 0,
      "long": 0,
      "long_change": 0
    },
    {
      "time": "2025-12-02 21:22:28",
      "short": 126,
      "short_change": 0,
      "long": 0,
      "long_change": 0
    }
    // ... 更多记录
  ]
}
```

---

## ✅ 测试结果

### 1. 数据库测试
```
✅ signal_history 表创建成功
✅ panic_history 表创建成功
✅ 数据保存功能正常
✅ 历史查询功能正常
```

### 2. API测试
```
✅ GET /api/monitor/signal - 200 OK
✅ GET /api/monitor/signal/history - 200 OK
✅ 数据自动保存 - 正常
✅ 历史记录数: 15 条
```

### 3. 页面测试
```
✅ 页面加载成功 - 13,769 字节
✅ 曲线图渲染正常
✅ 倒计时显示正常
✅ 数据更新正常
✅ 响应式布局正常
```

### 4. 曲线图测试
```
✅ Chart.js 加载成功
✅ 双曲线显示正常
✅ 颜色区分清晰
✅ 交互提示正常
✅ 平滑过渡效果正常
```

---

## 🌐 访问信息

### 服务器地址
**主地址**: https://5001-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai

### 监控页面
- 📊 **信号监控 v2** (推荐): `/signal`
  - 包含历史曲线图
  - 10分钟自动更新
  - 倒计时显示
  
- 📊 **信号监控 v1**: `/signal/v1`
  - 无曲线图
  - 10秒自动刷新
  - 简洁版本

- 📊 **恐慌清洗监控**: `/panic`
  - 10秒自动刷新
  - 待添加曲线图（未来版本）

### API端点
- 🔗 **当前信号数据**: `GET /api/monitor/signal`
- 🔗 **信号历史数据**: `GET /api/monitor/signal/history?hours=24`
- 🔗 **恐慌清洗数据**: `GET /api/monitor/panic`
- 🔗 **恐慌历史数据**: `GET /api/monitor/panic/history?hours=24`

---

## 📊 当前状态

### 数据源
- ⚠️ **当前使用**: 演示数据（固定值）
- 📌 **原因**: Google Drive API 未配置
- ✅ **服务状态**: 正常运行
- 🔄 **更新频率**: 10分钟/次（页面自动更新）

### 历史数据
- 📊 **记录数**: 15 条
- 📅 **时间范围**: 最近1小时
- 💾 **存储位置**: `crypto_data.db` 数据库
- 🔍 **查询方式**: API 端点或直接查询数据库

### 数据内容
#### 当前信号
- 做空: 126
- 做空变化: 0
- 做多: 0
- 做多变化: 0

---

## 🚀 使用指南

### 1. 访问监控页面
直接访问：
```
https://5001-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/signal
```

### 2. 查看历史曲线
- 曲线图自动显示最近24小时数据
- 红色曲线 = 做空信号
- 蓝色曲线 = 做多信号
- 鼠标悬停查看具体数值

### 3. 等待自动更新
- 页面显示倒计时
- 每10分钟自动更新一次
- 倒计时归零时自动刷新数据

### 4. 查询历史数据（API）
```bash
# 查询最近12小时
curl http://localhost:5001/api/monitor/signal/history?hours=12

# 查询今天的数据
curl http://localhost:5001/api/monitor/signal/history?date=2025-12-02
```

---

## 🔧 技术细节

### Chart.js 配置
```javascript
{
  type: 'line',
  data: {
    datasets: [
      {
        label: '做空信号',
        borderColor: '#f5576c',
        backgroundColor: 'rgba(245, 87, 108, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: '做多信号',
        borderColor: '#00f2fe',
        backgroundColor: 'rgba(0, 242, 254, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    }
  }
}
```

### 倒计时逻辑
```javascript
let nextUpdateTime = 600; // 10分钟

function updateCountdown() {
    nextUpdateTime--;
    
    if (nextUpdateTime <= 0) {
        nextUpdateTime = 600; // 重置
        loadCurrentData();    // 重新获取数据
        loadHistoryData();
    }
    
    const minutes = Math.floor(nextUpdateTime / 60);
    const seconds = nextUpdateTime % 60;
    // 显示：X分Y秒
}

// 每秒调用一次
setInterval(updateCountdown, 1000);
```

---

## 📝 注意事项

### 1. 数据更新频率
- ⏱️ **页面更新**: 10分钟/次（自动）
- ⏱️ **数据保存**: 每次API调用时（自动）
- ⏱️ **倒计时刷新**: 1秒/次

### 2. 历史数据限制
- 📊 默认查询24小时数据
- 💾 数据库无自动清理（需手动维护）
- 🔍 支持按日期或小时数查询

### 3. 性能考虑
- 📈 曲线图最多建议显示100个数据点
- 💾 数据库定期备份
- 🔄 长期运行需考虑数据清理策略

---

## 🎉 总结

v7.7 更新成功实现了信号监控的历史数据可视化功能：

✅ **数据持久化**: 自动保存历史信号数据  
✅ **可视化展示**: Chart.js 实现平滑曲线图  
✅ **自动更新**: 10分钟定时更新机制  
✅ **倒计时显示**: 实时显示更新进度  
✅ **历史查询**: 支持按时间范围查询  
✅ **响应式设计**: 完美适配多种设备  

**推荐使用**：信号监控 v2.0 页面（/signal）

**访问地址**: https://5001-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/signal

---

**更新作者**: Claude Code Assistant  
**更新日期**: 2025-12-02  
**版本**: v7.7  
**提交哈希**: 1978892
