from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="token2audio",
    version="0.1.0",
    description="Token2Audio Server Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "torch",
        "torchaudio",
        "numpy",
        "s3tokenizer",
        "onnxruntime",
        "librosa",
        "scipy",
        "psutil",
        "hyperpyyaml",
        "flashcosyvoice",
        "huggingface_hub",
    ],
    entry_points={
        "console_scripts": [
            "token2audio-server=token2audio.server:run_app",
            "token2audio-download=token2audio.download:main",
        ],
    },
    python_requires=">=3.8",
)

