@echo off
echo Clash 配置文件聚合器
echo ====================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查PyYAML是否安装
python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo 安装PyYAML依赖...
    pip install PyYAML
)

echo.
echo 使用示例聚合当前目录的配置文件...
python example_usage.py

echo.
echo 聚合完成！生成的文件：
echo - aggregated_clash_config.yaml (聚合后的配置文件)
echo - aggregated_clash_config_credentials.txt (用户凭据信息)

echo.
echo 你也可以手动指定文件：
echo python clash_aggregator.py config1.yaml config2.yaml -o output.yaml

pause