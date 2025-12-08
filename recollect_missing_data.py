#!/usr/bin/env python3
"""
批量重新采集缺失的数据文件
"""
import sys
import re
import requests
from collect_and_store import parse_and_store_data, get_today_folder_id
from playwright.sync_api import sync_playwright

def recollect_file(folder_id, filename, current_hour):
    """重新采集单个文件（使用 Playwright）"""
    print(f"\n{'='*80}")
    print(f"重新采集: {filename}")
    print('='*80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 访问文件夹
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        page.goto(folder_url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        
        # 滚动加载
        print("正在滚动加载文件...")
        for i in range(20):
            page.keyboard.press('End')
            page.wait_for_timeout(300)
        
        html = page.content()
        
        # 查找文件ID
        pattern = rf'{re.escape(filename)}.*?data-id="([^"]+)"'
        match = re.search(pattern, html)
        
        browser.close()
        
        if not match:
            print(f"❌ 文件不存在: {filename}")
            return False
        
        file_id = match.group(1)
        print(f"✅ 找到文件 (ID: {file_id})")
        
        # 下载文件
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            response = requests.get(download_url, timeout=30)
            if response.status_code != 200:
                print(f"❌ 下载失败: HTTP {response.status_code}")
                return False
            
            content = response.text
            print(f"✅ 文件下载成功，内容长度: {len(content)} 字符")
            
            # 解析并存储
            result = parse_and_store_data(content, filename, current_hour)
            if result:
                print(f"✅ 数据存储成功")
                return True
            else:
                print(f"⚠️  数据未存储（可能已存在或被拒绝）")
                return False
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False

def main():
    """主函数"""
    # 要重新采集的文件列表
    files_to_collect = [
        ('2025-12-08_0158.txt', 1),
        ('2025-12-08_0208.txt', 2),
        ('2025-12-08_0218.txt', 2),
        ('2025-12-08_0228.txt', 2),
    ]
    
    print("="*80)
    print("批量重新采集缺失数据")
    print("="*80)
    
    # 获取今天的文件夹 ID
    folder_id = get_today_folder_id()
    if not folder_id:
        print("❌ 无法获取今天的文件夹 ID")
        sys.exit(1)
    
    print(f"✅ 文件夹 ID: {folder_id}")
    
    # 逐个采集
    success_count = 0
    for filename, hour in files_to_collect:
        if recollect_file(folder_id, filename, hour):
            success_count += 1
    
    print(f"\n{'='*80}")
    print(f"采集完成！成功: {success_count}/{len(files_to_collect)}")
    print('='*80)

if __name__ == '__main__':
    main()
