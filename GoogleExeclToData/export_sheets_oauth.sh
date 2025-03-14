#!/bin/sh

# 配置项目目录
projectDir="GoogleExeclToData"

# 配置凭证文件路径 - OAuth 2.0客户端ID凭证
credentialsFile="client_secret_942388970445-ck7iefag4jn02bu92nq94t0o2m1a2ffr.apps.googleusercontent.com.json"

# 配置表格信息数组 (表格名称,表格ID,输出文件名,格式类型)
sheetsAll=(
    {"merge","1tapDg3OMX_7FkkoIxu23ijw6NNh3lrlV2cA-5Oz3IOI","users.json","list"}
)

######################################
# 以下为脚本逻辑，一般不需要修改
######################################
num=${#sheetsAll[*]}
argCount=4  # 每个表格的参数数量（名称、ID、输出文件名、格式类型）

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
}

idxBegin=-1
idxEnd=-1

# 处理命令行参数
if [ "$#" == "1" ] ; then
    num=`isNum $1`
    if [ $num == "true" ]; then
        if [ $1 == 0 ]; then
            idxBegin=0
            idxEnd=$sheetCount
        else
            if [ $1 -gt $sheetCount ] || [ $1 -lt 1 ]; then
                listAll $1
                exit 1
            fi
            idxBegin=$((1 - 1))
            idxEnd=$1
        fi
    else
        for ((i = 0; i < $sheetCount; i++)); do
            idx=$((i*${argCount}))
            name=${sheetsAll[$idx]}
            nameLower=$(echo $name | tr '[A-Z]' '[a-z]')
            argLower=$(echo $1 | tr '[A-Z]' '[a-z]')
            if [ "$argLower" == "$nameLower" ]; then
                idxBegin=$i
                idxEnd=$((i + 1))
                break
            fi
        done
    fi
fi

if [ "$idxBegin" -lt "0" ] ; then
    listAll $1
    exit 1
fi

echo "开始导出表格，范围: $((idxBegin+1)) 到 $idxEnd"

# 创建输出目录
mkdir -p output

# 循环处理每个表格
for ((i = idxBegin; i < idxEnd; i++)); do
    idx=$((i*${argCount}))
    name=${sheetsAll[$idx]}
    sheet_id=${sheetsAll[$idx+1]}
    output_file=${sheetsAll[$idx+2]}
    format_type=${sheetsAll[$idx+3]}
    key_field=${sheetsAll[$idx+4]:-""}  # 可选参数，嵌套格式的主键字段
    
    echo "正在处理: $name (ID: $sheet_id)"
    
    # 构建Python命令的参数
    cmd_args="--sheet_id \"$sheet_id\" --output \"output/$output_file\" --format \"$format_type\" --credentials \"$credentialsFile\""
    
    # 如果有主键字段，添加到参数中
    if [ ! -z "$key_field" ]; then
        cmd_args="$cmd_args --key_field \"$key_field\""
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