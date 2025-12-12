from setuptools import setup, find_packages

setup(
    name="chuidi_zipcode",
    version="0.1.0",
    description="A super zipcode lookup library based on GeoNames CSV",
    long_description=open('README.md').read(),
    author="chuidi",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.7',
)