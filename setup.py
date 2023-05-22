from setuptools import setup, find_packages

setup(
    name="gwf-utilization",
    version="0.1.7",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="tests",
    entry_points={"gwf.plugins": ["utilization = gwf_utilization.main:utilization"]},
    python_requires=">=3.7",
    install_requires=["click", "texttable>=1.4.0"],
    author="Michael Knudsen",
    author_email="michaelk@clin.au.dk",
    license="MIT",
)
