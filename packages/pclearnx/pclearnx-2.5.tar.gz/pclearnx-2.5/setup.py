from setuptools import setup, find_packages

setup(
    name="pclearnx",  
    version="2.5",
    packages=find_packages(),
    description="A package to create folders and copy predefined files",
    author="jerrry",
    author_email="jerry9333067@gmail.com",
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={
        'pclearnx': ['*.py', '*.pdf', '*.js', '*.pkt', '*.json', '*.txt']
    },
    entry_points={
        'console_scripts': [
            'build-folder=pclearnx:build', 
        ],
    },
)
