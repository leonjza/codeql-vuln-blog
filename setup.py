from setuptools import find_packages, setup

setup(
    name='vulnblog',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    extras_require={
        'dev': [
            'pytest',
        ]
    }
)
