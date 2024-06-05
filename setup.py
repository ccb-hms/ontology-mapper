from setuptools import setup, find_packages
from text2term.config import VERSION

description = 'a tool for mapping free-text descriptions of entities to ontology terms'
long_description = open('README.md').read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='text2term',
    version=VERSION,
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/ccb-hms/ontology-mapper',
    license='MIT',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Center for Computational Biomedicine, Harvard Medical School',
    author_email='rafael_goncalves@hms.harvard.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering'
    ],
    python_requires=">=3.9",
)
