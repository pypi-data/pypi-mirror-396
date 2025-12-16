from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='dataform-checklist',
    version='1.3.0',
    author='PTTEP Data Engineering Team',
    author_email='data-engineering@pttep.com',
    description='Generate Excel deployment checklists from Dataform repositories',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pttep/dataform-checklist',
    packages=find_packages(),
    package_data={
        'dataform_checklist': ['template/*.xlsx'],
    },
    include_package_data=True,
    install_requires=[
        'pandas>=2.0.0',
        'openpyxl>=3.1.0',
    ],
    entry_points={
        'console_scripts': [
            'dataform-checklist=dataform_checklist.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    keywords='dataform deployment checklist excel bigquery',
    project_urls={
        'Bug Reports': 'https://github.com/pttep/dataform-checklist/issues',
        'Source': 'https://github.com/pttep/dataform-checklist',
    },
)
