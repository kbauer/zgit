from setuptools import setup

setup(
    name='git-zip',
    version='0.1',
    packages=["zgit"],
    url='https://github.com/kbauer/zgit',
    license='MIT',
    author='Klaus-Dieter Bauer',
    author_email='kdb.devel@gmail.com',
    description='',
    entry_points={
        "console_scripts": [
            "zgit = zgit.commands.zgit_command:main",
        ]
    }
)
