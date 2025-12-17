from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="token2audio",
    version="0.1.8",
    description="Token2Audio Server Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "token2audio": ["assets/*.wav", "assets/*.html"],
    },
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
        "huggingface_hub",
        "transformers",
        "diffusers",
    ],
    extras_require={
        "gpu": [
            "triton>=3.0.0",
            "flash-attn",
            "nvidia-ml-py",
        ],
    },
    entry_points={
        "console_scripts": [
            "token2audio-server=token2audio.server:run_app",
            "token2audio-download=token2audio.download:main",
        ],
    },
    python_requires=">=3.8",
)

