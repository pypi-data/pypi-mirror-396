# main.py
import argparse
import json
from .pipeline import LIDPipeline

def main():
    parser = argparse.ArgumentParser(description="mms-lid: 다국어 식별기 실행")
    parser.add_argument("audio_path", type=str, help="분석할 오디오 파일 경로 (.wav)")
    parser.add_argument("--model_path", type=str, default=None, help="모델 파일 경로 (없으면 자동 다운로드)")
    parser.add_argument("--output", type=str, default="result.json", help="결과 저장 경로")
    
    args = parser.parse_args()

    # 1. 파이프라인 초기화 (최초 실행 시 모델 다운로드)
    try:
        pipeline = LIDPipeline(model_path=args.model_path)
    except Exception as e:
        print("프로그램을 종료합니다.")
        return

    # 2. 추론 실행
    print(f"🎧 분석 중: {args.audio_path}")
    try:
        segments = pipeline.predict(args.audio_path)
    except FileNotFoundError:
        print("❌ 오디오 파일을 찾을 수 없습니다.")
        return

    # 3. 결과 출력 및 저장
    print("\n" + "="*60)
    print(f"{'Start':<8} | {'End':<8} | {'Dur':<6} | {'Language'}")
    print("-" * 60)
    
    for seg in segments:
        dur = seg['end'] - seg['start']
        print(f"{seg['start']:<8.2f} | {seg['end']:<8.2f} | {dur:<6.2f} | {seg['label']}")
    print("="*60)

    # JSON 저장
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=4, ensure_ascii=False)
    print(f"💾 결과가 '{args.output}'에 저장되었습니다.")

if __name__ == "__main__":
    main()