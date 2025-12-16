# smart_data_manager_package/setup.py

from setuptools import setup, find_packages

setup(
    name='smart-data-manager',  # Must be unique on PyPI! Choose a descriptive, unique name.
    version='1.0.0',            # Start with a version number
    packages=find_packages(),   # Finds all modules in the package
    # Declare the required third-party libraries this package needs at runtime
    install_requires=[
        'pandas>=2.2',
        'SQLAlchemy>=2.0',
        'pyodbc>=5.1',
        # Do NOT list azure-functions or python-dotenv here, only dependencies of your core logic
    ],
    # Add optional metadata
    author='Sinomtha Mzamo',
    description='ETL logic for Smart Data Manager for Project Y.',
    long_description=open('README.md').read(), # Use README if available
    long_description_content_type='text/markdown',
)