import os
from setuptools import setup, find_packages

import librarian_dbmanage as pkg


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = pkg.__version__

setup(
    name='librarian-dbmanage',
    version=VERSION,
    license='BSD',
    packages=[pkg.__name__],
    include_package_data=True,
    long_description=read('README.rst'),
    install_requires=[
        'librarian_core',
        'librarian_lock',
        'librarian_content',
        'librarian_dashboard',
    ],
    dependency_links=[
        'git+ssh://git@github.com/Outernet-Project/librarian-core.git#egg=librarian_core-0.1',
        'git+ssh://git@github.com/Outernet-Project/librarian-lock.git#egg=librarian_lock-0.1',
        'git+ssh://git@github.com/Outernet-Project/librarian-content.git#egg=librarian_content-0.1',
        'git+ssh://git@github.com/Outernet-Project/librarian-dashboard.git#egg=librarian_dashboard-0.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Applicaton',
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
