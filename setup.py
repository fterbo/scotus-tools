# Copyright (c) 2018  Floyd Terbo

from distutils.core import setup
import setuptools


setup(name = "scotus-tools",
      version = "0.9.27",
      author = "Floyd Terbo",
      author_email = "fterbo@protonmail.com",
      packages = setuptools.find_packages(),
      install_requires = [
        "BeautifulSoup",
        "PyPDF2",
        "python-dateutil",
        "requests",
      ],
      zip_safe = False,
      scripts = ['tools/ordergrab', 'tools/docketgrab',
                 'tools/orderparse', 'tools/docketindexer',
                 'tools/docketsearch', 'tools/opiniongrab',
                 'tools/opinionindexer', 'tools/opinionsearch',
                 'tools/scotusstats', 'tools/docketsummary']
  )
