@echo off
chcp 65001 >nul
echo ========================================
echo    用户凭据验证工具
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

REM 检查user.csv文件
if not exist "user.csv" (
    echo ❌ 找不到user.csv文件
    echo 请确保user.csv文件在当前目录中
    pause
    exit /b 1
)

echo 📋 找到user.csv文件，开始验证用户凭据...
echo.
echo 验证设置:
echo   代理地址: 192.168.132.58:7891
echo   测试URL: https://www.google.com
echo   并发数: 10
echo.
echo 🚀 开始验证...
echo.

python validate_users.py

echo.
echo ========================================
echo 验证完成！
echo ========================================
echo.

if exist "valid_users_config.py" (
    echo ✅ 有效用户配置已生成: valid_users_config.py
    echo.
    echo 现在可以运行压力测试:
    echo   run_test.bat
    echo.
) else (
    echo ❌ 没有生成有效用户配置
    echo 请检查代理连接和用户凭据
    echo.
)

echo 按任意键退出...
pause >nul