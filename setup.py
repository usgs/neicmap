from distutils.core import setup

setup(name='neicmap',
      version='0.1dev',
      description='NEIC Python Mapping Library',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['neicmap'],
      install_requires=['numpy', 'matplotlib', 'scipy'],
      package_data = {'neicmap':['*.csv']},
)
