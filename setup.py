from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'agsci', 'solr', 'version.txt')).read().strip()

setup(name='agsci.solr',
    version=version,
    description="Multisite Solr search integration",
    long_description=open("README.txt").read() + "\n" +
                     open("HISTORY.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      ],
    keywords='',
    author='Tim Simkins, Penn State University',
    author_email='trs22@psu.edu',
    url='http://agsci.psu.edu/directory/trs22',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['agsci'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      # -*- Extra requirements: -*-
      ],
    entry_points="""
      # -*- Entry points: -*-
      """,
    )
