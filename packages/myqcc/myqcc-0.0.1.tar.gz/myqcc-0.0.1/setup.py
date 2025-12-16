from setuptools import setup, find_packages

setup(
    name="myqcc",
    version="0.0.1",
    author="QuantumDev",
    author_email="quantum@example.com",
    description="A Qiskit package containing basic quantum circuits and gate implementations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/myqcc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "qiskit",
        "qiskit-aer",
        "numpy",
        "matplotlib"
    ],
    python_requires='>=3.6',
)
