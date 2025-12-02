#!/usr/bin/env python3
"""
Google Drive 数据读取模块 - 从共享文件夹自动读取最新监控数据
"""

import os
import io
import re
from datetime import datetime
from typing import Dict, Optional, List
import pytz

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google.oauth2 import service_account
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    print("⚠️  Google Drive API 库未安装，将使用备用方案")


class GDriveReader:
    """Google Drive 数据读取器"""
    
    def __init__(self, folder_id: str = '1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ'):
        """
        初始化 Google Drive 读取器
        
        Args:
            folder_id: Google Drive 共享文件夹 ID
        """
        self.folder_id = folder_id
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        self.service = None
        self.credentials_path = '/home/user/webapp/gdrive_credentials.json'
        
        # 尝试初始化 Google Drive API
        if GDRIVE_AVAILABLE and os.path.exists(self.credentials_path):
            try:
                self._init_gdrive_service()
            except Exception as e:
                print(f"⚠️  初始化 Google Drive API 失败: {e}")
    
    def _init_gdrive_service(self):
        """初始化 Google Drive API 服务"""
        try:
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=credentials)
            print("✅ Google Drive API 已初始化")
        except Exception as e:
            print(f"❌ 初始化 Google Drive API 失败: {e}")
            self.service = None
    
    def get_today_folder_name(self) -> str:
        """获取今天的文件夹名称（北京时间，格式: YYYY-MM-DD）"""
        now = datetime.now(self.beijing_tz)
        return now.strftime('%Y-%m-%d')
    
    def find_folder_by_name(self, parent_id: str, folder_name: str) -> Optional[str]:
        """
        在指定父文件夹中查找子文件夹
        
        Args:
            parent_id: 父文件夹 ID
            folder_name: 要查找的文件夹名称
            
        Returns:
            找到的文件夹 ID，如果未找到则返回 None
        """
        if not self.service:
            return None
        
        try:
            query = f"'{parent_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=10
            ).execute()
            
            items = results.get('files', [])
            if items:
                return items[0]['id']
            return None
        except Exception as e:
            print(f"❌ 查找文件夹失败: {e}")
            return None
    
    def find_file_by_name(self, parent_id: str, file_name: str) -> Optional[str]:
        """
        在指定文件夹中查找文件
        
        Args:
            parent_id: 父文件夹 ID
            file_name: 要查找的文件名
            
        Returns:
            找到的文件 ID，如果未找到则返回 None
        """
        if not self.service:
            return None
        
        try:
            query = f"'{parent_id}' in parents and name='{file_name}' and mimeType!='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                pageSize=10,
                orderBy='modifiedTime desc'
            ).execute()
            
            items = results.get('files', [])
            if items:
                return items[0]['id']
            return None
        except Exception as e:
            print(f"❌ 查找文件失败: {e}")
            return None
    
    def download_file_content(self, file_id: str) -> Optional[str]:
        """
        下载文件内容
        
        Args:
            file_id: 文件 ID
            
        Returns:
            文件内容（字符串），如果失败则返回 None
        """
        if not self.service:
            return None
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # 尝试多种编码解码
            content = fh.getvalue()
            for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            print("❌ 无法解码文件内容")
            return None
        except Exception as e:
            print(f"❌ 下载文件失败: {e}")
            return None
    
    def read_signal_txt(self) -> Optional[Dict]:
        """
        读取今天的信号.txt文件
        
        Returns:
            解析后的信号数据字典，如果失败则返回 None
        """
        if not self.service:
            print("⚠️  Google Drive API 未初始化")
            return None
        
        try:
            # 1. 查找今天的日期文件夹
            today_folder = self.get_today_folder_name()
            print(f"🔍 查找日期文件夹: {today_folder}")
            
            folder_id = self.find_folder_by_name(self.folder_id, today_folder)
            if not folder_id:
                print(f"❌ 未找到日期文件夹: {today_folder}")
                return None
            
            print(f"✅ 找到日期文件夹: {folder_id}")
            
            # 2. 查找信号.txt文件
            file_id = self.find_file_by_name(folder_id, '信号.txt')
            if not file_id:
                print("❌ 未找到 信号.txt 文件")
                return None
            
            print(f"✅ 找到 信号.txt 文件: {file_id}")
            
            # 3. 下载并解析文件内容
            content = self.download_file_content(file_id)
            if not content:
                return None
            
            # 4. 解析数据
            return self._parse_signal_data(content)
        
        except Exception as e:
            print(f"❌ 读取信号数据失败: {e}")
            return None
    
    def read_panic_txt(self) -> Optional[Dict]:
        """
        读取今天的恐慌清洗.txt文件
        
        Returns:
            解析后的恐慌清洗数据字典，如果失败则返回 None
        """
        if not self.service:
            print("⚠️  Google Drive API 未初始化")
            return None
        
        try:
            # 1. 查找今天的日期文件夹
            today_folder = self.get_today_folder_name()
            print(f"🔍 查找日期文件夹: {today_folder}")
            
            folder_id = self.find_folder_by_name(self.folder_id, today_folder)
            if not folder_id:
                print(f"❌ 未找到日期文件夹: {today_folder}")
                return None
            
            print(f"✅ 找到日期文件夹: {folder_id}")
            
            # 2. 查找恐慌清洗.txt文件
            file_id = self.find_file_by_name(folder_id, '恐慌清洗.txt')
            if not file_id:
                print("❌ 未找到 恐慌清洗.txt 文件")
                return None
            
            print(f"✅ 找到 恐慌清洗.txt 文件: {file_id}")
            
            # 3. 下载并解析文件内容
            content = self.download_file_content(file_id)
            if not content:
                return None
            
            # 4. 解析数据
            return self._parse_panic_data(content)
        
        except Exception as e:
            print(f"❌ 读取恐慌清洗数据失败: {e}")
            return None
    
    def _parse_signal_data(self, content: str) -> Optional[Dict]:
        """
        解析信号.txt内容
        格式: 126|0|0|0|2025-12-02 20:56:01
        字段: 做空|变化|做多|变化|时间
        """
        try:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                
                # 解析数据行
                parts = line.split('|')
                if len(parts) >= 5:
                    return {
                        'short': parts[0].strip(),
                        'short_change': parts[1].strip(),
                        'long': parts[2].strip(),
                        'long_change': parts[3].strip(),
                        'update_time': parts[4].strip()
                    }
            
            return None
        except Exception as e:
            print(f"❌ 解析信号数据失败: {e}")
            return None
    
    def _parse_panic_data(self, content: str) -> Optional[Dict]:
        """
        解析恐慌清洗.txt内容
        格式: 10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
        字段: 恐慌清洗指标|趋势评级-市场区间-24h爆仓人数-24h爆仓金额-全网持仓量-时间
        """
        try:
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                
                # 解析数据行
                parts = line.split('|')
                if len(parts) >= 2:
                    # 第一部分: 恐慌清洗指标
                    panic_indicator = parts[0].strip()
                    
                    # 第二部分: 其他数据（用-分隔）
                    other_data = parts[1].strip()
                    
                    # 使用正则表达式提取最后的时间部分
                    time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})$', other_data)
                    if time_match:
                        update_time = time_match.group(1)
                        # 去掉时间后的剩余部分
                        data_without_time = other_data[:time_match.start()].rstrip('-')
                        
                        # 分割剩余数据
                        other_parts = data_without_time.split('-')
                        
                        if len(other_parts) >= 5:
                            return {
                                'panic_indicator': panic_indicator,
                                'trend_rating': other_parts[0].strip(),
                                'market_zone': other_parts[1].strip(),
                                'liquidation_24h_count': other_parts[2].strip(),
                                'liquidation_24h_amount': other_parts[3].strip(),
                                'total_position': other_parts[4].strip(),
                                'update_time': update_time
                            }
            
            return None
        except Exception as e:
            print(f"❌ 解析恐慌清洗数据失败: {e}")
            return None


# 测试代码
if __name__ == '__main__':
    reader = GDriveReader()
    
    print("\n" + "="*60)
    print("测试 Google Drive 数据读取")
    print("="*60)
    
    # 测试读取信号数据
    print("\n📊 读取信号数据:")
    signal_data = reader.read_signal_txt()
    if signal_data:
        print(f"✅ 成功读取: {signal_data}")
    else:
        print("❌ 读取失败")
    
    # 测试读取恐慌清洗数据
    print("\n📊 读取恐慌清洗数据:")
    panic_data = reader.read_panic_txt()
    if panic_data:
        print(f"✅ 成功读取: {panic_data}")
    else:
        print("❌ 读取失败")
