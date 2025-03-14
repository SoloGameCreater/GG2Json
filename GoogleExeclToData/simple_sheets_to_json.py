#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 定义访问Google Sheets所需的权限范围
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def main():
    """从Google表格导出数据到JSON文件的简化脚本"""
    # 配置信息
    creds_file = "client_secret_942388970445-ck7iefag4jn02bu92nq94t0o2m1a2ffr.apps.googleusercontent.com.json"
    spreadsheet_id = "1tapDg3OMX_7FkkoIxu23ijw6NNh3lrlV2cA-5Oz3IOI"
    output_file = "output/sheet_data.json"
    
    # 确保输出目录存在
    Path(output_file).parent.mkdir(exist_ok=True)
    
    # 设置凭证
    creds = None
    token_file = 'token.pickle'
    
    # 如果存在token文件，则加载已保存的凭证
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            try:
                creds = pickle.load(token)
                print("已加载保存的凭证")
            except:
                print("加载保存的凭证失败，将重新授权")
    
    # 如果没有有效凭证，则请求用户授权
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("已刷新凭证")
            except:
                print("刷新凭证失败，将重新授权")
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
                print("已完成新的授权")
                
                # 保存凭证以供下次使用
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                    print("已保存凭证到token.pickle文件")
            except Exception as e:
                print(f"授权过程出错: {e}")
                return 1
    
    try:
        # 创建Google Sheets API服务
        service = build('sheets', 'v4', credentials=creds)
        print("已创建Google Sheets API服务")
        
        # 获取表格信息
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_name = spreadsheet['sheets'][0]['properties']['title']
        print(f"表格名称: {spreadsheet['properties']['title']}")
        print(f"工作表: {sheet_name}")
        
        # 获取数据
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('未找到数据')
            return 1
        
        # 将数据转换为字典列表
        headers = values[0]
        data = []
        for row in values[1:]:
            # 确保行长度与标题行一致
            row_data = row + [''] * (len(headers) - len(row))
            data.append(dict(zip(headers, row_data)))
        
        print(f"已获取 {len(data)} 行数据")
        
        # 写入JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已成功导出到: {output_file}")
        
        # 显示数据预览
        preview = data[:2] if len(data) > 2 else data
        print("\n数据预览:")
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 