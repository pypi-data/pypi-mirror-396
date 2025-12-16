from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 
setup(
    name = 'pymof',
    version = "0.7.0",
    description = "Mass ratio variance-based outlier factor (MOF)",
    long_description=long_description, 
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires = [
        'numpy>=1.23','numba>=0.56.0','scipy>=1.8.0','scikit-learn>=1.2.0', 'matplotlib>=3.5'
    ],
)

