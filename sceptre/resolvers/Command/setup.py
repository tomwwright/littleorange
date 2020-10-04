from setuptools import setup

setup(
    name='sceptre-resolver-command',
    version='0.1',
    description='Resolves argument as shell command',
    py_modules=['command'],
    entry_points={
        'sceptre.resolvers': [
            'Command = command:Command',
        ],
    }
)
