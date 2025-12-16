from setuptools import setup, find_packages

setup(
    name='ct_veegan',  
    version='0.1.5',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'torch>=2.0.0',
        'numpy>=1.20.0',
        'requests>=2.0.0'   
    ],
    python_requires='>=3.8',
    description='GAN package for sequence vector generation and classification',
    author='Laode Hidayat',
    author_email='your_email@example.com',
    url='https://github.com/username/ct_veegan',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
