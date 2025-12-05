#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恐慌清洗指标数据采集器 - 后台服务
每3分钟自动采集一次数据
"""

import asyncio
import time
from datetime import datetime
from panic_wash_new import MockPanicWashCalculator, PanicWashCalculator
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class PanicWashCollectorService:
    """恐慌清洗数据采集服务"""
    
    def __init__(self, db_path='crypto_data.db', interval=180):
        """
        初始化采集服务
        :param db_path: 数据库路径
        :param interval: 采集间隔（秒），默认180秒=3分钟
        """
        self.db_path = db_path
        self.interval = interval
        self.running = False
        
        # 选择合适的计算器
        if PLAYWRIGHT_AVAILABLE:
            self.calculator = PanicWashCalculator(db_path)
            print("✅ 使用Playwright实时爬取模式")
        else:
            self.calculator = MockPanicWashCalculator(db_path)
            print("⚠️ 使用模拟数据模式")
    
    async def collect_once(self):
        """执行一次数据采集"""
        try:
            print(f"\n{'='*70}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始采集恐慌清洗数据...")
            print(f"{'='*70}")
            
            result = await self.calculator.run_once()
            
            if result.get('success'):
                print(f"✅ 采集成功！")
                print(f"   恐慌指数: {result['panic_index']:.8f}")
                print(f"   24H爆仓人数: {result['hour_24_people']:,}")
                print(f"   全网持仓: ${result['total_position']:,.2f}")
                return True
            else:
                print(f"❌ 采集失败: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ 采集异常: {str(e)}")
            return False
    
    async def run(self):
        """持续运行采集服务"""
        self.running = True
        
        print(f"\n{'='*70}")
        print(f"🚀 恐慌清洗指标采集服务启动")
        print(f"{'='*70}")
        print(f"数据库: {self.db_path}")
        print(f"采集间隔: {self.interval}秒 ({self.interval/60}分钟)")
        print(f"模式: {'实时爬取' if PLAYWRIGHT_AVAILABLE else '模拟数据'}")
        print(f"{'='*70}\n")
        
        # 启动时立即采集一次
        await self.collect_once()
        
        # 循环采集
        while self.running:
            try:
                print(f"\n⏰ 等待 {self.interval} 秒后进行下一次采集...")
                await asyncio.sleep(self.interval)
                
                if self.running:
                    await self.collect_once()
                    
            except KeyboardInterrupt:
                print("\n⚠️ 收到停止信号...")
                self.stop()
                break
            except Exception as e:
                print(f"❌ 服务异常: {str(e)}")
                # 发生异常后等待一段时间再继续
                await asyncio.sleep(60)
    
    def stop(self):
        """停止采集服务"""
        self.running = False
        print("✅ 采集服务已停止")

async def main():
    """主函数"""
    # 创建采集服务（3分钟间隔）
    service = PanicWashCollectorService(
        db_path='crypto_data.db',
        interval=180  # 3分钟
    )
    
    # 运行服务
    try:
        await service.run()
    except KeyboardInterrupt:
        print("\n⚠️ 服务被用户终止")
        service.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见！")
