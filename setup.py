from distutils.core import setup
setup(
  name = 'RP1210',
  packages = ['RP1210'],
  version = '0.0.1',
  license='MIT',
  description = 'A Python32 implementation of the RP1210C standard.',
  author = 'Darius Fieschko',
  author_email = 'dfieschko@gmail.com',
  url = 'https://github.com/dfieschko/RP1210',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/dfieschko/RP1210/archive/refs/tags/v0.0.1-alpha.tar.gz',    # I explain this later on
  keywords = ['RP1210', 'RP1210C', 'J1939'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
  ],
)
