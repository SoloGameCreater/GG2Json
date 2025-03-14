# 简易谷歌表格数据导出工具

这个工具可以帮助您使用OAuth 2.0凭证将Google Sheets中的数据导出为JSON格式文件。

## 功能特点

- 使用OAuth 2.0进行身份验证（适用于个人账户）
- 自动获取表格数据并导出为JSON格式
- 简单易用，无需复杂配置

## 安装依赖

```bash
pip install -r simple_requirements.txt
```

## 使用前准备

1. 确保您已经启用了Google Sheets API
   - 访问 [Google Cloud Console](https://console.cloud.google.com/)
   - 选择您的项目
   - 导航到"API和服务" > "库"
   - 搜索并启用"Google Sheets API"

2. 确保您的OAuth 2.0客户端ID凭证文件已放置在正确位置
   - 默认文件名: `client_secret_942388970445-ck7iefag4jn02bu92nq94t0o2m1a2ffr.apps.googleusercontent.com.json`

3. 修改脚本中的表格ID
   - 打开`simple_sheets_to_json.py`
   - 修改`spreadsheet_id`变量为您的表格ID

## 使用方法

### Windows系统

双击运行`simple_sheets_to_json.bat`或在命令提示符中执行：

```cmd
simple_sheets_to_json.bat
```

### Linux/Mac系统

```bash
# 赋予执行权限
chmod +x simple_sheets_to_json.sh

# 运行脚本
./simple_sheets_to_json.sh
```

## 首次使用

首次运行脚本时，系统会打开浏览器窗口，要求您登录Google账户并授权应用程序访问您的Google表格。授权后，凭证将保存在`token.pickle`文件中，后续运行不再需要重新授权（除非凭证过期）。

## 输出

程序将在`output`目录下生成`sheet_data.json`文件。

## 如何获取表格ID

表格ID是Google表格URL中的一部分。例如，在以下URL中：
```
https://docs.google.com/spreadsheets/d/1tapDg3OMX_7FkkoIxu23ijw6NNh3lrlV2cA-5Oz3IOI/edit
```
表格ID是：`1tapDg3OMX_7FkkoIxu23ijw6NNh3lrlV2cA-5Oz3IOI`

## 注意事项

1. 如果您的表格包含大量数据，加载可能需要一些时间
2. 如果遇到授权问题，可以删除`token.pickle`文件，然后重新运行脚本进行授权
3. 确保您的Google账户有权访问目标表格 