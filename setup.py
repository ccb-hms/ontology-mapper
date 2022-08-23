from setuptools import setup, find_packages


long_description = open('README.md').read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.4.1'

setup(
    name='text2term',
    version=version,
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/ccb-hms/ontology-mapper',
    license='MIT',
    description='A tool for mapping free-text descriptions of (biomedical) entities to controlled terms in an ontology',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Center for Computational Biomedicine, Harvard Medical School',
    author_email='rafael_goncalves@hms.harvard.edu',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    python_requires=">=3.9",
)
