import streamlit as st
import json
import logging
from io import StringIO
from utils import desensitize_text, restore_text, create_analyzer_engine

# 配置日志
logger = logging.getLogger("desensitization_app")
logging.basicConfig(level=logging.INFO)

# 尝试导入 chardet，如果不可用则使用回退方案
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    logger.warning("chardet 未安装，将仅使用 UTF-8 解码")

# Page Configuration
st.set_page_config(
    page_title="文本脱敏工具",
    page_icon="🛡️",
    layout="wide"
)

# Initialize Analyzer (Cached)
@st.cache_resource
def get_analyzer():
    with st.spinner("正在加载模型，请稍候... (初次运行可能需要几秒钟)"):
        return create_analyzer_engine()

analyzer = get_analyzer()

st.title("🛡️ 文本脱敏与还原工具")
st.markdown("""
本工具可以帮助您自动识别文本中的敏感信息并将其替换为占位符。同时生成一份映射表，用于将来将文本还原。
""")

tab1, tab2 = st.tabs(["🔒 脱敏 (Desensitize)", "🔓 还原 (Restore)"])

# --- Tab 1: Desensitization ---
with tab1:
    st.header("第一步：输入文本")
    input_method = st.radio("选择输入方式:", ("直接输入文本", "上传 TXT 文件"))

    text_to_process = ""
    
    if input_method == "直接输入文本":
        text_to_process = st.text_area("在此粘贴您的文本:", height=200)
    else:
        uploaded_file = st.file_uploader("上传 .txt 文件", type=["txt"])
        if uploaded_file is not None:
            raw_data = uploaded_file.getvalue()
            # 自动检测文件编码
            if HAS_CHARDET:
                detected = chardet.detect(raw_data)
                encoding = detected.get('encoding') or 'utf-8'
                logger.info(f"检测到文件编码: {encoding} (置信度: {detected.get('confidence', 0):.2f})")
            else:
                encoding = 'utf-8'
            
            try:
                text_to_process = raw_data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                # 回退到 UTF-8，替换无法解码的字符
                text_to_process = raw_data.decode('utf-8', errors='replace')
                st.warning("文件编码检测失败，部分字符可能显示异常")
            
            st.info(f"已加载文件: {uploaded_file.name}")

    if st.button("开始脱敏", type="primary"):
        if not text_to_process:
            st.warning("请输入文本或上传文件！")
        else:
            with st.spinner("正在分析和脱敏..."):
                try:
                    desensitized_text, mapping = desensitize_text(text_to_process, analyzer)
                    
                    st.success("脱敏完成！")
                    
                    # Create ZIP file in memory
                    import zipfile
                    from io import BytesIO
                    
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        zf.writestr("desensitized_text.txt", desensitized_text)
                        zf.writestr("mapping.json", json.dumps(mapping, ensure_ascii=False, indent=2))
                    
                    st.download_button(
                        label="📦 一键下载结果 (包含脱敏文本与映射表)",
                        data=zip_buffer.getvalue(),
                        file_name="desensitization_results.zip",
                        mime="application/zip",
                        type="primary"
                    )

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("脱敏后的文本")
                        st.text_area("结果预览", desensitized_text, height=300, label_visibility="collapsed")
                        # Optional: Keep individual download if user wants only text
                        st.download_button(
                            label="仅下载脱敏文本 (.txt)",
                            data=desensitized_text,
                            file_name="desensitized_text.txt",
                            mime="text/plain"
                        )
                        
                    with col2:
                        st.subheader("映射表 (用于还原)")
                        mapping_json = json.dumps(mapping, ensure_ascii=False, indent=2)
                        st.json(mapping, expanded=False)
                        # Optional: Keep individual download
                        st.download_button(
                            label="仅下载映射表 (.json)",
                            data=mapping_json,
                            file_name="mapping.json",
                            mime="application/json"
                        )
                except Exception as e:
                    logger.exception("脱敏过程发生错误")
                    st.error(f"发生错误: {e}")

# --- Tab 2: Restoration ---
with tab2:
    st.header("还原脱敏文本")
    st.markdown("请上传 **脱敏后的文本** 和 **映射表 (.json)** 来还原原始信息。")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("1. 脱敏文本")
        restore_text_input = st.text_area("粘贴文本:", height=150)
        restore_file = st.file_uploader("或上传 .txt 文件", type=["txt"], key="restore_file")
        
    with col_input2:
        st.subheader("2. 映射表")
        mapping_file = st.file_uploader("上传 .json 映射文件", type=["json"], key="mapping_file")

    if st.button("开始还原", type="primary"):
        target_text = ""
        target_map = {}
        
        # Get Text
        if restore_file:
            target_text = StringIO(restore_file.getvalue().decode("utf-8")).read()
        elif restore_text_input:
            target_text = restore_text_input
            
        # Get Map
        if mapping_file:
            try:
                target_map = json.load(mapping_file)
            except Exception as e:
                st.error(f"映射表文件格式错误: {e}")
                st.stop()
        
        if not target_text:
            st.warning("请提供脱敏文本！")
        elif not target_map:
            st.warning("请上传映射表文件！")
        else:
            with st.spinner("正在还原..."):
                try:
                    original_text = restore_text(target_text, target_map)
                    st.success("还原成功！")
                    st.subheader("原始文本")
                    st.text_area("还原结果", original_text, height=300)
                    st.download_button(
                        label="下载还原后的文本 (.txt)",
                        data=original_text,
                        file_name="restored_text.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    logger.exception("还原过程发生错误")
                    st.error(f"还原过程中发生错误: {e}")
