@echo off
setlocal enabledelayedexpansion

:: 配置项目目录
set projectDir=GoogleExeclToData

:: 配置凭证文件路径
set credentialsFile=credentials.json

:: 创建输出目录
if not exist output mkdir output

:: 定义表格信息
:: 格式: 表格名称 表格ID 输出文件名 格式类型 [主键字段]
set sheets[0].name=用户数据
set sheets[0].id=1KM52Dg08TlbETfnsmzm0gj6g__7wvGpXcf-4ZfGObKc
set sheets[0].output=users.json
set sheets[0].format=list

set sheets[1].name=商品信息
set sheets[1].id=1abc123def456ghi789jkl
set sheets[1].output=products.json
set sheets[1].format=list

set sheets[2].name=配置参数
set sheets[2].id=1xyz987uvw654tsr321qpo
set sheets[2].output=config.json
set sheets[2].format=nested
set sheets[2].key=id

:: 设置表格总数
set sheetCount=3

:: 显示帮助信息
if "%~1"=="" goto :showHelp
if "%~1"=="help" goto :showHelp
if "%~1"=="-h" goto :showHelp
if "%~1"=="--help" goto :showHelp

:: 处理命令行参数
set idxBegin=-1
set idxEnd=-1

:: 检查是否为数字
set "num=%~1"
set "isNum=true"
for /f "delims=0123456789" %%i in ("%num%") do set "isNum=false"

if "%isNum%"=="true" (
    if %1 EQU 0 (
        set idxBegin=0
        set idxEnd=%sheetCount%
    ) else (
        if %1 GTR %sheetCount% (
            echo 错误: 表格编号超出范围
            goto :showHelp
        )
        set /a idxBegin=%1-1
        set idxEnd=%1
    )
) else (
    :: 按名称查找
    for /l %%i in (0,1,%sheetCount%) do (
        if /i "!sheets[%%i].name!"=="%~1" (
            set idxBegin=%%i
            set /a idxEnd=%%i+1
            goto :found
        )
    )
    
    echo 错误: 未找到名为"%~1"的表格
    goto :showHelp
)

:found
echo 开始导出表格，范围: !idxBegin! 到 !idxEnd!

:: 循环处理每个表格
for /l %%i in (!idxBegin!,1,!idxEnd!) do (
    if %%i LSS %sheetCount% (
        echo 正在处理: !sheets[%%i].name! (ID: !sheets[%%i].id!)
        
        set cmd=python google_sheets_to_json_batch.py --sheet_id "!sheets[%%i].id!" --output "output/!sheets[%%i].output!" --format "!sheets[%%i].format!" --credentials "%credentialsFile%"
        
        if defined sheets[%%i].key (
            set cmd=!cmd! --key_field "!sheets[%%i].key!"
        )
        
        !cmd!
        
        if !errorlevel! EQU 0 (
            echo ✓ 成功导出: !sheets[%%i].name! -^> output/!sheets[%%i].output!
        ) else (
            echo ✗ 导出失败: !sheets[%%i].name!
        )
        
        echo ----------------------------------------
    )
)

echo 全部导出完成！
goto :eof

:showHelp
echo ===============================================
echo Google表格数据导出工具
echo ===============================================
echo 用法: %~nx0 [选项]
echo 选项:
echo   0         - 导出所有表格
echo   数字      - 按编号导出特定表格
echo   表格名称  - 按名称导出特定表格
echo   help,-h   - 显示此帮助信息
echo.
echo 可用表格:
echo   0 - 全部导出
for /l %%i in (0,1,%sheetCount%) do (
    if %%i LSS %sheetCount% (
        set /a num=%%i+1
        echo   !num! - !sheets[%%i].name!
    )
)
echo ===============================================

endlocal 