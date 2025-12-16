from setuptools import setup, find_packages

setup(
    name='sfrs-element-loader',           # PyPI package name (dashes are fine here)
    version='0.2.14',
    description='A tool to load and inspect SFRS elements from a database using SQLAlchemy.',
    author='Achim Andres',
    author_email='a.andres@gsi.de',
    packages=find_packages(),            # Automatically includes all packages with __init__.py
    install_requires=[
        'SQLAlchemy',
        'tabulate',
        'python-dotenv'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
