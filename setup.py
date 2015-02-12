from setuptools import setup

setup(
    name='avwx',
    version='0.1',
    description="A tool to grab aviation-related weather",
    url="https://github.com/NicholasMerrill/avwx",
    author="Nick Merrill",
    author_email="public@nickmerrill.co",
    license='MIT',
    packages=['avwx'],
    install_requires=[
        'python-dateutil',
    ],
    zip_safe=False,
)

