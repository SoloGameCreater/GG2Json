# 谷歌表格数据导出工具

这个工具可以帮助您将Google Sheets中的数据导出为JSON格式文件。

## 功能特点

- 支持通过URL或ID访问Google表格
- 支持选择特定的工作表
- 提供两种JSON导出格式:
  - 列表对象格式 (默认)
  - 嵌套对象格式 (基于指定的主键)
- 自动创建输出目录
- 提供数据预览功能
- 支持批处理自动化导出多个表格

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用前准备

1. 创建Google Cloud项目并启用Google Sheets API
2. 创建服务账号并下载JSON凭证文件
3. 在Google表格中共享权限给服务账号邮箱
4. 将凭证文件保存为`credentials.json`（或在批处理脚本中修改路径）

## 使用方法

### 交互式使用

运行以下命令:

```bash
python google_sheets_to_json.py
```

按照提示输入:
1. Google API凭证JSON文件路径
2. Google表格的URL或ID
3. 工作表名称(可选)
4. JSON导出格式选项
5. 如选择嵌套对象格式，需指定主键字段

### 批处理使用

#### Linux/Mac 系统

配置`export_sheets.sh`文件中的表格信息，然后运行:

```bash
# 赋予执行权限
chmod +x export_sheets.sh

# 导出所有表格
./export_sheets.sh 0

# 导出特定编号的表格
./export_sheets.sh 1

# 按名称导出表格
./export_sheets.sh "用户数据"
```

#### Windows 系统

配置`export_sheets.bat`文件中的表格信息，然后运行:

```cmd
# 导出所有表格
export_sheets.bat 0

# 导出特定编号的表格
export_sheets.bat 1

# 按名称导出表格
export_sheets.bat "用户数据"
```

## 批处理配置说明

在批处理脚本中，您需要配置以下信息:

1. `credentialsFile`: Google API凭证JSON文件路径
2. 表格信息数组，包含:
   - 表格名称
   - 表格ID
   - 输出文件名
   - 格式类型 (list 或 nested)
   - 主键字段 (嵌套格式需要)

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