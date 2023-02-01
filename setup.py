from distutils.core import setup
import setuptools

setup(
  name = 'RP1210',
  packages = setuptools.find_packages(),
  version = '0.0.24',
  license='MIT',
  description = 'A Python32 implementation of the RP1210C standard.',
  long_description = open('README.md').read(),
  long_description_content_type = 'text/markdown',
  author = 'Darius Fieschko',
  author_email = 'dfieschko@gmail.com',
  url = 'https://github.com/dfieschko/RP1210',
  keywords = ['RP1210', 'RP1210C', 'J1939', 'CAN', 'UDS'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Operating System :: Microsoft :: Windows'
  ],
  project_urls = {
    'Wiki' : 'https://github.com/dfieschko/RP1210/wiki',
    'Issues' : 'https://github.com/dfieschko/RP1210/issues',
    'Discussions' : 'https://github.com/dfieschko/RP1210/discussions'
  },
  python_requires='>=3.9'
)
