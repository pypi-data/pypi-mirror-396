#!/bin/bash

# cleanup.sh - 清理环境并确保端口可用

PORT=54321

echo "🔍 检查端口 $PORT 是否已被占用..."

PID=$(lsof -ti tcp:$PORT)

if [ -n "$PID" ]; then
    echo "🚨 端口 $PORT 正在被进程 $PID 占用，将尝试关闭该进程..."
    kill -9 $PID
    echo "✅ 进程已被关闭。"
else
    echo "✅ 端口 $PORT 空闲，无需操作。"
fi

echo "🧹 清理临时或缓存文件（如有）"
# 示例：rm -f *.tmp 或者其他特定文件，如：
# rm -f /home/ec2-user/SHAMP/tempfile*

echo "✨ 环境已清理完毕，可以运行Python程序。"
sleep 2