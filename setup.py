from setuptools import setup, find_packages

setup(

    name='gwf-utilization',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    test_suite='tests',

    entry_points={
        'gwf.plugins': ['utilization = gwf_utilization.main:utilization']
    },

    install_requires=[
        'click',
        'gwf>=1.2'
    ],

    tests_require=[
        'pytest'
    ],

    author='Michael Knudsen',
    author_email='michaelk@clin.au.dk',
    license='MIT'

)
