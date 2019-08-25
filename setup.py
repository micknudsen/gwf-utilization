from setuptools import setup, find_packages

setup(

    name='gwf-utilization',
    version='0.1.2',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    test_suite='tests',

    entry_points={
        'gwf.plugins': ['utilization = gwf_utilization.main:utilization']
    },

    python_requires='>=3.6',

    install_requires=[
        'click',
        'gwf>=1.2',
        'texttable>=1.4.0'
    ],

    author='Michael Knudsen',
    author_email='michaelk@clin.au.dk',
    license='MIT'

)
