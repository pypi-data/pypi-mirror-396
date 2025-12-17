from setuptools import setup, find_packages
import os

try:
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A personal cryptography library based on Feistel and CBC."


setup(
    name='cripto-learn',
    version='0.1.0',
    author='Nooch98',
    author_email='',
    description='Encryption/decryption library (Feistel-CBC) capable of encrypting files, directories, and databases, created as a test for learning cryptography',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nooch98/cripto',
    
    packages=find_packages(),
    
    install_requires=[], 
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)