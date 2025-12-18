from setuptools import setup,find_packages

setup(
    name='Lucifer-STT',
    version='0.1',
    author='Shreyas Warik',
    author_email='lucifer140705@gmail.com',
    description='this is speech to text package created by Shreyas Warik'
)
packages = find_packages(),
install_requirements= [
    'selenium',
    'webdriver_manger'
]
