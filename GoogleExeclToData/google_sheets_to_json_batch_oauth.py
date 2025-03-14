#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd

# 定义访问Google Sheets所需的权限范围
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def setup_credentials(creds_file):
    """设置Google Sheets API凭证（使用OAuth 2.0）"""
    creds = None
    token_file = 'token.pickle'
    
    # 如果存在token文件，则加载已保存的凭证
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            try:
                creds = pickle.load(token)
            except:
                print("加载保存的凭证失败，将重新授权")
    
    # 如果没有有效凭证，则请求用户授权
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                print("刷新凭证失败，将重新授权")
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"授权过程出错: {e}")
                return None
            
            # 保存凭证以供下次使用
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
    
    try:
        # 创建Google Sheets API服务
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"创建API服务失败: {e}")
        return None

def get_sheet_data(service, spreadsheet_id, sheet_name=None):
    """获取Google表格数据"""
    try:
        # 获取表格信息
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        # 如果未指定工作表名称，使用第一个工作表
        if not sheet_name:
            sheet_name = spreadsheet['sheets'][0]['properties']['title']
        
        # 获取工作表范围
        range_name = f"{sheet_name}"
        
        # 获取数据
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('未找到数据')
            return None
        
        # 将数据转换为字典列表
        headers = values[0]
        data = []
        for row in values[1:]:
            # 确保行长度与标题行一致
            row_data = row + [''] * (len(headers) - len(row))
            data.append(dict(zip(headers, row_data)))
        
        return data
    except Exception as e:
        print(f"获取表格数据错误: {e}")
        return None

def export_to_json(data, output_file, format_type="list", key_field=None):
    """将数据导出为JSON文件"""
    if not data:
        print("没有数据可导出")
        return False
    
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    # 根据格式类型处理数据
    if format_type == "list":
        # 列表对象格式 - 默认
        json_data = data
    elif format_type == "nested":
        # 嵌套对象格式
        if not key_field or key_field not in data[0].keys():
            print(f"错误: 字段 '{key_field}' 不存在或未指定")
            return False
        
        json_data = {}
        for item in data:
            key = item.pop(key_field)
            json_data[key] = item
    else:
        print(f"不支持的格式类型: {format_type}")
        return False
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从Google Sheets导出数据到JSON文件')
    parser.add_argument('--sheet_id', required=True, help='Google表格ID')
    parser.add_argument('--output', required=True, help='输出JSON文件路径')
    parser.add_argument('--credentials', required=True, help='Google API OAuth 2.0凭证JSON文件路径')
    parser.add_argument('--format', choices=['list', 'nested'], default='list', help='JSON格式类型: list或nested')
    parser.add_argument('--key_field', help='嵌套格式的主键字段名')
    parser.add_argument('--sheet_name', help='工作表名称(默认为第一个工作表)')
    
    args = parser.parse_args()
    
    # 检查参数
    if args.format == 'nested' and not args.key_field:
        print("错误: 嵌套格式需要指定--key_field参数")
        return 1
    
    # 设置凭证
    service = setup_credentials(args.credentials)
    if not service:
        return 1
    
    # 获取表格数据
    data = get_sheet_data(service, args.sheet_id, args.sheet_name)
    if not data:
        return 1
    
    # 导出数据
    success = export_to_json(data, args.output, args.format, args.key_field)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 