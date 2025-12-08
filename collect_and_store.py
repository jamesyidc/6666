#!/usr/bin/env python3
"""
完整的数据采集和存储脚本
包含计次得分和优先级计算功能
"""
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import pytz
import re
import sqlite3

PARENT_FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"  # 首页数据 (包含所有日期文件夹)
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def calculate_count_score_display(count, snapshot_time):
    """计算计次得分显示字符串"""
    hour = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S').hour
    _, _, display = calculate_count_score(count, hour)
    return display

def calculate_count_score_type(count, snapshot_time):
    """计算计次得分类型"""
    hour = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S').hour
    stars, star_type, _ = calculate_count_score(count, hour)
    return f"{star_type}{stars}星"

def calculate_count_score(count_times, current_hour):
    """
    根据计次和当前时间计算得分
    返回: (星级数量, 星级类型, 描述)
    
    规则：
    - 实心星表示好（计次少）
    - 空心星表示差（计次多）
    """
    # 确定时间段
    if current_hour < 6:
        # 截止6点前
        if count_times <= 1:
            return (3, "实心", "★★★")
        elif 1 < count_times <= 2:
            return (2, "实心", "★★☆")
        elif 2 < count_times <= 3:
            return (1, "实心", "★☆☆")
        elif 3 < count_times <= 4:
            return (1, "空心", "☆☆☆")
        elif 4 < count_times <= 5:
            return (2, "空心", "☆☆---")
        else:  # count_times > 5
            return (3, "空心", "☆---")
            
    elif 6 <= current_hour < 12:
        # 截止12点前
        if count_times <= 2:
            return (3, "实心", "★★★")
        elif 2 < count_times <= 3:
            return (2, "实心", "★★☆")
        elif 3 < count_times <= 4:
            return (1, "实心", "★☆☆")
        elif 4 < count_times <= 5:
            return (1, "空心", "☆☆☆")
        elif 5 < count_times <= 6:
            return (2, "空心", "☆☆---")
        else:  # count_times > 6
            return (3, "空心", "☆---")
            
    elif 12 <= current_hour < 18:
        # 截止18点前
        if count_times <= 3:
            return (3, "实心", "★★★")
        elif 3 < count_times <= 4:
            return (2, "实心", "★★☆")
        elif 4 < count_times <= 5:
            return (1, "实心", "★☆☆")
        elif 5 < count_times <= 6:
            return (1, "空心", "☆☆☆")
        elif 6 < count_times <= 7:
            return (2, "空心", "☆☆---")
        else:  # count_times > 7
            return (3, "空心", "☆---")
            
    else:  # 18 <= current_hour < 24
        # 截止22点前
        if count_times <= 4:
            return (3, "实心", "★★★")
        elif 4 < count_times <= 5:
            return (2, "实心", "★★☆")
        elif 5 < count_times <= 6:
            return (1, "实心", "★☆☆")
        elif 6 < count_times <= 7:
            return (1, "空心", "☆☆☆")
        elif 7 < count_times <= 8:
            return (2, "空心", "☆☆---")
        else:  # count_times > 8
            return (3, "空心", "☆---")

def calculate_priority_level(high_ratio_str, low_ratio_str):
    """
    根据最高占比和最低占比计算优先级等级
    
    等级1: 最高占比>90   最低占比>120
    等级2: 最高占比>80   最低占比>120
    等级3: 最高占比>90   最低占比>110
    等级4: 最高占比>70   最低占比>120
    等级5: 最高占比>80   最低占比>110
    等级6: 最高占比<80   最低占比<110
    """
    try:
        high_ratio = float(high_ratio_str.replace('%', '')) if high_ratio_str else 0
        low_ratio = float(low_ratio_str.replace('%', '')) if low_ratio_str else 0
        
        if high_ratio > 90 and low_ratio > 120:
            return "等级1"
        elif high_ratio > 80 and low_ratio > 120:
            return "等级2"
        elif high_ratio > 90 and low_ratio > 110:
            return "等级3"
        elif high_ratio > 70 and low_ratio > 120:
            return "等级4"
        elif high_ratio > 80 and low_ratio > 110:
            return "等级5"
        else:
            return "等级6"
    except:
        return "未知"

