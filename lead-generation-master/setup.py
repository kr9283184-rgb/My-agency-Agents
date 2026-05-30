from setuptools import setup, find_packages

setup(
    name="lead-gen-master",
    version="0.1.0",
    description="AI Lead Generation Master — Multi-agent lead generation system",
    author="Lead Gen Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "openpyxl>=3.1.0",
        "pandas>=1.5.0",
    ],
    extras_require={
        "llm": ["openai>=1.0.0"],
        "dev": ["pytest>=7.0.0"],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "lead-gen-master=lead_gen_master.cli:main",
        ],
    },
)
