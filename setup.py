

from setuptools import setup, find_packages
import io

version = '0.2.1'
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
    license='Apache-2.0 License',
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
        ],
    packages=find_packages(),

)