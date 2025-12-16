import setuptools

# pylint: disable=all

setuptools.setup(
    name='iiko-sdk',
    version='0.0.8',
    author='Anton Gorinenko',
    author_email='anton.gorinenko@gmail.com',
    description='IIKO Cloud SDK API',
    long_description='',
    keywords='python, utils, http',
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages('.', exclude=['tests'], include=['iiko_sdk*']),
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
    # TODO: Убрать версии
    install_requires=[
        'aiohttp>=3.11',
        'http-misc>=1.0.4'
    ],
    extras_require={
        'test': [
            'pytest',
            'python-dotenv',
            'envparse',
            'pytest-asyncio'
        ]
    },
    python_requires='>=3.13',
)
