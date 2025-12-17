from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alm-core",
    version="0.1.0",
    author="Jalendar Reddy Maligireddy",
    author_email="jalendarreddy97@gmail.com",
    description="Agent Language Model (ALM): A deterministic, policy-driven architecture for robust AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jalendar10/alm-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "networkx>=3.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "full": [
            "playwright>=1.40.0",
            "matplotlib>=3.5.0",
            "pyperclip>=1.8.0",
            "pyautogui>=0.9.50",
            "psutil>=5.9.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "alm=alm_core.cli:main",
        ],
    },
    keywords="ai agent llm automation policy privacy security",
    project_urls={
        "Bug Reports": "https://github.com/Jalendar10/alm-core/issues",
        "Source": "https://github.com/Jalendar10/alm-core",
        "Documentation": "https://github.com/Jalendar10/alm-core",
    },
)
