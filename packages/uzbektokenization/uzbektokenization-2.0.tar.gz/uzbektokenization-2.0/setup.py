from setuptools import setup, find_packages

setup(
    name='uzbektokenization',
    version='2.0',
    author='dasturbek',
    author_email='sobirovogabek0409@gmail.com',
    description='A package designed for segmenting Uzbek texts into (a) words (with compound words and phrases), (b) syllables, (c) affixes, and (d) characters.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ddasturbek/UzbekTokenization',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
