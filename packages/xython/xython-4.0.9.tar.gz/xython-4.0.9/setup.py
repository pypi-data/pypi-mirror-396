# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

#with open("README.md", "rt", encoding='UTF8') as fh:
#    long_description = fh.read()
setup(
    name='xython',
    version='4.0.9',
    url='https://www.xython.co.kr',
    install_requires=[],
    author='sj park',
    author_email='sjpkorea@naver.com',
    description="win32com + python + Office Automation = xython, (for easy automation for excel, word, outlook, regex, color, hwp, etc BY python & win32com)",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "xython": ["*.*"],
        },
    long_description_content_type="text/markdown",
    long_description=open('README.md', "r", encoding='UTF8').read(),
    python_requires='>=3.8',
    zip_safe=False,
    classifiers=['License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
    project_urls = {
      'Documentation': 'https://sjpkorea.github.io/xython.github.io/',
      'Link 1': 'https://www.xython.co.kr',
    }
    )

