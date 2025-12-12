# 지원하는 언어 목록 (순서 중요)
LANGS = [
    "ko", "en", "ja", "zh", "fr", "de", "es", "it", "pt", "ru",
    "ar", "hi", "tr", "ms", "da", "fi", "nl", "no", "sv"
]

# ID <-> 언어 매핑
ID2LANG = {i: lang for i, lang in enumerate(LANGS)}
SILENCE_ID = len(LANGS)
ID2LANG[SILENCE_ID] = "<silence>"

# 모델 설정
MODEL_ID = "facebook/mms-1b-fl102"
TARGET_SR = 16000

# Viterbi 하이퍼파라미터 (기본값)
DEFAULT_TRANSITION_SCALE = 20.0
DEFAULT_MIN_CONFIDENCE = 0.0

# [중요] 모델 가중치 다운로드 URL
# 사용자가 직접 호스팅한 .pth 파일의 직접 다운로드 링크(Direct Link)를 넣으세요.
# 예: Hugging Face Hub, Google Drive(direct link), AWS S3 등
MODEL_DOWNLOAD_URL = "https://huggingface.co/N01N9/mms-1b-ll-lid-timestamp/resolve/main/mms_1b_lid_timestamp_step_3000.pth"