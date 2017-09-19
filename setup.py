from setuptools import setup, find_packages
from optimize_upip import OptimizeUpip

setup(
    name='micropython-ibmiotf',
    version='0.0.1',
    packages=find_packages(),
    description='Unofficial IBM Watson IoT Platform SDK for Devices Running Micropython',
    url='https://github.com/boneskull/micropython-ibmiotf',
    author='Christopher Hiller',
    author_email='boneskull@boneskull.com',
    maintainer='Christopher Hiller',
    maintainer_email='boneskull@boneskull.com',
    license='Apache-2.0',
    install_requires=(
        'micropython-umqtt.simple>=1.3.4', 'micropython-umqtt.robust>=1.0',
        'micropython-logging>=0.1.3'),
    cmdclass=dict(sdist=OptimizeUpip)
)
