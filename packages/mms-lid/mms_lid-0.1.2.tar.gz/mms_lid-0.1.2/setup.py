# setup.py
from setuptools import setup, find_packages

# README.md 내용을 읽어서 상세 설명으로 사용
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mms-lid",                  # pip install 할 때 사용할 이름
    version="0.1.2",                  # 버전
    author="N01N9",               # 작성자 이름
    author_email=None,
    description="A Robust Language Identification Tool using MMS-1B",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://huggingface.co/N01N9/mms-1b-ll-lid-timestamp", # 깃허브 주소 등
    packages=find_packages(),         # omni_lid 폴더를 자동으로 찾음
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    
    # [중요] 의존성 라이브러리 자동 설치
    install_requires=[
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "transformers>=4.30.0",
        "numpy",
        "scipy",
        "tqdm",
        "requests",
    ],

    # [중요] 터미널 명령어 등록
    # 설치 후 터미널에서 'omnilid'라고 치면 omni_lid.cli 모듈의 main 함수가 실행됨
    entry_points={
        "console_scripts": [
            "mms_lid=mms_lid.cli:main",
        ],
    },
)