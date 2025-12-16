"""Prepare dataset for VLM fine-tuning with Axolotl.

This script helps convert various dataset formats into the format expected
by the Axolotl VLM fine-tuning workflow.

Supported input formats:
- CSV with image paths/URLs and text
- JSON/JSONL with conversation data
- Directory of images with corresponding text files
- HuggingFace datasets

Output format:
- CSV with columns: image_path, prompt, response
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd


def convert_from_csv(
    input_file: str,
    image_col: str = "image",
    prompt_col: str = "prompt",
    response_col: str = "response",
) -> pd.DataFrame:
    """Convert from CSV with custom column names."""
    print(f"Reading CSV from: {input_file}")
    df = pd.read_csv(input_file)

    print(f"Original columns: {df.columns.tolist()}")
    print(f"Total rows: {len(df)}")

    # Rename columns to standard format
    column_mapping = {
        image_col: "image_path",
        prompt_col: "prompt",
        response_col: "response",
    }

    df = df.rename(columns=column_mapping)

    # Validate required columns exist
    required_cols = ["image_path", "prompt", "response"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns after mapping: {missing_cols}. "
            f"Available columns: {df.columns.tolist()}"
        )

    return df[required_cols]


def convert_from_jsonl(input_file: str) -> pd.DataFrame:
    """Convert from JSONL format (e.g., LLaVA format).

    Expected format:
    {"image": "path/to/image.jpg", "conversations": [
        {"from": "human", "value": "question"},
        {"from": "gpt", "value": "answer"}
    ]}
    """
    print(f"Reading JSONL from: {input_file}")
    data = []

    with open(input_file, "r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                item = json.loads(line)

                # Extract image path
                image_path = item.get("image") or item.get("image_path")
                if not image_path:
                    print(f"Warning: Line {line_num} missing image path, skipping")
                    continue

                # Extract conversations
                conversations = item.get("conversations", [])
                if len(conversations) < 2:
                    print(f"Warning: Line {line_num} has incomplete conversation, skipping")
                    continue

                # Find human and gpt messages
                human_msg = next(
                    (c["value"] for c in conversations if c.get("from") == "human"),
                    None,
                )
                gpt_msg = next(
                    (c["value"] for c in conversations if c.get("from") == "gpt"), None
                )

                if human_msg and gpt_msg:
                    # Remove <image> tokens if present
                    human_msg = human_msg.replace("<image>", "").strip()

                    data.append(
                        {
                            "image_path": image_path,
                            "prompt": human_msg,
                            "response": gpt_msg,
                        }
                    )
                else:
                    print(f"Warning: Line {line_num} missing human/gpt messages, skipping")

            except json.JSONDecodeError as e:
                print(f"Warning: Line {line_num} invalid JSON: {e}")
                continue

    print(f"Successfully parsed {len(data)} conversations")
    return pd.DataFrame(data)


def convert_from_directory(
    image_dir: str, text_dir: str, image_ext: str = ".jpg"
) -> pd.DataFrame:
    """Convert from directory structure.

    Expects:
    - image_dir/: contains image files
    - text_dir/: contains text files with same basename
      Each text file should have two lines: prompt and response
    """
    print(f"Reading from directories:")
    print(f"  Images: {image_dir}")
    print(f"  Texts: {text_dir}")

    image_dir = Path(image_dir)
    text_dir = Path(text_dir)

    data = []
    image_files = sorted(image_dir.glob(f"*{image_ext}"))

    print(f"Found {len(image_files)} images")

    for img_path in image_files:
        # Find corresponding text file
        text_path = text_dir / f"{img_path.stem}.txt"

        if not text_path.exists():
            print(f"Warning: No text file for {img_path.name}, skipping")
            continue

        # Read text file (expecting two lines: prompt and response)
        with open(text_path, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        if len(lines) < 2:
            print(f"Warning: {text_path.name} has fewer than 2 lines, skipping")
            continue

        prompt = lines[0]
        response = lines[1]

        data.append(
            {"image_path": str(img_path.absolute()), "prompt": prompt, "response": response}
        )

    print(f"Successfully processed {len(data)} image-text pairs")
    return pd.DataFrame(data)


def convert_from_huggingface(
    dataset_name: str,
    split: str = "train",
    image_col: str = "image",
    prompt_col: str = "prompt",
    response_col: str = "response",
) -> pd.DataFrame:
    """Convert from HuggingFace dataset."""
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Please install datasets: pip install datasets")

    print(f"Loading HuggingFace dataset: {dataset_name} (split: {split})")
    dataset = load_dataset(dataset_name, split=split)

    print(f"Dataset size: {len(dataset)}")
    print(f"Features: {dataset.features}")

    # Convert to pandas
    df = dataset.to_pandas()

    # Handle image column (might be PIL Image or path)
    if image_col in df.columns:
        # If it's a PIL Image, we need to save it
        if hasattr(df[image_col].iloc[0], "save"):
            print("Detected PIL Images, saving to /tmp/vlm_images/...")
            os.makedirs("/tmp/vlm_images", exist_ok=True)

            image_paths = []
            for idx, img in enumerate(df[image_col]):
                img_path = f"/tmp/vlm_images/img_{idx:06d}.jpg"
                img.save(img_path)
                image_paths.append(img_path)

            df["image_path"] = image_paths
        else:
            df = df.rename(columns={image_col: "image_path"})

    # Rename other columns
    column_mapping = {prompt_col: "prompt", response_col: "response"}
    df = df.rename(columns=column_mapping)

    # Validate required columns
    required_cols = ["image_path", "prompt", "response"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {missing_cols}. "
            f"Available columns: {df.columns.tolist()}"
        )

    return df[required_cols]


def validate_dataset(df: pd.DataFrame) -> None:
    """Validate dataset format and content."""
    print("\n" + "=" * 60)
    print("Validating dataset...")
    print("=" * 60)

    # Check required columns
    required_cols = ["image_path", "prompt", "response"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    print(f"✓ All required columns present")

    # Check for null values
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        print(f"Warning: Found null values:\n{null_counts}")
    else:
        print(f"✓ No null values found")

    # Check image paths exist (if they're local paths)
    local_paths = df["image_path"].apply(lambda x: not str(x).startswith("http"))
    if local_paths.any():
        missing_files = []
        for idx, path in df[local_paths]["image_path"].items():
            if not os.path.exists(path):
                missing_files.append(path)

        if missing_files:
            print(f"Warning: {len(missing_files)} image files not found:")
            for path in missing_files[:5]:  # Show first 5
                print(f"  - {path}")
            if len(missing_files) > 5:
                print(f"  ... and {len(missing_files) - 5} more")
        else:
            print(f"✓ All local image paths exist")

    # Statistics
    print(f"\nDataset statistics:")
    print(f"  Total samples: {len(df)}")
    print(f"  Unique images: {df['image_path'].nunique()}")
    print(f"  Avg prompt length: {df['prompt'].str.len().mean():.1f} chars")
    print(f"  Avg response length: {df['response'].str.len().mean():.1f} chars")

    # Show sample
    print(f"\nSample rows:")
    print(df.head(3).to_string())

    print("\n" + "=" * 60)
    print("Validation complete!")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare VLM dataset for Axolotl fine-tuning"
    )

    # Input format selection
    parser.add_argument(
        "--format",
        choices=["csv", "jsonl", "directory", "huggingface"],
        required=True,
        help="Input dataset format",
    )

    # Common arguments
    parser.add_argument("--output", required=True, help="Output CSV file path")

    # CSV-specific arguments
    parser.add_argument(
        "--input-file", help="Input file path (for csv/jsonl formats)"
    )
    parser.add_argument(
        "--image-col", default="image", help="Image column name (default: image)"
    )
    parser.add_argument(
        "--prompt-col", default="prompt", help="Prompt column name (default: prompt)"
    )
    parser.add_argument(
        "--response-col",
        default="response",
        help="Response column name (default: response)",
    )

    # Directory-specific arguments
    parser.add_argument("--image-dir", help="Directory containing images")
    parser.add_argument("--text-dir", help="Directory containing text files")
    parser.add_argument(
        "--image-ext", default=".jpg", help="Image extension (default: .jpg)"
    )

    # HuggingFace-specific arguments
    parser.add_argument("--hf-dataset", help="HuggingFace dataset name")
    parser.add_argument("--hf-split", default="train", help="Dataset split (default: train)")

    # Optional arguments
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't convert (for existing CSV)",
    )

    args = parser.parse_args()

    # Convert based on format
    if args.validate_only:
        print("Validation mode: Loading existing CSV")
        df = pd.read_csv(args.output)
    elif args.format == "csv":
        if not args.input_file:
            parser.error("--input-file required for csv format")
        df = convert_from_csv(
            args.input_file, args.image_col, args.prompt_col, args.response_col
        )
    elif args.format == "jsonl":
        if not args.input_file:
            parser.error("--input-file required for jsonl format")
        df = convert_from_jsonl(args.input_file)
    elif args.format == "directory":
        if not args.image_dir or not args.text_dir:
            parser.error("--image-dir and --text-dir required for directory format")
        df = convert_from_directory(args.image_dir, args.text_dir, args.image_ext)
    elif args.format == "huggingface":
        if not args.hf_dataset:
            parser.error("--hf-dataset required for huggingface format")
        df = convert_from_huggingface(
            args.hf_dataset, args.hf_split, args.image_col, args.prompt_col, args.response_col
        )

    # Validate
    validate_dataset(df)

    # Save
    if not args.validate_only:
        print(f"\nSaving to: {args.output}")
        df.to_csv(args.output, index=False)
        print(f"✓ Successfully saved {len(df)} rows to {args.output}")

        print("\n" + "=" * 60)
        print("Next steps:")
        print("=" * 60)
        print(f"1. Upload dataset to mixtrain:")
        print(f"   mixtrain dataset create my-vlm-data --file {args.output}")
        print(f"\n2. Run the fine-tuning workflow:")
        print(f"   mixtrain workflow run vlm-finetune \\")
        print(f"     --dataset_name my-vlm-data \\")
        print(f"     --output_model_name my-finetuned-model \\")
        print(f"     --base_model llava-hf/llava-1.5-7b-hf")
        print("=" * 60)


if __name__ == "__main__":
    main()


# Example usage:
#
# 1. Convert from CSV with custom columns:
#    python prepare_vlm_dataset.py \
#      --format csv \
#      --input-file data.csv \
#      --image-col img_path \
#      --prompt-col question \
#      --response-col answer \
#      --output vlm_dataset.csv
#
# 2. Convert from JSONL (LLaVA format):
#    python prepare_vlm_dataset.py \
#      --format jsonl \
#      --input-file llava_data.jsonl \
#      --output vlm_dataset.csv
#
# 3. Convert from directory structure:
#    python prepare_vlm_dataset.py \
#      --format directory \
#      --image-dir /path/to/images \
#      --text-dir /path/to/texts \
#      --output vlm_dataset.csv
#
# 4. Convert from HuggingFace dataset:
#    python prepare_vlm_dataset.py \
#      --format huggingface \
#      --hf-dataset liuhaotian/LLaVA-Instruct-150K \
#      --hf-split train \
#      --output vlm_dataset.csv
#
# 5. Validate existing dataset:
#    python prepare_vlm_dataset.py \
#      --format csv \
#      --output vlm_dataset.csv \
#      --validate-only
