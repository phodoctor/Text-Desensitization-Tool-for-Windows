import logging
from typing import Tuple, Dict, List, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

logger = logging.getLogger("desensitization_tool")

# Add local models directory to path
import os
import sys
# Check if running in a PyInstaller bundle
if getattr(sys, "frozen", False):
    # PyInstaller extracts data to a temporary folder
    current_dir = sys._MEIPASS
    # We will configure the spec to put 'models' at the root of MEIPASS
    models_dir = os.path.join(current_dir, "models")
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, "models")

if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

def create_analyzer_engine() -> AnalyzerEngine:
    """
    Initialize Presidio AnalyzerEngine with English and Chinese support.
    Assumes 'en_core_web_lg' and 'zh_core_web_sm' are installed.
    If 'zh_core_web_sm' is not found, falls back to just English.
    """
    try:
        # Try to configure both English and Chinese
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "en", "model_name": "en_core_web_lg"},
                {
                    "lang_code": "zh", 
                    "model_name": "zh_core_web_trf",
                    "context_nlp": "zh_core_web_trf", # 显式指定上下文模型
                },
            ],
            "ner_model_configuration": {
                "labels_to_ignore": [
                    "CARDINAL", "ORDINAL", "QUANTITY", "WORK_OF_ART", "FAC", "EVENT", "LAW", "PRODUCT", "LANGUAGE"
                ],
            },
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en", "zh"])
    except OSError as e:
        logger.warning(f"Could not load Chinese model, falling back to English default. Error: {e}")
        # Fallback to default (usually just English 'en_core_web_lg')
        analyzer = AnalyzerEngine()

    # --- Add Custom Recognizers ---
    from presidio_analyzer import PatternRecognizer, Pattern

    # 1. Chinese ID Card (Standard 18 digit or 17 digit + X)
    # Also covering the user's case where it might already be partially masked or just raw digits
    # Regex: 15 or 18 digits. 18-digit ends with check digit (0-9 or X).
    # User sample: 11010819750320XXXX (already masked)
    # We want to catch this too.
    # 标准18位身份证号: 6位地区码 + 8位生日 + 3位顺序码 + 1位校验码
    id_card_pattern = Pattern(name="chinese_id_pattern", regex=r"\b\d{6}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])\d{3}[\dXx]\b", score=0.95)
    # Fallback: 匹配部分脱敏的身份证号 (如 11010819750320XXXX)
    masked_id_pattern = Pattern(name="masked_id_pattern", regex=r"\b\d{14,17}[Xx]+\b", score=0.95)
    
    id_recognizer = PatternRecognizer(
        supported_entity="CHINA_ID_CARD",
        patterns=[id_card_pattern, masked_id_pattern],
        supported_language="zh"
    )
    analyzer.registry.add_recognizer(id_recognizer)

    # 2. Bank Account Number
    # 银行卡号: 常见以 62(银联)、4(VISA)、5(MasterCard) 开头，16-19位
    # 支持连续数字或空格/短横线分隔格式
    bank_account_pattern = Pattern(name="bank_account_pattern", regex=r"\b(?:62|4\d|5[0-5])\d{2}[ -]?(?:\d{4}[ -]?){2,3}\d{1,4}\b", score=0.95)
    bank_recognizer = PatternRecognizer(
        supported_entity="BANK_ACCOUNT",
        patterns=[bank_account_pattern],
        supported_language="zh"
    )
    analyzer.registry.add_recognizer(bank_recognizer)

    # 3. Patent Number
    # User sample: CN202310567890.X
    patent_pattern = Pattern(name="patent_pattern", regex=r"(?i)\bCN\d+\.[0-9X]+\b", score=0.95)
    patent_recognizer = PatternRecognizer(
        supported_entity="PATENT_NUMBER",
        patterns=[patent_pattern],
        supported_language="zh"
    )
    analyzer.registry.add_recognizer(patent_recognizer)

    # 4. Chinese Address (Rule-based)
    # User sample: 北京市海淀区中关村东路XX号 世纪科贸大厦 B座 1502室
    # Heuristic: Find pattern ending in "Road XX Number" followed optionally by "Building/Room"
    # Note: "北京市海淀区" might be caught by standard NLP Location, but the detailed part needs a regex.
    # Pattern: (Optional Admin Div)(Road/Street)(Number)(Optional Building/Room info)
    # Using a broad match for the suffix to capture "B座 1502室" etc.
    address_pattern = Pattern(
        name="chinese_address_pattern", 
        regex=r"(?:[^:：\s*]+(?:省|市|区|县|街道))?[\u4e00-\u9fa5]+(?:路|街|巷|道)\S*号(?:\s*[\u4e00-\u9fa5A-Za-z0-9]+(?:大厦|广场|中心|座|室|楼|单元))*", 
        score=0.95
    )
    address_recognizer = PatternRecognizer(
        supported_entity="ADDRESS_DETAILED",
        patterns=[address_pattern],
        supported_language="zh"
    )
    analyzer.registry.add_recognizer(address_recognizer)

    # 5. 中国大陆手机号 (11位，1[3-9]开头)
    phone_pattern = Pattern(name="chinese_phone_pattern", regex=r"\b1[3-9]\d{9}\b", score=0.95)
    phone_recognizer = PatternRecognizer(
        supported_entity="PHONE_NUMBER_CN",
        patterns=[phone_pattern],
        supported_language="zh"
    )
    analyzer.registry.add_recognizer(phone_recognizer)

    # 6. 电子邮箱地址
    email_pattern = Pattern(name="email_pattern", regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", score=0.95)
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        patterns=[email_pattern],
        supported_language="zh"
    )
    analyzer.registry.add_recognizer(email_recognizer)
    
    return analyzer


