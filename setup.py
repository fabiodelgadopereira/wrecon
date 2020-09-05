from setuptools import setup


setup(name='wrecon',
      version='0.1',
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
    ],
      zip_safe=False)