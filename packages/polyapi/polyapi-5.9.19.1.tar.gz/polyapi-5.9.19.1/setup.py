from setuptools import find_packages, setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name='polyapi',
    version='5.9.19.1',
    description='Wrapper for Polymatica API',
    long_description=open('README.md', encoding='utf-8').read(),
    url='https://slsoft.ru/products/polymatica/',
    author='Polymatica Rus LLC',
    author_email='polymatica_support@slsoft.ru',
    license='MIT',
    classifiers=classifiers,
    keywords="polymatica",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "setuptools",
        "numpy==1.19.5; python_version<'3.9'",
        "numpy>1.21.1; python_version>='3.9'",
        "pandas>=1.1.5,<=1.2.5; python_version<'3.9'",
        "pandas>2.0.0; python_version>='3.9'",
        "requests>=2.27.1",
        "pydantic==1.9.2",
        "packaging",
    ],
)
