from setuptools import setup

setup(
    name='kbauer_core_utils',
    version='0.1',
    packages=[],
    url='',
    license='',
    author='Klaus-Dieter Bauer',
    author_email='kdb.devel@gmail.com',
    description='',
    entry_points = {
        "console_scripts": [
            "kbauer_install_all = kbauer_coreutils.kbauer_install_all:main"
        ]
    }
)
