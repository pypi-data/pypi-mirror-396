from distutils.core import setup
import setuptools

DESCRIPTION = 'ICDR is a high performing library for retrieving contrastive text data from a document collection.'
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='icdr',
    version='0.0.21',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Leonidas Akritidis",
    author_email="lakritidis@ihu.gr",
    maintainer="Leonidas Akritidis",
    maintainer_email="lakritidis@ihu.gr",
    packages=setuptools.find_packages(),
    url='https://github.com/lakritidis/icdr',
    install_requires=["pandas"],
    license="Apache",
    keywords=[
        "index", "inverted index", "contrastive data", "pairs", "information retrieval",
        "similarity search", "search", "string search", "approximate retrieval"],
    py_modules=["icdr"],
    package_data={'': ['icdr.so', 'icdr.dylib', 'icdr.dll', 'libgcc_s_seh-1.dll', 'libstdc++-6.dll']},
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache License",
            "Operating System :: OS Independent",
        ],
)