def get_today_folder_id():
    """根据当前日期自动查找对应的文件夹ID"""
    now = datetime.now(BEIJING_TZ)
    today_folder_name = now.strftime('%Y-%m-%d')
    
    print(f"🔍 查找今天的文件夹: {today_folder_name}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 访问父文件夹
        parent_url = f"https://drive.google.com/drive/folders/{PARENT_FOLDER_ID}"
        page.goto(parent_url, timeout=20000)
        page.wait_for_timeout(3000)
        
        # 查找今天的文件夹
        items = page.query_selector_all('[data-id]')
        
        for item in items:
            try:
                tooltip = item.get_attribute('data-tooltip') or ''
                data_id = item.get_attribute('data-id') or ''
                
                if today_folder_name in tooltip:
                    print(f"✅ 找到今天的文件夹: {tooltip}")
                    print(f"   ID: {data_id}")
                    browser.close()
                    return data_id
            except:
                pass
        
        browser.close()
        print(f"❌ 未找到今天的文件夹: {today_folder_name}")
        return None

def get_latest_file_data():
    """获取最新文件数据"""
    now = datetime.now(BEIJING_TZ)
    current_hour = now.hour
    
    print(f"当前北京时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前小时: {current_hour}")
    
    # 自动获取今天的文件夹ID
    folder_id = get_today_folder_id()
    if not folder_id:
        print("❌ 无法获取今天的文件夹ID，采集失败")
        return None
    
    # 生成候选文件名
    candidates = []
    for i in range(0, 4):
        # 使用timedelta来正确处理时间减法，避免分钟数为负
        check_time = now.replace(second=0, microsecond=0)
        # 先对齐到10分钟整点
        aligned_minute = (check_time.minute // 10) * 10
        check_time = check_time.replace(minute=aligned_minute)
        # 然后减去i*10分钟
        check_time = check_time - timedelta(minutes=i * 10)
        filename = check_time.strftime('%Y-%m-%d_%H%M.txt')
        candidates.append(filename)
    
    print(f"候选文件: {candidates}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 使用今天的文件夹ID
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        page.goto(folder_url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        
        # 滚动加载
        print("正在滚动加载文件...")
        for i in range(20):
            page.keyboard.press('End')
            page.wait_for_timeout(300)
        
        html = page.content()
        
        # 查找所有文件（使用当前北京时间日期）
        current_date = now.strftime('%Y-%m-%d')
        pattern = rf'{current_date}_(\d{{4}})\.txt'
        found_files = re.findall(pattern, html)
        found_files = sorted(set(found_files), reverse=True)
        
        if found_files:
            latest_time = found_files[0]
            latest_filename = f"{current_date}_{latest_time}.txt"
            print(f"找到最新文件: {latest_filename}")
            
            # 直接从页面HTML中提取文件ID（更可靠的方法）
            # 已经访问过文件夹，直接获取页面内容
            folder_html = page.content()
            
            # 使用正则表达式查找文件名对应的data-id
            pattern = rf'{re.escape(latest_filename)}.*?data-id="([^"]+)"'
            match = re.search(pattern, folder_html)
            
            if match:
                file_id = match.group(1)
                print(f"✅ 提取到文件ID: {file_id}")
                
                if file_id:
                    browser.close()
                    
                    # 使用 requests 直接下载文件内容（更可靠）
                    import requests
                    download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
                    print(f"📥 直接下载文件: {download_url}")
                    
                    try:
                        response = requests.get(download_url, timeout=30)
                        if response.status_code == 200:
                            content = response.text
                            print(f"✅ 文件下载成功，内容长度: {len(content)} 字符")
                            return parse_and_store_data(content, latest_filename, current_hour)
                        else:
                            print(f"❌ 文件下载失败: HTTP {response.status_code}")
                            return None
                    except Exception as e:
                        print(f"❌ 下载文件时出错: {str(e)}")
                        return None
        
        browser.close()
        return None

def parse_and_store_data(content, filename, current_hour):
    """解析并存储文件内容到数据库"""
    # 从文件名提取实际数据时间，而不是采集时间
    # 文件名格式: 2025-12-07_1124.txt
    import re
    match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{4})\.txt', filename)
    if match:
        file_date = match.group(1)
        file_time = match.group(2)
        # 文件时间格式: HHMM -> HH:MM:00
        snapshot_time = f"{file_date} {file_time[:2]}:{file_time[2:]}:00"
        snapshot_date = file_date
    else:
        # 如果无法解析文件名，使用当前时间作为后备
        now = datetime.now(BEIJING_TZ)
        snapshot_time = now.strftime('%Y-%m-%d %H:%M:%S')
        snapshot_date = now.strftime('%Y-%m-%d')
    
    data = {
        '文件名': filename,
        '采集时间': snapshot_time
    }
    
    # 提取基础数据（修复：允许冒号后有空格）
    patterns = {
        '急涨': r'急涨\s*[：:]\s*(\d+)',
        '急跌': r'急跌\s*[：:]\s*(\d+)',
        '状态': r'状态\s*[：:]\s*([^\n\|★]+)',
        '比值': r'比值\s*[：:]\s*([\d.]+)',
        '差值': r'差值\s*[：:]\s*([-\d.]+)',
        '比价最低': r'比价最低\s+(\d+)',
        '比价创新高': r'比价创新高\s+(\d+)',
        '计次': r'透明标签_计次=(\d+)',
    }
    
    # 调试：输出内容片段
    print("\n🔍 内容片段（前2000字符）:")
    clean_content = content[:2000]
    if '急涨' in clean_content:
        print("   找到'急涨'关键字")
        # 查找并打印急涨所在行
        for line in clean_content.split('\n'):
            if '急涨' in line or '急跌' in line:
                print(f"   内容: {line[:150]}")
                break
    else:
        print("   未找到'急涨'关键字（可能在后面）")
        print(f"   内容开头: {clean_content[:200]}")
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            data[key] = match.group(1).strip()  # 去除首尾空格
    
    # 调试：输出提取到的数据
    print("\n📊 提取到的基础数据:")
    for key in ['急涨', '急跌', '状态', '比值', '差值']:
        print(f"   {key}: {data.get(key, '未提取到')}")
    
    # 解析币种数据
    lines = content.split('\n')
    count_rise_10 = 0
    count_fall_10 = 0
    coin_list = []
    
    for line in lines:
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 16:
                try:
                    index_num = int(parts[0].strip())
                    symbol = parts[1].strip()
                    change = float(parts[2].strip()) if parts[2].strip() else 0
                    rush_up = int(parts[3].strip()) if parts[3].strip() else 0
                    rush_down = int(parts[4].strip()) if parts[4].strip() else 0
                    update_time = parts[5].strip()
                    high_price = float(parts[6].strip()) if parts[6].strip() else 0
                    high_time = parts[7].strip()
                    decline = float(parts[8].strip()) if parts[8].strip() else 0
                    change_24h = float(parts[9].strip()) if parts[9].strip() else 0
                    rank = int(parts[12].strip()) if parts[12].strip() else 0
                    current_price = float(parts[13].strip()) if parts[13].strip() else 0
                    ratio1 = parts[14].strip()  # 最高占比
                    ratio2 = parts[15].strip()  # 最低占比
                    
                    # 统计24小时涨跌幅
                    if change_24h >= 10.0:
                        count_rise_10 += 1
                    elif change_24h <= -10.0:
                        count_fall_10 += 1
                    
                    # 计算优先级
                    priority = calculate_priority_level(ratio1, ratio2)
                    
                    coin_list.append({
                        'index_num': index_num,
                        'symbol': symbol,
                        'change': change,
                        'rush_up': rush_up,
                        'rush_down': rush_down,
                        'update_time': update_time,
                        'high_price': high_price,
                        'high_time': high_time,
                        'decline': decline,
                        'change_24h': change_24h,
                        'rank': rank,
                        'current_price': current_price,
                        'ratio1': ratio1,
                        'ratio2': ratio2,
                        'priority': priority
                    })
                except (ValueError, IndexError) as e:
                    pass
    
    data['24h涨幅>=10%'] = count_rise_10
    data['24h跌幅<=-10%'] = count_fall_10
    
    # 计算计次得分
    if '计次' in data:
        count_times = int(data['计次'])
        star_count, star_type, star_display = calculate_count_score(count_times, current_hour)
        data['计次得分_数量'] = star_count
        data['计次得分_类型'] = star_type
        data['计次得分_显示'] = star_display
    
    # 存储到数据库
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    # ===== 数据验证：检查急涨/急跌是否合理 =====
    new_rush_up = int(data.get('急涨', 0))
    new_rush_down = int(data.get('急跌', 0))
    
    # 获取最近一条记录（包括计次）
    cursor.execute("""
        SELECT rush_up, rush_down, count, snapshot_time 
        FROM crypto_snapshots 
        ORDER BY snapshot_time DESC 
        LIMIT 1
    """)
    last_record = cursor.fetchone()
    
    if last_record:
        last_rush_up, last_rush_down, last_count, last_time = last_record
        
        # 解析时间，检查是否跨天重置
        last_dt = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
        current_dt = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S')
        
        # 判断是否跨越了新一天的00:10重置点
        # 规则：如果上一条记录是昨天的，且当前时间是今天00:10之后的第一条，允许重置
        last_date = last_dt.date()
        current_date = current_dt.date()
        is_new_day_reset = False
        
        if current_date > last_date:
            # 跨天了，允许数据重置（不管具体时间）
            is_new_day_reset = True
            print(f"\n🔄 检测到跨天重置 (从 {last_date} 到 {current_date})")
            print(f"   上一天最终值: 急涨={last_rush_up}, 急跌={last_rush_down}")
            print(f"   新一天初始值: 急涨={new_rush_up}, 急跌={new_rush_down}")
        
        # 验证规则：急涨和急跌只能增大或保持不变，不能减小（除非是跨天重置）
        # 如果数据减小，强制使用上一条记录的值（保持单调递增）
        if not is_new_day_reset and (new_rush_up < last_rush_up or new_rush_down < last_rush_down):
            print(f"\n⚠️  数据异常检测！")
            print(f"   上一条记录 ({last_time}): 急涨={last_rush_up}, 急跌={last_rush_down}")
            print(f"   当前数据（源文件）: 急涨={new_rush_up}, 急跌={new_rush_down}")
            
            # 自动修正：保持单调递增
            original_rush_up = new_rush_up
            original_rush_down = new_rush_down
            
            if new_rush_up < last_rush_up:
                print(f"   🔧 自动修正：急涨 {new_rush_up} → {last_rush_up}（保持不变）")
                new_rush_up = last_rush_up
                data['急涨'] = str(last_rush_up)
                
            if new_rush_down < last_rush_down:
                print(f"   🔧 自动修正：急跌 {new_rush_down} → {last_rush_down}（保持不变）")
                new_rush_down = last_rush_down
                data['急跌'] = str(last_rush_down)
            
            # 重新计算差值
            new_diff = new_rush_up - new_rush_down
            data['差值'] = str(new_diff)
            
            print(f"   ✅ 修正后数据: 急涨={new_rush_up}, 急跌={new_rush_down}, 差值={new_diff}")
            print(f"   📝 说明：根据原则'1天内急涨/急跌不能减小'，自动保持为上一时刻的值")
        
        # ===== 原则1b：检查计次是否减小（计次也不能减小） =====
        # ===== 原则2：检查计次是否合理（相邻两轮最多增加1） =====
        new_count = int(data.get('计次', 0))
        
        if not is_new_day_reset and last_count > 0:
            count_change = new_count - last_count
            
            # 原则1b：计次不能减小
            if count_change < 0:
                print(f"\n⚠️  计次减小检测！")
                print(f"   上一条记录 ({last_time}): 计次={last_count}")
                print(f"   当前数据（源文件）: 计次={new_count}")
                print(f"   ❌ 计次减少了 {abs(count_change)}（违反原则1：计次不能减小）")
                
                # 自动修正：保持不变
                print(f"   🔧 自动修正：计次 {new_count} → {last_count}（保持不变）")
                data['计次'] = str(last_count)
                new_count = last_count
                
                # 重新计算计次得分
                count_times = last_count
                star_count, star_type, star_display = calculate_count_score(count_times, current_hour)
                data['计次得分_数量'] = star_count
                data['计次得分_类型'] = star_type
                data['计次得分_显示'] = star_display
                
                print(f"   ✅ 修正后数据: 计次={last_count}")
                print(f"   📝 说明：根据原则'1天内计次不能减小'，自动保持为上一时刻的值")
            
            # 原则2：计次最多增加1
            elif count_change > 1:
                print(f"\n⚠️  计次增加过多检测！")
                print(f"   上一条记录 ({last_time}): 计次={last_count}")
                print(f"   当前数据（源文件）: 计次={new_count}")
                print(f"   ❌ 计次增加了 {count_change}（超过最大允许值1）")
                
                # 自动修正：最多只能增加1
                corrected_count = last_count + 1
                print(f"   🔧 自动修正：计次 {new_count} → {corrected_count}（最多增加1）")
                data['计次'] = str(corrected_count)
                
                # 重新计算计次得分
                count_times = corrected_count
                star_count, star_type, star_display = calculate_count_score(count_times, current_hour)
                data['计次得分_数量'] = star_count
                data['计次得分_类型'] = star_type
                data['计次得分_显示'] = star_display
                
                print(f"   ✅ 修正后数据: 计次={corrected_count}")
                print(f"   📝 说明：根据原则'计次相隔两轮最多增加1'，自动修正为 {last_count}+1")
    
    # 检查是否已经存在相同时间的记录（避免重复采集）
    cursor.execute("""
        SELECT id FROM crypto_snapshots 
        WHERE snapshot_time = ?
    """, (snapshot_time,))
    
    existing = cursor.fetchone()
    if existing:
        print(f"\n⚠️  数据已存在: {snapshot_time} (ID: {existing[0]})")
        print(f"   跳过重复采集")
        conn.close()
        return None
    
    # 插入快照数据
    cursor.execute("""
        INSERT INTO crypto_snapshots (
            snapshot_time, snapshot_date, rush_up, rush_down, diff, count,
            ratio, status, green_count, percentage, filename, created_at,
            count_score_display, count_score_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        snapshot_time,
        snapshot_date,
        int(data.get('急涨', 0)),
        int(data.get('急跌', 0)),
        int(data.get('差值', 0)),
        int(data.get('计次', 0)),
        float(data.get('比值', 0)),
        data.get('状态', ''),
        0,  # green_count (暂时设为0)
        '',  # percentage (暂时为空)
        filename,
        snapshot_time,
        # 计算计次得分
        calculate_count_score_display(int(data.get('计次', 0)), snapshot_time),
        calculate_count_score_type(int(data.get('计次', 0)), snapshot_time)
    ))
    
    snapshot_id = cursor.lastrowid
    
    # 插入币种数据
    for coin in coin_list:
        cursor.execute("""
            INSERT INTO crypto_coin_data (
                snapshot_id, snapshot_time, symbol, index_order,
                change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h,
                rank, current_price, ratio1, ratio2,
                priority_level, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_id,
            snapshot_time,
            coin['symbol'],
            coin['index_num'],
            coin['change'],
            coin['rush_up'],
            coin['rush_down'],
            coin['update_time'],
            coin['high_price'],
            coin['high_time'],
            coin['decline'],
            coin['change_24h'],
            coin['rank'],
            coin['current_price'],
            coin['ratio1'],
            coin['ratio2'],
            coin['priority'],
            snapshot_time
        ))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 数据已存储到数据库")
    print(f"   快照ID: {snapshot_id}")
    print(f"   币种数量: {len(coin_list)}")
    
    data['coin_list'] = coin_list
    return data

def main():
    print("="*80)
    print("开始采集数据...")
    print("="*80)
    
    result = get_latest_file_data()
    
    if result:
        print("\n" + "="*80)
        print("✅ 数据采集成功!")
        print("="*80)
        
        # 按顺序显示数据
        display_order = [
            '文件名', '采集时间', 
            '急涨', '急跌', '状态', '比值', '差值',
            '比价最低', '比价创新高', 
            '计次', '计次得分_显示', '计次得分_类型',
            '24h涨幅>=10%', '24h跌幅<=-10%'
        ]
        
        for key in display_order:
            if key in result:
                print(f"{key:15s}: {result[key]}")
        
        # 显示优先级统计
        if 'coin_list' in result:
            priority_stats = {}
            for coin in result['coin_list']:
                level = coin['priority']
                priority_stats[level] = priority_stats.get(level, 0) + 1
            
            print("\n优先级统计:")
            for level in ['等级1', '等级2', '等级3', '等级4', '等级5', '等级6', '未知']:
                count = priority_stats.get(level, 0)
                if count > 0:
                    print(f"  {level}: {count} 个币种")
        
        return result
    else:
        print("\n❌ 数据采集失败")
        return None

if __name__ == '__main__':
    main()
