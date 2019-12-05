from setuptools import setup
import pylint_report

setup(
    name=pylint_report.__name__,
    version=pylint_report.__version__,
    description='Generates an html report summarizing the results of pylint.',
    url='https://github.com/drdv/pylint-report',
    author='Dimitar Dimitrov',
    author_email='mail.mitko@gmail.com',
    license='Apache 2.0',
    python_requires='>=3.6',
    py_modules=['pylint_report'],
    install_requires=['pandas', 'pylint'],
    scripts=['pylint_report/pylint_report.py'],
)
