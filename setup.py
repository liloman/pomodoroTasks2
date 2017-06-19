#!/bin/env python
from setuptools import setup,find_packages

setup(
    name="pomodorotasks",
    packages=find_packages(exclude=['test' 'test/*']),
    install_requires=['tasklib', 'pygobject', 'dbus-python','future'],
    entry_points={
        'console_scripts': [
            'pomodoro-tasks-client = pomodoro.client:main'
            ],
        'gui_scripts': [
            'pomodoro-tasks-daemon = pomodorotasks.daemon:main',
            ]
        },
    include_package_data=True,
    package_data={'pomodorotasks': ['images/*.png', 'gui/*.glade']},
    test_suite='nose.collector',
    tests_require=['nose']
    )
