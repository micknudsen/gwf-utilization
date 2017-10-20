from setuptools import setup, find_packages

setup(

    name='gwf-utilization',

    packages=find_packages(),

    entry_points={'gwf.plugins': ['utilization = gwf_utilization.main:utilization']},

    install_requires=['click',
                      'gwf>=1.1'],

    author='Michael Knudsen',
    author_email='michaelk@clin.au.dk',
    license='MIT'

)
