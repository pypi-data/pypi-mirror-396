from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Useful utilities for data IO operations, including Snowflake, S3, and SageMaker integrations."

setup(
    name='bpx-dataio',
    version='0.1.0',
    description='Useful utilities for data IO operations, including Snowflake, S3, and SageMaker integrations.',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author="Julian Liu",
    author_email='data.intelligence.mastery@gmail.com',
    url='https://github.com/bpx/bpx-dataio',  # Update with your actual repository URL
    package_dir={'': 'packages'},
    packages=find_packages(where='packages'),
    install_requires=[
        'boto3>=1.26.0',
        'snowflake-connector-python[pandas]>=3.0.0',
        'certifi>=2022.0.0',
        'pandas>=1.5.0', 
        'numpy>=1.23.0',
        'sagemaker>=2.0.0',
        'scikit-learn>=1.0.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  # Update with your license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='data-io snowflake s3 sagemaker aws bpx',
)
