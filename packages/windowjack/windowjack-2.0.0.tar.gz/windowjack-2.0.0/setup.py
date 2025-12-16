from setuptools import setup, find_packages

setup(
    name="windowjack",
    version="2.0.0",
    description="Windows screen and window capture library with occlusion support",
    author="WindowJack",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
