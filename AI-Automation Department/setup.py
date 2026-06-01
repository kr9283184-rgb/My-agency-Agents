from setuptools import setup, find_packages


setup(
    name="ai-automation-department",
    version="0.1.0",
    description="AI Automation Department - multi-agent system for designing and delivering business automations",
    author="AI Automation Team",
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
            "ai-automate=ai_automation.cli:main",
        ],
    },
)
