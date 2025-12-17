from setuptools import setup, find_packages

setup(
    name="nidataset",
    version="0.3.2",
    description="NIfTI dataset management package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Giulio Russo, Ciro Russo",
    author_email="russogiulio1998@icloud.com, ciro.russo2910@gmail.com",
    url="https://github.com/GiulioRusso/Ni-Dataset",
    packages=find_packages(),
    license="MIT License",
    install_requires=[
        "nibabel>=5.3.3",
        "numpy>=2.3.5",
        "opencv_python>=4.9.0.80",
        "pandas>=2.3.3",
        "Pillow>=12.0.0",
        "scipy>=1.16.3",
        "simpleitk>=2.5.3",
        "skimage>=0.0",
        "tqdm>=4.67.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.0",
)