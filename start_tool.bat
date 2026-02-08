@echo off
setlocal
cd /d "%~dp0"
echo 🚀 正在启动 Windows 文本脱敏工具...

:: 检查是否存在虚拟环境
if not exist ".venv" (
    echo ⚠️ 未检测到虚拟环境，正在为您自动创建...
    
    :: 1. 创建虚拟环境
    echo [1/3] 创建 Python 虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败！请检查是否安装了 Python。
        pause
        exit /b
    )

    :: 2. 激活并安装依赖
    echo [2/3] 安装项目依赖...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo ❌ 依赖安装失败！
        pause
        exit /b
    )

    :: 3. 下载模型
    echo [3/3] 配置 NLP 模型...
    python model_installer.py
    
    echo ✅ 环境配置完成！
) else (
    call .venv\Scripts\activate.bat
)

:: 启动应用
echo 🌟 启动 Streamlit 应用...
streamlit run app.py

pause
