# 谷歌表格数据导出工具

这个工具可以帮助您将Google Sheets中的数据导出为JSON格式文件。

> **注意**: 当前版本仅支持OAuth 2.0身份验证方式。服务账号认证方式的脚本已被移除。

## 功能特点

- 使用OAuth 2.0进行身份验证（适用于个人账户）
- 支持通过ID访问Google表格
- 支持选择特定的工作表
- 提供两种JSON导出格式:
  - 列表对象格式 (默认)
  - 嵌套对象格式 (基于指定的主键)
- 自动创建输出目录
- 支持批处理自动化导出多个表格
- **新功能**: 支持将导出的JSON文件按顶级键拆分成多个子文件

## 安装依赖

```bash
pip install -r requirements_oauth.txt
```

## 使用前准备

1. 确保您已经从Google Cloud Console下载了OAuth 2.0客户端ID凭证文件
2. 确保您的Google表格已经对您的Google账户开放了访问权限

## 首次使用

首次运行脚本时，系统会打开浏览器窗口，要求您登录Google账户并授权应用程序访问您的Google表格。授权后，凭证将保存在`token.pickle`文件中，后续运行不再需要重新授权（除非凭证过期）。

## 批处理使用

### Linux/Mac 系统

配置`export_sheets_oauth.sh`文件中的表格信息，然后运行:

```bash
# 赋予执行权限
chmod +x export_sheets_oauth.sh

# 导出所有表格
./export_sheets_oauth.sh 0

# 导出特定编号的表格
./export_sheets_oauth.sh 1

# 按名称导出表格
./export_sheets_oauth.sh "用户数据"
```

### Windows 系统

配置`export_sheets_oauth.bat`文件中的表格信息，然后运行:

```cmd
# 导出所有表格
export_sheets_oauth.bat 0

# 导出特定编号的表格
export_sheets_oauth.bat 1

# 按名称导出表格
export_sheets_oauth.bat "用户数据"
```

## 批处理配置说明

在批处理脚本中，您需要配置以下信息:

1. `credentialsFile`: OAuth 2.0客户端ID凭证JSON文件路径
2. 表格信息数组，包含:
   - 表格名称
   - 表格ID
   - 输出文件名
   - 格式类型 (list 或 nested)
   - 主键字段 (嵌套格式需要)

## 如何获取表格ID

表格ID是Google表格URL中的一部分。例如，在以下URL中：
```
https://docs.google.com/spreadsheets/d/1KM52Dg08TlbETfnsmzm0gj6g__7wvGpXcf-4ZfGObKc/edit#gid=0
```
表格ID是：`1KM52Dg08TlbETfnsmzm0gj6g__7wvGpXcf-4ZfGObKc`

## 输出

程序将在`output`目录下生成JSON文件。

## 示例输出

### 列表对象格式
```json
[
  {
    "姓名": "张三",
    "年龄": 25,
    "城市": "北京"
  },
  {
    "姓名": "李四",
    "年龄": 30,
    "城市": "上海"
  }
]
```

### 嵌套对象格式
```json
{
  "张三": {
    "年龄": 25,
    "城市": "北京"
  },
  "李四": {
    "年龄": 30,
    "城市": "上海"
  }
}
```

## 新增功能：JSON文件拆分

### 功能说明

该功能可以将导出的JSON文件按照顶级键拆分成多个子文件。例如，如果您的JSON文件结构如下：

```json
{
  "MergeableItem": [...],
  "MergeChain": [...]
}
```

拆分后将生成两个文件：
- `MergeableItem.json`
- `MergeChain.json`

这些文件默认将保存在原始JSON文件的父目录的父目录下的`export`文件夹中。您也可以通过`--output-dir`参数指定自定义输出目录。

### 使用方法

#### 1. 在导出时自动拆分（默认行为）

从v1.1版本开始，导出JSON文件后会默认执行拆分操作，无需添加额外参数：

```bash
python google_sheets_to_json_batch_oauth.py --sheet_id YOUR_SHEET_ID --output output/data.json --credentials YOUR_CREDENTIALS_FILE --format sheet_grouped
```

如果您不希望拆分JSON文件，可以添加`--no-split`参数：

```bash
python google_sheets_to_json_batch_oauth.py --sheet_id YOUR_SHEET_ID --output output/data.json --credentials YOUR_CREDENTIALS_FILE --format sheet_grouped --no-split
```

如果您希望将拆分后的JSON文件保存到自定义目录，可以添加`--output-dir`参数：

```bash
python google_sheets_to_json_batch_oauth.py --sheet_id YOUR_SHEET_ID --output output/data.json --credentials YOUR_CREDENTIALS_FILE --format sheet_grouped --output-dir XProject/Assets/ExtraRes/Configs/DataJson
```

#### 2. 单独拆分已有的JSON文件

您也可以使用单独的脚本来拆分已经存在的JSON文件：

```bash
python json_splitter.py --input output/merge.json
```

或者

```bash
python split_json.py output/merge.json
```

如果您希望将拆分后的JSON文件保存到自定义目录，可以添加`--output-dir`参数：

```bash
python json_splitter.py --input output/merge.json --output-dir XProject/Assets/ExtraRes/Configs/DataJson
```

这将读取`output/merge.json`文件，并将其拆分成多个子文件，保存在指定的目录中。

### 在批处理脚本中配置输出目录

您可以通过以下两种方式在批处理脚本中配置输出目录：

1. 在脚本文件中修改`export_dir`变量：

```bash
# 配置拆分后的JSON文件输出目录
export_dir="XProject/Assets/ExtraRes/Configs/DataJson"
```

2. 在命令行中使用`--output-dir`参数：

```bash
./export_sheets_oauth.sh 1 --output-dir XProject/Assets/ExtraRes/Configs/DataJson
```

## 注意事项

1. 如果您的表格包含大量数据，首次加载可能需要一些时间
2. 确保您的OAuth 2.0凭证具有正确的重定向URI（通常是`http://localhost`）
3. 如果遇到授权问题，可以删除`token.pickle`文件，然后重新运行脚本进行授权 