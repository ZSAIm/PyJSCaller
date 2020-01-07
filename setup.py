

from setuptools import setup, find_packages
import io

version = '0.2.0'
author = 'ZSAIm'
author_email = 'zzsaim@163.com'

with io.open('README.rst', 'r', encoding='utf-8') as freadme:
    long_description = freadme.read()

setup(
    name='PyJSCaller',
    version=version,
    description='Run JavaScript code from Python',
    long_description=long_description,
    author=author,
    author_email=author_email,
    url='https://github.com/ZSAIm/PyJSCaller',
    license='MIT License',
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: JavaScript',
        ],
    packages=find_packages(),

)