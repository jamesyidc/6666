# 加密货币得分系统 V1.0

## 📊 系统概述

这是一个加密货币做多/做空评分统计系统，能够：
- 采集多个币种在不同时间范围的得分数据
- 计算各时间段的平均做多得分、做空得分和差值
- 提供可视化的Web界面和JSON API接口
- 自动每3分钟更新一次数据

## 🎯 核心功能

### 1. 多时间范围分析
支持6个时间范围的得分统计：
- **3分钟** - 超短期趋势
- **1小时** - 短期趋势
- **3小时** - 中短期趋势
- **6小时** - 中期趋势
- **12小时** - 中长期趋势
- **24小时** - 长期趋势

### 2. 统计指标
对每个时间范围计算：
- ✅ 平均做多得分
- ✅ 平均做空得分  
- ✅ 平均差值（多空差异）
- ✅ 趋势方向（看多📈 / 看空📉）
- ✅ 参与币种数量

### 3. 币种覆盖
目前支持19个主流加密货币：
```
BTC, ETH, BNB, SOL, DOT, LINK, ADA, FIL, DOGE,
UNI, TAO, CFX, BCH, XLM, HBAR, ETC, AVAX, MATIC, OKB
```

## 🚀 快速开始

### 启动服务
```bash
cd /home/user/webapp
python3 score_system.py
```

### 访问系统
- **Web界面**: https://5009-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai
- **本地访问**: http://localhost:5009

## 📡 API接口

### 1. 获取统计数据
```bash
GET /api/score/statistics
```

**响应示例：**
```json
{
  "update_time": "2025-12-03 15:16:46",
  "statistics": [
    {
      "time_range": "3m",
      "avg_long_score": 50.87,
      "avg_short_score": 51.37,
      "avg_diff": -0.5,
      "coin_count": 19,
      "trend": "📉 看空"
    },
    {
      "time_range": "1h",
      "avg_long_score": 45.11,
      "avg_short_score": 44.33,
      "avg_diff": 0.77,
      "coin_count": 19,
      "trend": "📈 看多"
    }
    // ... 其他时间范围
  ]
}
```

### 2. 获取各币种详细得分
```bash
GET /api/score/coins?hours=24
```

**参数：**
- `hours` - 获取最近N小时的数据（默认24）

**响应示例：**
```json
{
  "BTC-USDT-SWAP": {
    "3m": {
      "long_score": 53.68,
      "short_score": 56.03,
      "diff": -2.35,
      "update_time": "2025-12-03 15:16:46"
    },
    "1h": {
      "long_score": 41.85,
      "short_score": 46.0,
      "diff": -4.15,
      "update_time": "2025-12-03 15:16:46"
    }
    // ... 其他时间范围
  },
  "ETH-USDT-SWAP": {
    // ... 类似结构
  }
  // ... 其他币种
}
```

### 3. 手动刷新数据
```bash
GET /api/score/refresh
```

**响应：**
```json
{
  "success": true,
  "message": "数据刷新成功",
  "time": "2025-12-03 15:20:00"
}
```

## 💾 数据库结构

### score_history 表
存储历史得分记录：
```sql
CREATE TABLE score_history (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,           -- 币种符号
    time_range TEXT NOT NULL,       -- 时间范围 (3m, 1h, 3h, 6h, 12h, 24h)
    long_score REAL,                -- 做多得分
    short_score REAL,               -- 做空得分
    score_diff REAL,                -- 得分差值
    data_source TEXT,               -- 数据来源
    record_time DATETIME            -- 记录时间
);
```

### score_statistics 表
存储统计数据：
```sql
CREATE TABLE score_statistics (
    id INTEGER PRIMARY KEY,
    time_range TEXT NOT NULL,       -- 时间范围
    avg_long_score REAL,            -- 平均做多得分
    avg_short_score REAL,           -- 平均做空得分
    avg_diff REAL,                  -- 平均差值
    coin_count INTEGER,             -- 币种数量
    update_time DATETIME            -- 更新时间
);
```

## 🔄 自动更新

系统会自动执行以下操作：
1. **启动时**：立即采集一次数据并计算统计
2. **后台线程**：每3分钟自动更新一次
3. **数据存储**：所有历史数据都会保存到数据库

## 📊 Web界面特性

### 统计卡片
- 渐变色彩设计
- 清晰的多空得分对比
- 实时趋势指示（📈看多 / 📉看空）
- 悬停动画效果

### 详细表格
- 包含所有币种的完整数据
- 按时间范围分列显示
- 颜色编码：
  - 🟢 绿色 = 做多得分
  - 🔴 红色 = 做空得分
  - 差值正数 = 绿色高亮
  - 差值负数 = 红色高亮

### 实时刷新
- 手动刷新按钮
- 自动每3分钟刷新一次
- 刷新状态提示

## 🔧 技术栈

- **后端**: Python 3, Flask
- **数据库**: SQLite3
- **前端**: HTML5, CSS3, JavaScript (原生)
- **数据采集**: 多线程定时任务
- **API**: RESTful JSON接口

## 📁 相关文件

```
/home/user/webapp/
├── score_system.py           # 主程序（后端 + API）
├── score_system.html         # Web前端页面
├── crypto_data.db           # SQLite数据库
└── score_system.log         # 运行日志
```

## 🎨 使用场景

1. **趋势分析**：观察不同时间范围的多空趋势
2. **市场情绪**：通过多空差值判断市场情绪
3. **币种对比**：比较不同币种的得分表现
4. **历史追踪**：查看历史得分变化趋势

## 📈 数据说明

### 得分范围
- 得分范围：0-100
- 50分为中性
- >50 偏向做多
- <50 偏向做空

### 差值解读
- 正差值（绿色）：做多力量强于做空
- 负差值（红色）：做空力量强于做多
- 绝对值越大，多空分歧越明显

## 🔐 安全说明

⚠️ **注意**：
- 当前使用模拟数据生成器
- 生产环境需要接入真实数据源API
- 建议添加数据源验证和异常处理

## 🚧 后续优化

### 计划功能
- [ ] 接入真实数据源API
- [ ] 添加历史趋势图表
- [ ] 增加更多统计指标（如标准差、极值等）
- [ ] 支持自定义币种列表
- [ ] 添加告警功能（异常波动提醒）
- [ ] 数据导出功能（CSV/Excel）
- [ ] 用户自定义时间范围

### 性能优化
- [ ] 数据库查询优化
- [ ] 添加数据缓存层
- [ ] API响应压缩
- [ ] 分页加载大数据集

## 📞 问题反馈

如遇到问题，请检查：
1. 服务是否正常运行：`ps aux | grep score_system`
2. 查看日志：`tail -f score_system.log`
3. 数据库是否正常：`sqlite3 crypto_data.db "SELECT COUNT(*) FROM score_history;"`

---

**版本**: V1.0  
**更新时间**: 2025-12-03  
**状态**: ✅ 运行中  
**访问地址**: https://5009-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai
