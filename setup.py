from os.path import dirname, join
from setuptools import setup


readme_path = join(dirname(__file__), 'README.md')

with open(readme_path) as readme_file:
    readme = readme_file.read()


setup(
    name='aiothrottling',
    version='0.0.1',
    author='Konstantin Togoi',
    author_email='konstantin.togoi@protonmail.com',
    url='https://github.com/KonstantinTogoi/aiovkcom',
    description='vk.com Python REST API wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=['aiothrottling'],
    keywords=['asyncio api throttling throttler'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)