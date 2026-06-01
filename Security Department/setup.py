from setuptools import setup, find_packages


setup(
    name="security-department",
    version="0.1.0",
    description="Cybersecurity and System Reliability Department for defensive security operations",
    author="Security Team",
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
            "security-department=security_department.cli:main",
        ],
    },
)
