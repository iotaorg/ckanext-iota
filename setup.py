from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-iota',
	version=version,
	description="CKAN Harvester for Iota",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Vitor Baptista',
	author_email='vitor@vitorbaptista.com',
	url='http://github.com/AwareTI/ckanext-iota',
	license='AGPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.iota'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	# myplugin=ckanext.iota:PluginClass
	""",
)
