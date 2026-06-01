from setuptools import setup, find_packages


setup(
    name="website-development-department",
    version="0.1.0",
    description="AI Website Development & Design Department",
    author="Website Department",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "website-develop=website_development.cli:main",
        ],
    },
)
