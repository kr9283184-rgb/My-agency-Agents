from setuptools import setup, find_packages

setup(
    name="project-management-department",
    version="0.1.0",
    description="AI Project Management Department — Multi-agent system for managing projects from kickoff to delivery",
    author="Project Management Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "project-manage=project_management.cli:main",
        ],
    },
)
