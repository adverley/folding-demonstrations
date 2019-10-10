from setuptools import setup, find_packages


def create_package_list(base_package):
    return ([base_package] +
            [base_package + '.' + pkg
             for pkg
             in find_packages(base_package)])


setup(
    name='folding_demonstrations',
    version='1.0',
    packages=create_package_list('folding_demonstrations'),
    include_package_data=True,
    install_requires=[
         'pillow'
    ],
    description='API and home of the wiki of a video dataset with human folding demonstrations',
    author='Andreas Verleysen',
    author_email='andreas.verleysen@ugent.be',
    license='CC BY 4.0',
)
