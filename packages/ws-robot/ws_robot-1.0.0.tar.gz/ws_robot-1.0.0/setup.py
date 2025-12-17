"""
Setup script for ws-robot package
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ws-robot',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='WebSocket机器人客户端库 - 基于websocket-client的同步WebSocket机器人实现',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ws-robot',
    packages=find_packages(exclude=['test*', '*_use.py']),
    py_modules=[
        'ws_message',
        'ws_robot_client',
        'ws_robot_manager',
        'ws_robot_instance',
        'robot_api_body',
        'ws_robot_use'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'websocket-client>=1.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.18.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    keywords='websocket robot client sync agora rtc',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/ws-robot/issues',
        'Source': 'https://github.com/yourusername/ws-robot',
    },
)

