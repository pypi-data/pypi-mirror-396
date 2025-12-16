import os
import argparse
import sys

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("Error: 'huggingface_hub' library is not installed.")
    print("Please install it via 'pip install huggingface_hub'")
    sys.exit(1)

REPO_ID = "stepfun-ai/Step-Audio-2-mini"
SUBFOLDER = "token2wav"

def main():
    parser = argparse.ArgumentParser(description="Download Token2Audio models from HuggingFace")
    parser.add_argument("output_dir", nargs="?", default="token2audio-models", help="Output directory for models (default: token2audio-models)")
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    
    print(f"Downloading models from {REPO_ID}/{SUBFOLDER} to: {output_dir}")
    
    try:
        # 使用 snapshot_download 下载特定文件夹
        # allow_patterns 匹配 token2wav 下的所有文件
        snapshot_download(
            repo_id=REPO_ID,
            local_dir=output_dir,
            allow_patterns=f"{SUBFOLDER}/*",
            local_dir_use_symlinks=False
        )
        
        final_path = os.path.join(output_dir, SUBFOLDER)
        print(f"\nDownload completed successfully!")
        print(f"Model files are located at: {final_path}")
        print(f"You can run the server with:")
        print(f"python -m token2audio.server --model-path {final_path}")
        
    except Exception as e:
        print(f"\nError downloading models: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
