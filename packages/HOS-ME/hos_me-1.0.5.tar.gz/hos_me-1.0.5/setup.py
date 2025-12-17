from setuptools import setup, find_packages
import os

# Read the requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# Read the README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='HOS_ME',
    version='1.0.5',
    author='HOS ME Team',
    author_email='hos_me@example.com',
    description='HOS ME - 一个功能强大的办公自动化平台，支持批量任务处理、模板管理、复杂内容渲染和文档导入导出',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hos-me/hos-me',
    packages=find_packages(include=['hos_office_platform', 'hos_office_platform.*']),
    include_package_data=True,
    package_data={
        'hos_office_platform': [
            'templates/*',
            'static/css/*',
            'static/js/*',
            'workflow_templates.json',
            'mod.txt'
        ],
    },
    # 移除敏感文件配置
    data_files=[
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Flask',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0',
            'flake8>=4.0',
            'black>=22.0',
            'isort>=5.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'hos-me=hos_office_platform.app:main',
            'hosme=hos_office_platform.app:main',
        ],
    },
    zip_safe=False,
)