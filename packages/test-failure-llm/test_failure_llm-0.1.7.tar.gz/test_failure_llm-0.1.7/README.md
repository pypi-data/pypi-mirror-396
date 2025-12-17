# Multimodal Test Analysis LLM (From Scratch)

This project implements a **Multimodal Large Language Model** completely from scratch using PyTorch.

## Features
-   **Custom Neural Network**: Uses a CNN for vision and a Transformer for text.
-   **Smart Analysis**: Combines Neural Network predictions with Expert Heuristics for reliable debugging.
-   **CLI Tool**: Easy to integrate into CI/CD pipelines.

## Installation

You can install this package locally:

```bash
pip install .
```

Or for development (editable mode):
```bash
pip install -e .
```

## Usage

### 1. Analyze a Failure
After installation, the `analyze-failure` command is available system-wide:

```bash
analyze-failure --error "NoSuchElement: //div[text()='Workforce']" --source "path/to/source.html" --screenshot "path/to/screenshot.png"
```

### 2. Train the Model
To improve the neural network's accuracy (requires large dataset):

```bash
train-llm
```

## Project Structure
-   `test_failure_llm/`: The source code package.
    -   `model.py`: The Neural Network architecture.
    -   `analyzer.py`: Inference logic and CLI entry point.
    -   `train.py`: Training loop.
-   `setup.py`: Packaging configuration.

## Requirements
-   Python 3.8+
-   PyTorch
-   Torchvision
-   Pillow
