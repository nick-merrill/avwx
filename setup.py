from setuptools import setup

setup(
    name='avwx',
    version='1.0.0',
    description="A tool to grab aviation-related weather",
    url="https://github.com/cloudrave/avwx",
    author="Nick Merrill",
    author_email="public@nickmerrill.co",
    license='MIT',
    packages=['avwx'],
    install_requires=[
        'python-dateutil',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='aviation-weather',
)
