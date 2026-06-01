from setuptools import setup, find_packages


setup(
    name="testing-department",
    version="0.1.0",
    description="Quality Assurance and Testing Department for release readiness validation",
    author="QA Team",
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
            "qa-test=testing_department.cli:main",
        ],
    },
)
