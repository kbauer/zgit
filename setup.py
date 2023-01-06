from setuptools import setup

setup(
    name='git-zip',
    version='0.1',
    packages=["gitzip"],
    url='https://github.com/kbauer/git-zip',
    license='MIT',
    author='Klaus-Dieter Bauer',
    author_email='kdb.devel@gmail.com',
    description='',
    entry_points={
        "console_scripts": [
            "git-zip = gitzip.commands.git_zip:main",
            "git = gitzip.commands.git:main",
        ]
    }
)
