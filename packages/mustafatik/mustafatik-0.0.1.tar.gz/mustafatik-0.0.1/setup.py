from setuptools import setup, find_packages

setup(
    name='mustafatik',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[],
    author='Mustafa',
    author_email='wert1245grad@gmail.com',
    description='A utility library for generating device and user-agent data.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Mustafa',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
