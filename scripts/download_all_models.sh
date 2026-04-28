#!/bin/bash
# 下载 hacxy/l2d-models 全部模型
# 使用 gh-proxy 加速

BASE_DIR="/opt/emotion-ai-assiant/frontend/web/public/live2d"
MODELS=(
    "HK416-1-normal"
    "HK416-2-destroy"
    "HK416-2-normal"
    "Haru"
    "Hiyori"
    "Kar98k-normal"
    "Mao"
    "Mark"
    "Natori"
    "Pio"
    "Ren"
    "Rice"
    "Senko_Normals"
    "Wanko"
    "abeikelongbi_3"
    "bilibili-22"
    "bilibili-33"
    "cat-black"
    "cat-white"
    "chino"
    "date"
    "hallo"
    "haruto"
    "hibiki"
    "histoire"
    "kobayaxi"
    "koharu"
    "kp31"
    "live_uu"
    "mai"
    "murakumo"
    "platelet"
    "platelet_2"
    "potion-Maker-Pio"
    "rem"
    "rem_2"
    "shizuku"
    "shizuku_48"
    "shizuku_pajama"
    "terisa"
    "tia"
    "umaru"
    "uni"
    "wed_16"
    "xisitina"
    "z16"
)

GHPROXY="https://gh-proxy.org/https://raw.githubusercontent.com/hacxy/l2d-models/main/models"
GITHUB="https://raw.githubusercontent.com/hacxy/l2d-models/main/models"

TOTAL=${#MODELS[@]}
echo "开始下载 $TOTAL 个模型..."
echo "=========================================="

for i in "${!MODELS[@]}"; do
    model="${MODELS[$i]}"
    idx=$((i + 1))
    echo "[$idx/$TOTAL] 正在下载: $model"

    model_dir="$BASE_DIR/$model"
    mkdir -p "$model_dir"
    cd "$model_dir"

    # 获取模型文件列表
    files_json=$(curl -s "https://api.github.com/repos/hacxy/l2d-models/contents/models/$model?ref=main" 2>/dev/null)

    if [ -z "$files_json" ] || echo "$files_json" | grep -q '"message"'; then
        echo "  ⚠️ 获取文件列表失败，跳过"
        continue
    fi

    # 提取文件和目录
    echo "$files_json" | grep -o '"name": "[^"]*"' | sed 's/"name": "//' | while read -r name; do
        # 获取类型
        type=$(echo "$files_json" | grep -A2 "\"name\": \"$name\"" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')

        if [ "$type" = "file" ]; then
            # 下载文件，尝试gh-proxy，失败则尝试GitHub raw
            echo "  下载: $name"

            # 尝试gh-proxy
            curl -s -L --max-time 60 -o "$name" "$GHPROXY/$model/$name" 2>/dev/null

            # 如果文件为空，尝试GitHub raw
            if [ ! -s "$name" ]; then
                curl -s -L --max-time 60 -o "$name" "$GITHUB/$model/$name" 2>/dev/null
            fi

            # 检查是否下载成功
            if [ -s "$name" ]; then
                echo "    ✓ $name ($(du -h "$name" | cut -f1))"
            else
                echo "    ✗ $name 下载失败"
                rm -f "$name"
            fi
        elif [ "$type" = "dir" ]; then
            # 创建子目录并递归下载
            echo "  目录: $name/"
            mkdir -p "$name"
            cd "$name"

            subdir_json=$(curl -s "https://api.github.com/repos/hacxy/l2d-models/contents/models/$model/$name?ref=main" 2>/dev/null)
            if [ -n "$subdir_json" ]; then
                echo "$subdir_json" | grep -o '"name": "[^"]*"' | sed 's/"name": "//' | while read -r subname; do
                    subtype=$(echo "$subdir_json" | grep -A2 "\"name\": \"$subname\"" | grep '"type"' | sed 's/.*"type": "\([^"]*\)".*/\1/')
                    if [ "$subtype" = "file" ]; then
                        curl -s -L --max-time 60 -o "$subname" "$GHPROXY/$model/$name/$subname" 2>/dev/null
                        if [ ! -s "$subname" ]; then
                            curl -s -L --max-time 60 -o "$subname" "$GITHUB/$model/$name/$subname" 2>/dev/null
                        fi
                        if [ -s "$subname" ]; then
                            echo "    ✓ $name/$subname"
                        fi
                    fi
                done
            fi
            cd "$model_dir"
        fi
    done

    # 统计下载的文件数量
    file_count=$(find "$model_dir" -type f | wc -l)
    dir_count=$(find "$model_dir" -type d | wc -l)
    if [ "$file_count" -gt 0 ]; then
        echo "  ✓ 完成: $file_count 个文件"
    else
        echo "  ✗ 失败"
    fi

    echo ""
done

echo "=========================================="
echo "下载完成！"
echo "模型保存位置: $BASE_DIR"

# 列出所有模型
echo ""
echo "已下载的模型："
ls -1 "$BASE_DIR"