def desensitize_text(
    text: str, 
    analyzer: Optional[AnalyzerEngine] = None
) -> Tuple[str, Dict[str, str]]:
    """
    Desensitize text by replacing sensitive entities with placeholders.
    Returns the desensitized text and a mapping dictionary for restoration.
    """
    if not analyzer:
        analyzer = create_analyzer_engine()

    # Analyze the text (allowing both English and Chinese if configured)
    results = analyzer.analyze(text=text, language="zh" if _is_chinese(text) else "en")

    # Conflict Resolution: Handle overlapping entities
    # Strategy: Prefer higher score, then longer length.
    # 1. Sort by score (desc), then length (desc)
    results.sort(key=lambda x: (x.score, x.end - x.start), reverse=True)

    # 2. Filter overlaps
    final_results = []
    # Keep track of occupied indices
    # Since we don't have many entities usually, a simple check against selected list is fine
    for result in results:
        is_overlap = False
        for kept in final_results:
            # Check overlap: max(start1, start2) < min(end1, end2)
            if max(result.start, kept.start) < min(result.end, kept.end):
                is_overlap = True
                break
        if not is_overlap:
            final_results.append(result)

    # 3. Sort by start index in descending order for safe string replacement
    final_results.sort(key=lambda x: x.start, reverse=True)

    mapping = {}
    desensitized_text = text
    
    # Counter for unique placeholder generation
    entity_counters = {}

    for result in final_results:
        entity_type = result.entity_type
        start = result.start
        end = result.end
        original_value = text[start:end]

        # Skip if somehow the indices are invalid
        if start < 0 or end > len(text):
            continue

        # Generate unique placeholder
        if entity_type not in entity_counters:
            entity_counters[entity_type] = 0
        entity_counters[entity_type] += 1
        
        placeholder = f"<{entity_type}_{entity_counters[entity_type]}>"
        
        # Store mapping
        mapping[placeholder] = original_value
        
        # Replace in text (using string slicing)
        desensitized_text = desensitized_text[:start] + placeholder + desensitized_text[end:]

    return desensitized_text, mapping

def restore_text(desensitized_text: str, mapping: Dict[str, str]) -> str:
    """
    Restore the original text from desensitized text using the mapping dictionary.
    """
    original_text = desensitized_text
    # We iterate over the mapping. 
    # Note: If placeholders are nested (unlikely given the construction), order might matter.
    # Since our placeholders <TYPE_ID> are distinct, simple replacement works.
    for placeholder, original_value in mapping.items():
        original_text = original_text.replace(placeholder, original_value)
    
    return original_text

def _is_chinese(text: str) -> bool:
    """
    Simple heuristic to check if text contains Chinese characters.
    """
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False
