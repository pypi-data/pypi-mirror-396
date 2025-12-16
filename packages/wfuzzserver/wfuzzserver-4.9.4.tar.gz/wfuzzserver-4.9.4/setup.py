import os
import sys
import re
from setuptools import setup, find_packages

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


version = re.search(
    r'^__version__\s*=\s*"(.*)"',
    open('src/wfuzzserver/__init__.py').read(),
    re.M
).group(1)

docs_requires = [
    "Sphinx",
]

dev_requires = [
    'mock',
    'coverage',
    'codecov',
    'netaddr',  # tests/api/test_payload.py uses ipranges payload
    'pip-tools',
    'flake8==3.8.3',
    'black==19.10b0;python_version>"3.5"',
    'pytest',
]

install_requires = [
    'pycurl',
    'pyparsing>=2.4',  #'pyparsing>=2.4*'
    'six',
    'configparser',
    'chardet',
    'xmltodict',
    'dicttoxml',
    'requests_toolbelt>=1.0.0'
]


if sys.platform.startswith("win"):
    install_requires += ["colorama>=0.4.0"]


try:
    #os.symlink('../../docs/user/advanced.rst', 'src/wfuzzserver/advanced.rst')
    setup(
        name="wfuzzserver",
        packages=find_packages(where='src'),
        package_dir={'wfuzzserver': 'src/wfuzzserver'},
        include_package_data=True,
        package_data={'wfuzzserver': ['*.rst']},
        entry_points={
            'console_scripts': [
                'wfuzzserver = wfuzzserver.wfuzz:main',
                'wfpayloadserver = wfuzzserver.wfuzz:main_filter',
                'wfencodeserver = wfuzzserver.wfuzz:main_encoder',
            ],
            'gui_scripts': [
                'wxfuzzserver = wfuzzserver.wfuzz:main_gui',
            ]
        },
        version="4.9.4",  #4.9.4 version uses only http/1.1, to disble this search for "#revert to http/1.1"
        description="Wfuzz - The web fuzzer",
        long_description=long_descr,
        long_description_content_type='text/markdown',
        author="Xavi Mendez (@x4vi_mendez)",
        author_email="",
        url="http://wfuzz.org",
        license="GPLv2",
        install_requires=install_requires,
        extras_require={
            'dev': dev_requires,
            'docs': docs_requires,
        },
        python_requires=">=2.6",
        classifiers=(
            'Development Status :: 4 - Beta',
            'Natural Language :: English',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ),
    )
except Exception as e:
    #os.unlink('src/wfuzzserver/advanced.rst')
    print(">>>>>>>>>>>>>Exception in Setup")
    print(e)
