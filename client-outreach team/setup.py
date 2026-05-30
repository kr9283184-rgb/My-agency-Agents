from setuptools import setup, find_packages

setup(
    name="client-outreach",
    version="0.1.0",
    description="AI Sales & Outreach Department — Multi-agent outbound sales system",
    author="Sales Outreach Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "playwright>=1.40.0",
        "reportlab>=4.0.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.23.0"],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "client-outreach=client_outreach.cli:main",
        ],
    },
)
