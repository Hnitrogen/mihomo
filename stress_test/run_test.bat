@echo off
chcp 65001 >nul
echo ========================================
echo    Clash-Meta 压力测试启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

REM 检查是否安装了依赖
python -c "import locust" >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

echo 请选择测试模式:
echo.
echo 1. 轻量测试 (10用户, 5分钟)
echo 2. 中等测试 (50用户, 10分钟)  
echo 3. 重度测试 (100用户, 15分钟)
echo 4. 极限测试 (200用户, 20分钟)
echo 5. 自定义测试
echo 6. Web界面模式
echo 7. 运行所有场景
echo.
set /p choice="请输入选择 (1-7): "

if "%choice%"=="1" (
    echo 🚀 启动轻量测试...
    python comprehensive_stress_test.py --scenario light
) else if "%choice%"=="2" (
    echo 🚀 启动中等测试...
    python comprehensive_stress_test.py --scenario medium
) else if "%choice%"=="3" (
    echo 🚀 启动重度测试...
    python comprehensive_stress_test.py --scenario heavy
) else if "%choice%"=="4" (
    echo 🚀 启动极限测试...
    python comprehensive_stress_test.py --scenario extreme
) else if "%choice%"=="5" (
    echo 自定义测试参数:
    set /p users="用户数 (默认50): "
    set /p rate="启动速率/秒 (默认5): "
    set /p duration="持续时间 (如: 10m 或 600s, 默认10m): "
    
    if "%users%"=="" set users=50
    if "%rate%"=="" set rate=5
    if "%duration%"=="" set duration=10m
    
    echo 🚀 启动自定义测试 (%users%用户, %rate%/秒, %duration%)...
    python comprehensive_stress_test.py --users %users% --spawn-rate %rate% --duration %duration%
) else if "%choice%"=="6" (
    echo 🌐 启动Web界面模式...
    echo 请在浏览器中访问: http://localhost:8089
    echo 按 Ctrl+C 停止测试
    locust -f locustfile.py --host=http://localhost --web-host=0.0.0.0
) else if "%choice%"=="7" (
    echo 🚀 运行所有测试场景...
    python comprehensive_stress_test.py --all-scenarios
) else (
    echo 无效选择，启动默认轻量测试...
    python comprehensive_stress_test.py --scenario light
)

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 生成的文件:
dir /b *.html *.json *.csv *_charts 2>nul
echo.
echo 按任意键退出...
pause >nul