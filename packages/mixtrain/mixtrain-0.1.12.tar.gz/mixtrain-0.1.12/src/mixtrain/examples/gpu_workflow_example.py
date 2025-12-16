"""Example workflow demonstrating sandbox configuration with GPU and custom image."""

from mixtrain import MixFlow, mixparam


class GPUWorkflow(MixFlow):
    """GPU-accelerated workflow with custom Docker image and resource configuration.

    This workflow demonstrates how to configure the execution sandbox environment
    using special attributes with the _mixflow_ prefix.
    """

    # Sandbox configuration attributes (using _mixflow_ prefix)
    _mixflow_image = "nvcr.io/nvidia/pytorch:22.12-py3"  # NVIDIA PyTorch image
    _mixflow_gpu = "a10g"  # GPU type: a10g, t4, a100, etc.
    _mixflow_memory = 16384  # Memory in MiB (16GB)
    _mixflow_timeout = 1800  # Maximum runtime: 30 minutes

    # Workflow parameters
    model_name: str = mixparam(description="Name of the model to train")

    learning_rate: float = mixparam(
        default=0.001, description="Learning rate for training"
    )

    batch_size: int = mixparam(default=32, description="Training batch size")

    epochs: int = mixparam(default=10, description="Number of training epochs")

    def setup(self):
        """Initialize the workflow."""
        print("Setting up GPU workflow...")
        print(f"Model: {self.model_name}")
        print(f"Learning rate: {self.learning_rate}")
        print(f"Batch size: {self.batch_size}")
        print(f"Epochs: {self.epochs}")

    def run(self):
        """Execute the GPU-accelerated workflow."""
        import torch

        print("\nRunning GPU workflow...")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            print(f"CUDA device count: {torch.cuda.device_count()}")
            print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")

        print(f"\nTraining {self.model_name} for {self.epochs} epochs")
        print(f"Using batch size: {self.batch_size}")
        print(f"Learning rate: {self.learning_rate}")

        # Your actual GPU-accelerated training logic here
        # For example: train model, process data, etc.

        print("\nGPU workflow execution completed!")

    def cleanup(self):
        """Clean up resources after workflow execution."""
        print("Cleaning up GPU workflow resources...")


class CPUWorkflow(MixFlow):
    """CPU-only workflow with custom timeout and memory settings.

    This workflow demonstrates a simpler configuration for CPU-only tasks.
    """

    # Sandbox configuration - using default Debian image with custom resources
    _mixflow_memory = 8192  # 8GB memory
    _mixflow_timeout = 600  # 10 minutes max runtime
    _mixflow_cpu = 4.0  # 4 CPU cores

    # Workflow parameters
    dataset_name: str = mixparam(description="Dataset to process")

    chunk_size: int = mixparam(
        default=1000, description="Size of processing chunks"
    )

    def setup(self):
        """Initialize the CPU workflow."""
        print("Setting up CPU workflow...")
        print(f"Dataset: {self.dataset_name}")
        print(f"Chunk size: {self.chunk_size}")

    def run(self):
        """Execute the CPU workflow."""
        print("\nRunning CPU workflow...")
        print(f"Processing dataset: {self.dataset_name}")
        print(f"Using chunk size: {self.chunk_size}")

        # Your actual processing logic here

        print("\nCPU workflow execution completed!")

    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up CPU workflow resources...")


class MultiNodeGPUWorkflow(MixFlow):
    """Multi-node distributed training workflow.

    Demonstrates configuration for distributed training across multiple nodes.
    Note: num_nodes is stored in config for custom orchestration logic.
    """

    _mixflow_image = "nvcr.io/nvidia/pytorch:22.12-py3"
    _mixflow_gpu = "a100"  # High-performance GPU for distributed training
    _mixflow_memory = 32768  # 32GB per node
    _mixflow_num_nodes = 4  # 4 nodes for distributed training
    _mixflow_timeout = 3600  # 1 hour timeout

    model_name: str = mixparam(description="Model to train")
    distributed_backend: str = mixparam(
        default="nccl", description="Distributed backend (nccl, gloo)"
    )

    def run(self):
        """Execute multi-node distributed training."""
        print(f"\nRunning distributed training on {self._mixflow_num_nodes} nodes")
        print(f"Model: {self.model_name}")
        print(f"Backend: {self.distributed_backend}")

        # Your distributed training logic here
        # The num_nodes config can be used to spawn multiple processes/containers

        print("\nDistributed training completed!")

    def cleanup(self):
        """Clean up distributed resources."""
        print("Cleaning up distributed training resources...")


class CustomImageWorkflow(MixFlow):
    """Workflow with a custom Ubuntu-based image.

    This demonstrates using different base images for different use cases.
    """

    # Use a specific Ubuntu version with custom settings
    _mixflow_image = "ubuntu:22.04"
    _mixflow_memory = 4096  # 4GB
    _mixflow_timeout = 900  # 15 minutes

    task_name: str = mixparam(description="Name of the task to execute")

    def setup(self):
        """Initialize the workflow."""
        print(f"Setting up custom image workflow for task: {self.task_name}")

    def run(self):
        """Execute the workflow."""
        print(f"\nExecuting task: {self.task_name}")
        print("Using Ubuntu 22.04 base image")

        # Your task logic here

        print("\nTask execution completed!")

    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up resources...")
