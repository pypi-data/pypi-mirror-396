from setuptools import setup, find_packages # type: ignore

setup(
    name='thart-automata',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'run-thart = thart_core.automata:markov_analysis',
        ],
    },
    # Metadata for PyPI
    author='ORG: Mohammed Farhaan',
    description='A Python package for THART-n automata.',
    url='https://github.com/Mohammed-farhaan-math/THARTn',

)