from distutils.core import setup

setup(name='neicmap',
      version='0.1dev',
      description='NEIC Python Mapping Library',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      install_requires=['numpy', 'matplotlib', 'scipy'],
      package_data = {'pagermap':['*.csv']},
)
