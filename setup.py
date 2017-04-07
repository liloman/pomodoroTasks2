#!/bin/env python
from setuptools import setup,find_packages

setup(
    name="pomodorotasks",
    packages=find_packages(),
    install_requires=['tasklib', 'pygobject'],
    entry_points={
        'console_scripts': [
            'pomodorotasks = pomodoro.client:main'
            ],
        'gui_scripts': [
            'pomodoro-taskd = pomodorotasks.daemon:main',
            ]
        },
    include_package_data=True,
    package_data={'pomodorotasks': ['images/*.png', 'gui/*.glade']}
    )
