#!/usr/bin/env bash
# TD Claude Bridge — 命令行工具
# source 这个文件后可直接用 td_* 命令
# 使用示例:
#   source td_claude.sh
#   td_network                          # 查看网络结构
#   td_params /geo1                     # 查看 geo1 所有参数
#   td_set /geo1 tx 2.5                 # 设置参数
#   td_exec "op('/geo1').par.tx = 1.0"  # 执行任意 Python

TD_URL="http://localhost:9980"

# 检查 TD 桥是否在线
td_ping() {
    if curl -sf --max-time 2 "${TD_URL}/network" > /dev/null 2>&1; then
        echo "✓ TD bridge online at ${TD_URL}"
    else
        echo "✗ TD bridge offline — 请在 TD 里打开 Web Server DAT (port 9980)"
        return 1
    fi
}

# 读取网络结构
td_network() {
    local root="${1:-/}"
    curl -sf "${TD_URL}/network?root=${root}" | python3 -m json.tool
}

# 简化版网络列表（只显示 path + type）
td_ls() {
    curl -sf "${TD_URL}/network" | \
        python3 -c "
import json, sys
data = json.load(sys.stdin)
for o in data.get('ops', []):
    print(f\"{o['path']:<50} {o['type']}\")
"
}

# 读取某个 OP 的参数
td_params() {
    local op_path="$1"
    if [[ -z "$op_path" ]]; then
        echo "用法: td_params /path/to/op"
        return 1
    fi
    curl -sf "${TD_URL}/params?op=${op_path}" | python3 -m json.tool
}

# 设置参数: td_set /path param value
td_set() {
    local op_path="$1" param="$2" value="$3"
    if [[ -z "$op_path" || -z "$param" || -z "$value" ]]; then
        echo "用法: td_set /path/to/op param_name value"
        return 1
    fi
    curl -sf -X POST "${TD_URL}/params" \
        -H "Content-Type: application/json" \
        -d "{\"op\": \"${op_path}\", \"param\": \"${param}\", \"value\": ${value}}" \
        | python3 -m json.tool
}

# 设置字符串参数（值加引号）
td_sets() {
    local op_path="$1" param="$2" value="$3"
    curl -sf -X POST "${TD_URL}/params" \
        -H "Content-Type: application/json" \
        -d "{\"op\": \"${op_path}\", \"param\": \"${param}\", \"value\": \"${value}\"}" \
        | python3 -m json.tool
}

# 执行任意 TD Python 代码
td_exec() {
    local code="$1"
    local payload
    payload=$(python3 -c "import json,sys; print(json.dumps({'code': sys.argv[1]}))" "$code")
    curl -sf -X POST "${TD_URL}/exec" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        | python3 -m json.tool
}

# 从文件执行 TD Python 脚本
td_execfile() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "文件不存在: $file"
        return 1
    fi
    local code
    code=$(cat "$file")
    local payload
    payload=$(python3 -c "import json,sys; print(json.dumps({'code': sys.argv[1]}))" "$code")
    curl -sf -X POST "${TD_URL}/exec" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        | python3 -m json.tool
}

echo "TD Claude Bridge 已加载 — 运行 td_ping 检查连接"
