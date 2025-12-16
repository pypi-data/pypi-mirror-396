"""Generate embeddings for a mixtrain dataset and append as a new column."""

import subprocess
import sys
import tempfile
from typing import Any

import pandas as pd
from mixtrain import MixClient, MixFlow, mixparam


def install_package(packages):
    """Installs a given Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
        print(f"Successfully installed {packages}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing {packages}: {e}")


mix = MixClient()


class GenerateEmbeddings(MixFlow):
    """Generate embeddings for text data in a dataset and append as a column.

    This workflow reads text data from an input dataset, generates embeddings
    using a specified model, and saves the results with embeddings appended
    as a new column.

    Args:
        input_dataset_name: Name of the input dataset (Apache Iceberg)
        output_dataset_name: Name of the output dataset to create
        text_column: Name of the column containing text to embed
        embedding_column: Name of the column to store embeddings (default: "embedding")
        embedding_model: Model to use for embeddings (default: "openai")
        model_name: Specific model name (e.g., "text-embedding-3-small" for OpenAI)
        batch_size: Number of texts to process at once (default: 100)
        limit: Maximum number of rows to process (-1 for all)
    """

    input_dataset_name: str = mixparam(description="Name of the input dataset")
    output_dataset_name: str = mixparam(description="Name of the output dataset")
    text_column: str = mixparam(
        default="text", description="Column name containing text to embed"
    )
    embedding_column: str = mixparam(
        default="embedding", description="Column name to store embeddings"
    )
    embedding_model: str = mixparam(
        default="openai",
        description="Embedding model provider (openai, sentence-transformers)",
    )
    model_name: str = mixparam(
        default="text-embedding-3-small", description="Specific model name to use"
    )
    batch_size: int = mixparam(
        default=100, description="Batch size for processing"
    )
    limit: int = mixparam(
        default=-1, description="Maximum number of rows to process (-1 for all)"
    )

    def __init__(self):
        super().__init__()
        self.embedding_client = None

    def setup(self, run_config: dict[str, Any]):
        """Initialize the workflow with configuration."""
        print(f"Setting up embedding generation workflow...")
        print(f"Run config: {run_config}")

        for key, value in run_config.items():
            setattr(self, key, value)

        # Install required packages based on embedding model
        if self.embedding_model == "openai":
            install_package(["openai"])
            import openai

            # Get API key from mixtrain secrets
            api_key = mix.get_secret("OPENAI_API_KEY")
            self.embedding_client = openai.OpenAI(api_key=api_key)

        elif self.embedding_model == "sentence-transformers":
            install_package(["sentence-transformers", "torch"])
            from sentence_transformers import SentenceTransformer

            self.embedding_client = SentenceTransformer(self.model_name)

        else:
            raise ValueError(f"Unsupported embedding model: {self.embedding_model}")

        print(f"Using {self.embedding_model} with model: {self.model_name}")

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if self.embedding_model == "openai":
            response = self.embedding_client.embeddings.create(
                input=texts, model=self.model_name
            )
            return [item.embedding for item in response.data]

        elif self.embedding_model == "sentence-transformers":
            embeddings = self.embedding_client.encode(texts, show_progress_bar=False)
            return embeddings.tolist()

        else:
            raise ValueError(f"Unsupported embedding model: {self.embedding_model}")

    def run(self):
        """Execute the embedding generation workflow."""
        print(f"\n{'=' * 60}")
        print(f"Generating embeddings for dataset: {self.input_dataset_name}")
        print(f"Text column: {self.text_column}")
        print(f"Output dataset: {self.output_dataset_name}")
        print(f"Embedding column: {self.embedding_column}")
        print(f"{'=' * 60}\n")

        # Load input dataset
        print(f"Loading dataset: {self.input_dataset_name}")
        input_dataset = mix.get_dataset(self.input_dataset_name)
        df = input_dataset.scan().to_pandas()

        # Apply limit if specified
        if self.limit != -1:
            df = df.head(self.limit)

        print(f"Loaded {len(df)} rows")

        # Validate text column exists
        if self.text_column not in df.columns:
            raise ValueError(
                f"Text column '{self.text_column}' not found in dataset. "
                f"Available columns: {df.columns.tolist()}"
            )

        # Get texts to embed
        texts = df[self.text_column].astype(str).tolist()

        # Generate embeddings in batches
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        print(f"\nGenerating embeddings in {total_batches} batches...")
        for i in range(0, len(texts), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch_texts = texts[i : i + self.batch_size]

            print(
                f"Processing batch {batch_num}/{total_batches} ({len(batch_texts)} texts)..."
            )
            batch_embeddings = self.generate_embeddings_batch(batch_texts)
            all_embeddings.extend(batch_embeddings)

        # Add embeddings to dataframe
        df[self.embedding_column] = all_embeddings

        # Convert embeddings list to string representation for CSV storage
        # (Iceberg can handle array types, but CSV is intermediate format)
        df[f"{self.embedding_column}_str"] = df[self.embedding_column].apply(str)

        print(f"\nGenerated {len(all_embeddings)} embeddings")
        print(f"Embedding dimension: {len(all_embeddings[0])}")

        # Save to output dataset
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            df.to_csv(f.name, index=False)
            print(f"\nCreating output dataset: {self.output_dataset_name}")
            mix.create_dataset_from_file(self.output_dataset_name, f.name)

        print(f"\n{'=' * 60}")
        print(f"✓ Successfully generated embeddings!")
        print(f"✓ Output dataset: {self.output_dataset_name}")
        print(f"✓ Embedding column: {self.embedding_column}")
        print(f"✓ Total rows: {len(df)}")
        print(f"{'=' * 60}\n")

    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up workflow resources...")
        self.embedding_client = None


# Example usage:
# To run this workflow:
# 1. Ensure you have an input dataset with text data
# 2. Set OPENAI_API_KEY secret in mixtrain (for OpenAI embeddings)
# 3. Run the workflow with appropriate parameters
#
# Example:
# workflow = GenerateEmbeddings()
# workflow.setup({
#     "input_dataset_name": "my_text_dataset",
#     "output_dataset_name": "my_text_dataset_with_embeddings",
#     "text_column": "text",
#     "embedding_model": "openai",
#     "model_name": "text-embedding-3-small",
#     "limit": 100
# })
# workflow.run()
# workflow.cleanup()
