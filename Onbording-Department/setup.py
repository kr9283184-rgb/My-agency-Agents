from setuptools import setup, find_packages

setup(
    name="onboarding-department",
    version="0.1.0",
    description="AI Client Onboarding Department — Multi-agent system for onboarding won deals",
    author="Onboarding Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "playwright>=1.40.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "onboarding=onboarding_department.cli:main",
        ],
    },
)
