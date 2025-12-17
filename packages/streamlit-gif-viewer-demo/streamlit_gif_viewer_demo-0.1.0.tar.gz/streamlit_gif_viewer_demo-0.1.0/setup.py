from pathlib import Path
import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setuptools.setup(
    name="streamlit-gif-viewer-demo",  # Make it unique with your username!
    version="0.1.0",
    author="Your Name",  # TODO: Add your name
    author_email="your.email@example.com",  # TODO: Add your email
    description="A Streamlit component for displaying GIFs with beautiful styling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/streamlit-gif-viewer",  # TODO: Add your repo URL
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit >= 1.0.0",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)

