"""
Project setup file
"""
import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='sageintacctrestsdk',
    version='1.3.2',
    author='Ashwin T',
    author_email='ashwin.t@fyle.in',
    description='Python SDK for accessing Sage Intacct REST APIs',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['sage-intacct', 'sage', 'rest-api', 'api', 'python', 'sdk'],
    url='https://github.com/fylein/intacct-rest-sdk-py',
    packages=setuptools.find_packages(),
    install_requires=['requests>=2.31.0'],
    classifiers=[
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
