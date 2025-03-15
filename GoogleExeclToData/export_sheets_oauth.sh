#!/bin/sh

# 配置项目目录
projectDir="GoogleExeclToData"

# 配置凭证文件路径 - OAuth 2.0客户端ID凭证
credentialsFile="client_secret_942388970445-ck7iefag4jn02bu92nq94t0o2m1a2ffr.apps.googleusercontent.com.json"

# 配置表格信息数组 (表格名称,表格ID,输出文件名,格式类型)
sheetsAll=(
    {"TripleMerge","1tapDg3OMX_7FkkoIxu23ijw6NNh3lrlV2cA-5Oz3IOI"}
)

# 配置拆分后的JSON文件输出目录
# 默认为空，使用默认路径（输入文件的父目录的父目录下的export文件夹）
# 如果需要自定义输出目录，请取消下面一行的注释并修改路径
export_dir="XProject/Assets/ExtraRes/Configs/DataJson"

export_script_dir="XProject/Assets/GameMain/Scripts/Common/Config"

######################################
# 以下为脚本逻辑，一般不需要修改
######################################
num=${#sheetsAll[*]}
argCount=2  # 每个表格的参数数量（名称、ID）

# 检查参数数量是否正确
if [ "$((num%${argCount}))" != "0" ]; then
    echo "错误！表格配置有误，请检查。"
    exit 1
fi

sheetCount=$((num/${argCount}))
echo "共配置了 ${sheetCount} 个表格"

# 判断输入是否为数字
isNum(){
    if echo $1 | grep -q '[^0-9]'; then
        echo false
    else
        echo true
    fi
}

# 列出所有可用的表格
listAll(){
    echo "==============================================="
    echo "参数错误: $1"
    echo "请使用以下可用的表格编号或名称："
    echo "==============================================="
    echo "0 - 全部导出"
    for ((i = 0; i < $sheetCount; i++)); do
        idx=$((i*${argCount}))
        name=${sheetsAll[$idx]}
        nameLower=$(echo $name | tr '[A-Z]' '[a-z]')
        echo $((i + 1)) "- $nameLower"
    done
    echo "==============================================="
    echo "附加选项："
    echo "--single-sheet - 只导出默认工作表（与表格编号或名称一起使用）"
    echo "--no-split - 不拆分JSON文件（默认会拆分）"
    echo "--output-dir <dir> - 指定拆分后的JSON文件输出目录"
    echo "例如: ./export_sheets_oauth.sh 1 --single-sheet --no-split"
    echo "例如: ./export_sheets_oauth.sh 1 --output-dir XProject/Assets/ExtraRes/Configs/DataJson"
}

idxBegin=-1
idxEnd=-1
export_all_sheets=true  # 默认为true，导出所有工作表
split_json=true  # 默认拆分JSON文件

# 处理命令行参数
for arg in "$@"; do
    if [ "$arg" == "--single-sheet" ]; then
        export_all_sheets=false
    elif [ "$arg" == "--all-sheets" ]; then
        export_all_sheets=true
    elif [ "$arg" == "--split" ]; then
        split_json=true
    elif [ "$arg" == "--no-split" ]; then
        split_json=false
    elif [ "$arg" == "--output-dir" ]; then
        # 下一个参数是输出目录
        shift
        export_dir="$1"
        shift
        continue
    elif [ "$idxBegin" -lt "0" ]; then
        num=`isNum $arg`
        if [ $num == "true" ]; then
            if [ $arg == 0 ]; then
                idxBegin=0
                idxEnd=$sheetCount
            else
                if [ $arg -gt $sheetCount ] || [ $arg -lt 1 ]; then
                    listAll $arg
                    exit 1
                fi
                idxBegin=$(($arg - 1))
                idxEnd=$arg
            fi
        else
            for ((i = 0; i < $sheetCount; i++)); do
                idx=$((i*${argCount}))
                name=${sheetsAll[$idx]}
                nameLower=$(echo $name | tr '[A-Z]' '[a-z]')
                argLower=$(echo $arg | tr '[A-Z]' '[a-z]')
                if [ "$argLower" == "$nameLower" ]; then
                    idxBegin=$i
                    idxEnd=$((i + 1))
                    break
                fi
            done
        fi
    fi
done

if [ "$idxBegin" -lt "0" ] ; then
    listAll $1
    exit 1
fi

echo "开始导出表格，范围: $((idxBegin+1)) 到 $idxEnd"
if [ "$export_all_sheets" == "true" ]; then
    echo "将导出所有工作表数据（默认）"
else
    echo "将只导出默认工作表"
fi

if [ "$split_json" == "true" ]; then
    echo "将拆分导出的JSON文件（默认）"
    if [ ! -z "$export_dir" ]; then
        echo "拆分后的JSON文件将保存到: $export_dir"
    fi
else
    echo "不拆分导出的JSON文件"
fi

# 创建输出目录
mkdir -p output

# 循环处理每个表格
for ((i = idxBegin; i < idxEnd; i++)); do
    idx=$((i*${argCount}))
    name=${sheetsAll[$idx]}
    sheet_id=${sheetsAll[$idx+1]}
    output_file="${name}.json"  # 自动生成输出文件名为"表格名称.json"
    format_type="list"  # 默认格式类型为list
    key_field=${sheetsAll[$idx+2]:-""}  # 可选参数，嵌套格式的主键字段
    
    echo "正在处理: $name (ID: $sheet_id)"
    
    # 如果需要导出所有工作表，则使用sheet_grouped格式
    if [ "$export_all_sheets" == "true" ]; then
        echo "将导出所有工作表数据（默认）"
        # 使用sheet_grouped格式
        format_type="sheet_grouped"
    else
        echo "将只导出默认工作表"
    fi
    
    # 构建Python命令的参数
    cmd_args="--sheet_id \"$sheet_id\" --output \"output/$output_file\" --format \"$format_type\" --credentials \"$credentialsFile\""
    
    # 如果有主键字段，添加到参数中
    if [ ! -z "$key_field" ]; then
        cmd_args="$cmd_args --key_field \"$key_field\""
    fi
    
    # 如果需要拆分JSON文件，添加--split参数
    if [ "$split_json" == "true" ]; then
        cmd_args="$cmd_args --split"
        # 如果指定了输出目录，则添加--output-dir参数
        if [ ! -z "$export_dir" ]; then
            cmd_args="$cmd_args --output-dir \"$export_dir\""
        fi
    else
        cmd_args="$cmd_args --no-split"
    fi
    
    # 执行Python脚本
    eval "python google_sheets_to_json_batch_oauth.py $cmd_args"
    
    if [ $? -eq 0 ]; then
        echo "✓ 成功导出: $name -> output/$output_file"
    else
        echo "✗ 导出失败: $name"
    fi
    
    echo "----------------------------------------"
done

echo "全部导出完成！" 