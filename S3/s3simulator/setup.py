"""
Setup script for the s3sim package.
"""
from setuptools import setup, find_packages

setup(
    name='s3sim',
    version='0.1.0',
    description='AWS S3 operations with Moto simulator support',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.24.0',
    ],
    extras_require={
        'dev': [
            'moto[server]>=4.0.0',
            'pytest>=7.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            's3sim=s3sim.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
)