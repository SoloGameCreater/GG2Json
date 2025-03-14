@echo off
echo 开始从Google表格导出数据...
python simple_sheets_to_json.py
if %errorlevel% equ 0 (
    echo 导出成功完成！
) else (
    echo 导出过程中出现错误，请检查上面的错误信息。
)
pause 