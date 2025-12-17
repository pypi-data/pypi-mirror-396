# setup.py

from setuptools import setup, find_packages

setup(
    name='rubmix', # نامی که با آن نصب می‌شود: pip install rubmix
    version='1.0.0',
    packages=find_packages(),
    description='Advanced Rubika Keypad Builder for rubpy using rubka logic.',
    author='Your Name', # نام خودتان
    install_requires=[
        # وابستگی‌های مورد نیاز
        'rubpy>=1.0.0', # این کتابخانه باید نصب شود
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)