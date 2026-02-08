import subprocess
import sys
import os

def install_model(model_name):
    """
    Install a spaCy model using pip.
    """
    print(f"⬇️正在安装模型: {model_name}...")
    try:
        # 使用清华源加速下载
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            model_name,
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        print(f"✅ 模型 {model_name} 安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 模型 {model_name} 安装失败: {e}")
        print("💡 尝试使用官方源重试...")
        try:
             subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                model_name
            ])
             print(f"✅ 模型 {model_name} 安装成功！ (官方源)")
             return True
        except subprocess.CalledProcessError:
             print(f"❌ 最终安装失败。请检查网络连接。")
             return False

def check_and_install_models():
    """
    Check if required models are installed, if not, install them.
    """
    # Define required models and their download links/names
    required_models = [
        "en_core_web_lg", # English Large model
        "zh_core_web_trf" # Chinese Transformer model
    ]
    
    for model in required_models:
        print(f"🔍 检查模型: {model}")
        try:
            import spacy
            if not spacy.util.is_package(model):
                print(f"   模型 {model} 未找到，准备下载...")
                # Download using spacy command
                subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
                print(f"✅ {model} 下载并安装完成")
            else:
                print(f"✅ {model} 已存在，跳过。")
        except ImportError:
             print("❌ spaCy 未安装！请先运行 pip install -r requirements.txt")
             return
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    print("🚀 开始自动配置 NLP 模型环境...")
    check_and_install_models()
    print("\n🎉 所有模型检查完毕！你可以运行 streamlit run app.py 启动工具了。")
