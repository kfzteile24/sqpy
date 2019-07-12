from setuptools import setup, find_packages

def get_long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name='sqpy',
    version='0.1.5',

    description="Limited sqsh-compatible CLI app using ODBC protocol to fetch CSV data.",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    install_requires=[
        'pyodbc'
    ],

    dependency_links=[
    ],

    #extras_require={
    #    'test': ['pytest', 'pytest_click'],
    #},

    packages=find_packages(),

    author='kfzteile24 GmbH',
    license='MIT',

    entry_points={
        'console_scripts': [
            'sqpy = sqpy.cli:main',
        ],
    },

)
