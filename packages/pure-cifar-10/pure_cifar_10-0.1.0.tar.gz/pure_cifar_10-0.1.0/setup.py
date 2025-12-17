from setuptools import setup

setup(
    name="pure_cifar_10",
    version="0.1.0",
    description="Pure Python/NumPy CIFAR-10 dataset loader",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ratul Buragohain",
    author_email="ratul75@hotmail.com",
    packages=["pure_cifar_10"],
    install_requires=["numpy>=2.0.0", "tqdm>=4.66.0"],
    python_requires=">=3.10",
    url="https://github.com/ratulb/pure_cifar_10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
