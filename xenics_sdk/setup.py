from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='xenics-xeneth',
    python_requires='>3.9',
    version='0.1.0',
    description='Xenics XenEth python SDK',
    url='https://www.xenics.com/',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Proprietary',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='xenics, xeneth, sdk',
    license='Proprietary',
)