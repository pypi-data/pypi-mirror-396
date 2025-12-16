@echo off
echo 设置UV国内镜像源环境变量...

REM 设置清华大学PyPI镜像源
set UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set UV_EXTRA_INDEX_URL=https://pypi.org/simple

echo 环境变量设置完成！
echo UV_INDEX_URL: %UV_INDEX_URL%
echo UV_EXTRA_INDEX_URL: %UV_EXTRA_INDEX_URL%

REM 为当前会话激活环境变量
setx UV_INDEX_URL "https://pypi.tuna.tsinghua.edu.cn/simple"
setx UV_EXTRA_INDEX_URL "https://pypi.org/simple"

echo 环境变量已永久保存到系统！

echo.
echo 使用说明：
echo 1. 运行此脚本设置镜像源
echo 2. 使用 uv add [package] 安装依赖包
echo 3. 使用 uv sync 同步依赖
echo.
pause