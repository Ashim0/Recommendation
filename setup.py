from setuptools import setup, find_packages

setup(
    name='recommendation',
    version='1.0.0',
    author='Ashim',
    author_email='ashim@gmail.com',
    description='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # List your project dependencies here
        # 'examplepackage>=1.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
