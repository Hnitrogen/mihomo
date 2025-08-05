@echo off
echo 正在打包 Linux 部署文件...

REM 检查部署目录是否存在
if not exist deploy_linux (
    echo 部署目录不存在，请先运行 create_deploy_package.bat
    pause
    exit /b 1
)

REM 创建压缩包（如果有 7zip）
if exist "C:\Program Files\7-Zip\7z.exe" (
    echo 使用 7-Zip 创建压缩包...
    "C:\Program Files\7-Zip\7z.exe" a -ttar mihomo-linux-deploy.tar deploy_linux\*
    "C:\Program Files\7-Zip\7z.exe" a -tgzip mihomo-linux-deploy.tar.gz mihomo-linux-deploy.tar
    del mihomo-linux-deploy.tar
    echo 已创建: mihomo-linux-deploy.tar.gz
) else if exist "C:\Program Files (x86)\7-Zip\7z.exe" (
    echo 使用 7-Zip 创建压缩包...
    "C:\Program Files (x86)\7-Zip\7z.exe" a -ttar mihomo-linux-deploy.tar deploy_linux\*
    "C:\Program Files (x86)\7-Zip\7z.exe" a -tgzip mihomo-linux-deploy.tar.gz mihomo-linux-deploy.tar
    del mihomo-linux-deploy.tar
    echo 已创建: mihomo-linux-deploy.tar.gz
) else (
    echo 未找到 7-Zip，请手动压缩 deploy_linux 目录
    echo 或者使用以下 PowerShell 命令:
    echo Compress-Archive -Path deploy_linux -DestinationPath mihomo-linux-deploy.zip
)

echo.
echo 部署包准备完成！
echo.
echo 上传到 Linux 服务器的步骤:
echo 1. 将 deploy_linux 目录或压缩包上传到服务器
echo 2. 如果是压缩包，解压: tar -xzf mihomo-linux-deploy.tar.gz
echo 3. 进入目录: cd deploy_linux
echo 4. 给脚本执行权限: chmod +x *.sh scripts/*.sh
echo 5. 安装: sudo ./install.sh
echo 6. 启动: sudo systemctl start mihomo
echo.
pause