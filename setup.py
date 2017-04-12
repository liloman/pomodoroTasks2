#!/bin/env python
from setuptools import setup,find_packages

setup(
    name="pomodorotasks",
    packages=find_packages(exclude=['test' 'test/*']),
    install_requires=['tasklib', 'pygobject', 'dbus-python'],
    entry_points={
        'console_scripts': [
            'pomodorotasks = pomodoro.client:main'
            ],
        'gui_scripts': [
            'pomodoro-taskd = pomodorotasks.daemon:main',
            ]
        },
    include_package_data=True,
    package_data={'pomodorotasks': ['images/*.png', 'gui/*.glade']},
    test_suite='nose.collector',
    tests_require=['nose']
    )
