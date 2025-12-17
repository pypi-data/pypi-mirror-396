# setup.py
from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name='rubmix',
    version='1.0.1',  # حتماً ورژن جدید
    packages=find_packages(),

    description='Advanced Rubika Keypad Builder for rubpy using rubka logic.',
    long_description=long_desc,
    long_description_content_type='text/markdown',

    author='Erfan',
    python_requires='>=3.8',

    install_requires=[
        'rubpy',
        'rubka',
    ],

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
