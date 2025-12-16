from setuptools import setup, find_packages

setup(
    name="earthplus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
        "PyOpenGL>=3.1.6",
    ],
    extras_require={
        "accelerate": ["PyOpenGL_accelerate>=3.1.6"]
    },
    python_requires=">=3.11",
    author="Francis Jusu",
    author_email="jusufrancis08@gmail.com",
    description="A simple Python 3D engine for beginners using Pygame and OpenGL",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Francis589-png/earthplus",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

