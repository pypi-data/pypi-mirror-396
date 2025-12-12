# -*- coding: utf-8 -*-
import codecs
import os

import setuptools

setuptools.setup(
    name='dding',
    version='0.1.9',
    keywords='dding',
    description='通知机器人.',
    # version = dding.__version__,
    install_requires=[
        'six',
    ],
    entry_points={
        'console_scripts': [
            'dding = dding.cmdline:main',
        ],
    },
    long_description=codecs.open(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        ), 'r', 'utf-8'
    ).read(),
    author='charlessoft',
    author_email='charlessoft@qq.com',

    url='https://github.com/charlessoft/dding',
    packages=setuptools.find_packages(),
    license='MIT'
)
