"""
Setup file for uni_bot edX plugin.
"""

import os
import re

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(filename) as version_file:
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]",
            version_file.read(),
            re.M,
        )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Handles pip-compile output format with comments and indentation.
    """
    requirements = []
    for path in requirements_paths:
        with open(path) as reqs:
            for line in reqs:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('-'):
                    continue
                line = line.split('#')[0].strip()
                if line:
                    requirements.append(line)
    return requirements


setup(
    name='intela-unibot',
    version=get_version('uni_bot', '__init__.py'),
    author='Intela',
    author_email='info@intela.io',
    description='edX plugin for Uni Bot setup',
    license='AGPL',
    long_description='Uni Bot plugin for edX platform',
    long_description_content_type='text/plain',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
    ],
    packages=[
        'uni_bot',
        'uni_bot_auth',
    ],
    include_package_data=True,
    install_requires=load_requirements('requirements/base.txt'),
    zip_safe=False,
    entry_points={
        'lms.djangoapp': [
            'uni_bot = uni_bot.apps:UniBotPluginConfig',
            'uni_bot_auth = uni_bot_auth.apps:UniBotAuthAppConfig',
        ],
        'cms.djangoapp': ['uni_bot = uni_bot.apps:UniBotPluginConfig'],
        'openedx.course_tab': ['uni_bot_tab = uni_bot.tab:UniBotDashboardTab'],
    },
)
