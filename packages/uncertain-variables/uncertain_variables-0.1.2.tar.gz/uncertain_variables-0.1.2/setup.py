from setuptools import setup, find_packages

setup(
    name='uncertain_variables',
    version='0.1.2',
    author='András Urbanics, Bence Popovics, Emese Vastag, Elmar Zander, Noémi Friedman',
    author_email='popbence@hun-ren.sztaki.hu',
    description='Defining and handling variable sets with probability distributions for surrogate modelling and uncertainty quantification applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TRACE-Structures/uncertain_variables/',
    packages=find_packages(),
    py_modules=['uncertain_variables'],
    install_requires=[
        'numpy',
        'scikit-learn',
        'scipy',
        'matplotlib',
        'SALib',
        'pint'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
    ],
)
