from setuptools import setup, find_packages

setup (
    name='nettect_stt',
    version='0.1',
    author='Naeem Ali',
    author_email='example@gmail.com',
    description='This is Speech to Text Recognition tool create by Naeem Ali'
)
packages = find_packages(),
install_requirments = [
    'selenium',
    'webdriver_manager'
] 