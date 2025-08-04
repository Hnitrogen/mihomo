@echo off
echo 构建修改后的 clash-meta...

REM 构建项目
go build -o mihomo-custom.exe .
if %ERRORLEVEL% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)

echo 构建成功！

echo.
echo 启动 clash-meta 使用新配置...
echo 使用配置文件: proxy_user_config.yaml
echo.

REM 启动 clash-meta
mihomo-custom.exe -f proxy_user_config.yaml

pause