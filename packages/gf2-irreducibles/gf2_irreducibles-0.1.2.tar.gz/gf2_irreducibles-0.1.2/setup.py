from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gf2-irreducibles",
    version="0.1.2",
    author="Gad E. Yaron",
    author_email="gadelaz.yaron@mail.huji.ac.il",
    description="Lookup table for low-weight binary irreducible polynomials (GF(2^n)).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gad1001/gf2-irreducibles",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires='>=3.6',
)