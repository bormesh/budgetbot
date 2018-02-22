# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

from setuptools import find_packages, setup

setup(

    name='budgetbot',

    version='0.0.1',

    packages=find_packages(),

    include_package_data=True,

    package_dir={'budgetbot': 'budgetbot'},

    scripts=[
        'budgetbot/scripts/rebuild-database',
        'budgetbot/scripts/run-webapp',
        'budgetbot/scripts/budgetbot-config',
        'budgetbot/scripts/upgrade-database',
    ],

)
