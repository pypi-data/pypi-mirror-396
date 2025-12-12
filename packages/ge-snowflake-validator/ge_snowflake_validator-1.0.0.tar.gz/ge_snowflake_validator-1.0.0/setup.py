from setuptools import setup, find_packages

setup(
    name='ge-snowflake-validator',
    version='1.0.0',
    description='Dynamic data quality validation for Snowflake using Great Expectations',
    author='Priya Pandey',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'great-expectations>=0.18.0',
        'snowflake-connector-python>=3.0.0',
        'snowflake-sqlalchemy>=1.4.0',
        'sqlalchemy>=1.4.0,<2.0.0',
        'pyyaml>=6.0',
        'pandas>=1.5.0',
    ],
    entry_points={
        'console_scripts': [
            'ge-snowflake-profile=ge_snowflake.cli:profile_command',
            'ge-snowflake-validate=ge_snowflake.cli:validate_command',
            'ge-snowflake-init=ge_snowflake.cli:init_command',
        ],
    },
)