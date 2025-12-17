from setuptools import setup, find_packages

setup(
    name="test_failure_llm",
    version="0.1.2",
    description="A Multimodal LLM from scratch for analyzing test failures.",
    author="Antigravity",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "test_failure_llm": ["training_data.json"] 
    },
    install_requires=[
        "torch",
        "torchvision",
        "pillow",
        "easyocr"
    ],
    entry_points={
        "console_scripts": [
            "analyze-failure=test_failure_llm.analyzer:main",
            "train-llm=test_failure_llm.train:train",
        ],
    },
)
