import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__),
                           'README.md')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-fragments-categories',
    version='0.1.2',
    packages=find_packages(),
    license='MIT License',
    description='Categories for the django fragments framework.',
    long_description=README,
    url='https://github.com/devopsjosh/django-fragments-categories',
    author='Joshua Tesch',
    author_email='jt@devopsjosh.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    install_requires=[
        'Django>=2.0',
    ]
)
