from os.path import dirname, join
from setuptools import find_packages, setup


readme_path = join(dirname(__file__), 'README.md')

with open(readme_path) as readme_file:
    readme = readme_file.read()


setup(
    name='aiothrottling',
    version='0.0.4',
    author='Konstantin Togoi',
    author_email='konstantin.togoi@protonmail.com',
    url='https://github.com/KonstantinTogoi/aiothrottling',
    project_urls={'Documentation': 'https://aiothrottling.readthedocs.io'},
    download_url='https://pypi.org/project/aiothrottling/',
    description='Throttling utilities for asyncio tasks.',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=find_packages(),
    platforms=['Any'],
    python_requires='>=3.5',
    install_requires=['aiothrottles'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest-asyncio'],
    keywords=['asyncio api throttle throttles throttler throttling'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
