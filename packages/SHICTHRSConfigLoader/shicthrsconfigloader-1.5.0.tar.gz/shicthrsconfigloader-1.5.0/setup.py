from setuptools import setup, find_packages

setup(name='SHICTHRSConfigLoader',
      version='1.5.0',
      description='SHICTHRS Config file logging system',
      url='https://github.com/JNTMTMTM/SHICTHRS_ConfigLoader',
      author='SHICTHRS',
      author_email='contact@shicthrs.com',
      license='GPL-3.0',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['colorama==0.4.6'],
      zip_safe=False)