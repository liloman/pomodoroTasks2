#!/bin/env python
try:
    from setuptools import setup,find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup,find_packages

setup(
    name="pomodorotasks",
    packages=find_packages(exclude=['tests' 'tests/*']),
    install_requires=['tasklib', 'pygobject', 'dbus-python','future'],
    entry_points={
        'console_scripts': [
            'pomodoro-tasks-client = pomodorotasks.client:main'
            ],
        'gui_scripts': [
            'pomodoro-tasks-daemon = pomodorotasks.daemon:main',
            ]
        },
    include_package_data=True,
    package_data={'pomodorotasks': ['images/*.png', 'gui/*.glade']},
    test_suite='nose.collector',
    tests_require=['nose'],
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
    )
