import os
import codecs
from setuptools import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name             = 'yat',
    packages         = ['yat'],
    version          = '0.1',
    description      = 'Yet Another Translator using Google Translate API.',
    long_description = read('README.md'),
    author           = 'rr-',
    author_email     = 'rr-@sakuya.pl',
    url              = 'https://github.com/rr-/translator',
    download_url     = 'https://github.com/rr-/translator/tarball/0.2',
    keywords         = ['google translate', 'cli', 'translate', 'translator', 'google'],
    install_requires = ['colorama'],
    scripts          = ['yat/tl'],
    classifiers      = [],
)
