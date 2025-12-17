"""Setup configuration for font-generator package."""

from setuptools import setup, find_packages
import os


def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


setup(
    name='font-generator',
    version='0.1.1',
    description='A Python package for font manipulation and conversion',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='GenXLabs.org',
    author_email='genxlabs385@outlook.com',
    url='https://github.com/GenXLabs-org/font-generator',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Fonts',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.7',
    install_requires=[
        'fonttools>=4.0.0',
        'svgpathtools>=1.4.0',
    ],
    extras_require={
        'handwritten': ['fontforge'],  # Optional, requires system fontforge
    },
    entry_points={
        'console_scripts': [
            'font-generator=font_generator.cli:main',
        ],
    },
    keywords='font ttf otf svg conversion handwritten typography',
    project_urls={
        'Bug Reports': 'https://github.com/GenXLabs-org/font-generator/issues',
        'Source': 'https://github.com/GenXLabs-org/font-generator',
    },
)
