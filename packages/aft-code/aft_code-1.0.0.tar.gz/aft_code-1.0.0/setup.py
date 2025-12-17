from setuptools import setup,find_packages
setup(
    name='aft-code',
    version='1.0.0',
    packages=find_packages(),
    python_requires='>=3.11',
    description='working with file packages',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    requires=["ujson"]



)