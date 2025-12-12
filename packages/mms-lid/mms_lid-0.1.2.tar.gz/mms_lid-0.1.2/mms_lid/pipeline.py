# omni_lid/pipeline.py
import os
import torch
import torchaudio
import requests
from tqdm import tqdm
from .model import OmniLIDModel
from .decoder import ViterbiDecoder
from .config import (
    LANGS, ID2LANG, SILENCE_ID, TARGET_SR, MODEL_DOWNLOAD_URL,
    DEFAULT_TRANSITION_SCALE, DEFAULT_MIN_CONFIDENCE
)

class LIDPipeline:
    def __init__(self, model_path=None, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Device: {self.device}")

        # 1. 모델 경로 설정 (없으면 다운로드)
        if model_path is None:
            model_path = "weights/best_lid_model_ce.pth"
            self._download_if_needed(model_path)
        
        # 2. 모델 초기화
        self.model = OmniLIDModel(len(LANGS))
        self._load_weights(model_path)
        self.model.to(self.device).eval()
        
        if self.device == "cuda":
            self.model.half() # FP16 추론

        # 3. 디코더 초기화
        self.decoder = ViterbiDecoder(
            ID2LANG, SILENCE_ID, 
            transition_scale=DEFAULT_TRANSITION_SCALE, 
            min_confidence=DEFAULT_MIN_CONFIDENCE
        )

    def _download_if_needed(self, path):
        """모델 파일이 없으면 URL에서 다운로드합니다."""
        if os.path.exists(path):
            return
        
        print(f"📥 모델 파일이 없습니다. 다운로드를 시작합니다...\nURL: {MODEL_DOWNLOAD_URL}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        try:
            response = requests.get(MODEL_DOWNLOAD_URL, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc=path) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
            print("✅ 다운로드 완료!")
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
            print(f"⚠️ '{path}' 위치에 모델 파일을 직접 넣어주세요.")
            raise e

    def _load_weights(self, path):
        try:
            checkpoint = torch.load(path, map_location="cpu")
            state_dict = checkpoint["model_state_dict"] if "model_state_dict" in checkpoint else checkpoint
            new_state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
            self.model.load_state_dict(new_state_dict, strict=False)
            print("✅ 모델 가중치 로드 완료")
        except Exception as e:
            print(f"❌ 가중치 로드 실패: {e}")
            raise e

    def predict(self, audio_input):
        """
        audio_input: 파일 경로(str) 또는 Tensor
        returns: 세그먼트 리스트
        """
        # 1. 오디오 로드 및 전처리
        if isinstance(audio_input, str):
            wav, sr = torchaudio.load(audio_input)
            if sr != TARGET_SR:
                wav = torchaudio.transforms.Resample(sr, TARGET_SR)(wav)
        else:
            wav = audio_input

        # 모노 변환 & 정규화
        if wav.ndim > 1: wav = wav.mean(dim=0)
        wav = (wav - wav.mean()) / torch.sqrt(wav.var() + 1e-7)

        # 배치 차원 추가 & Device 이동
        input_values = wav.unsqueeze(0).to(self.device)
        if self.device == "cuda": input_values = input_values.half()

        # 2. 추론
        with torch.no_grad():
            logits = self.model(input_values)

        # 3. 디코딩 (Viterbi)
        best_path, probs = self.decoder.decode(logits.squeeze())
        segments = self.decoder.get_segments(best_path)

        return segments