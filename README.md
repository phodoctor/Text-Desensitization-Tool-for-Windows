# 🛡️ Windows 文本脱敏工具 (Text Desensitization Tool for Windows)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)](https://streamlit.io/)

基于 [Microsoft Presidio](https://microsoft.github.io/presidio/) 构建的轻量级中英文文本脱敏与还原工具。支持本地部署，确保数据安全。

---

## ✨ 功能特性

- **🔒 隐私安全**：完全本地运行，无需上传数据至云端。
- **⚡ 智能识别**：集成 spaCy 中文模型，精准识别实体。
- **🎯 多维覆盖**：支持多种敏感信息类型的自动检测。
- **↩️ 数据还原**：特有的脱敏/还原映射机制，支持数据闭环。
- **🖥️ 交互友好**：提供直观的 Web 操作界面。

## 🎥 演示效果

### 🔒 文本脱敏
[🎥 点击观看脱敏演示视频 (MP4)](https://github.com/user-attachments/assets/faa21d6f-f3e8-4ffa-8299-bb96821397bf)

### ↩️ 文本还原
[🎥 点击观看还原演示视频 (MP4)](https://github.com/user-attachments/assets/8f0f9f4d-ae20-4ba4-a3fa-d8a89a3d055e)

## 📋 支持的敏感信息类型

| 类型代码 | 描述 | 检测方式 |
|:---|:---|:---|
| `CHINA_ID_CARD` | 中国居民身份证 (18位) | 正则 + 校验位 |
| `PHONE_NUMBER` | 手机号码 (中国大陆) | 正则表达式 |
| `BANK_ACCOUNT` | 银行卡号 | 正则表达式 |
| `EMAIL_ADDRESS`| 电子邮箱 | 全局通用正则 |
| `PATENT_NUMBER`| 专利申请号 | 中国专利格式 |
| `ADDRESS` | 详细地址 | 模型 + 规则 |
| `PERSON` | 人名 | NLP 模型识别 |
| `ORG` | 组织机构名 | NLP 模型识别 |

## 🚀 快速开始

### 环境依赖
- Windows / Linux / macOS
- Python 3.8+

### 📥 方式一：一键启动 (Windows 推荐)

1. 克隆本项目到本地：
   ```bash
   git clone https://github.com/phodoctor/Text-Desensitization-Tool-for-Windows.git
   ```
2. 进入项目目录，双击运行 **`start_tool.bat`**。
   > 脚本会自动创建虚拟环境、安装依赖并启动应用。

### 🛠️ 方式二：手动安装与运行

如果您习惯使用命令行，请按以下步骤操作：

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **下载 NLP 模型**
   ```bash
   python model_installer.py
   ```
   > 脚本会自动检测并下载 `zh_core_web_trf` (中文) 和 `en_core_web_lg` (英文) 模型。

3. **启动应用**
   ```bash
   streamlit run app.py
   ```

## 📂 项目结构

```
TextDesensitizationTool/
├── app.py              # Streamlit 主程序入口
├── utils.py            # 核心业务逻辑 (脱敏/还原)
├── model_installer.py  # 模型自动化安装脚本
├── run_app.py          # 启动引导脚本
├── requirements.txt    # 项目依赖列表
├── start_tool.bat      # Windows 一键启动脚本
├── LICENSE             # MIT 许可证
└── README.md           # 项目说明文档
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建新的 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。
