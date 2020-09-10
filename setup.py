from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='wrecon',
      version='0.6',
      description='WRecon is an open source no intussive web scanner. It is designed to discover all URL in a website recursively, without using bruteforce or unauthorized access. It comes with a camouflage engine and nice features for pentesting.',
      url='https://github.com/fabiodelgadopereira/wrecon',
      author='Fabio Delgado',
      author_email='fabio_delgado2@hotmail.com',
      license='MIT',
      packages=['wrecon'],
      python_requires='>=3.7',
      install_requires=[
        'requests',
        'bs4',
        'colorama',
    ],long_description=long_description,
     long_description_content_type='text/markdown',
      zip_safe=False,
    entry_points={
        'console_scripts': [
            'wrecon = wrecon.wrecon:main',
        ]})