from setuptools import setup

setup(
    name='git-zip',
    version='0.1',
    packages=["gitzip"],
    url='',
    license='',
    author='Klaus-Dieter Bauer',
    author_email='kdb.devel@gmail.com',
    description='',
    entry_points = {
        "console_scripts": [
            "git-zip = gitzip.commands.git_zip:main"
        ]
    }
)
