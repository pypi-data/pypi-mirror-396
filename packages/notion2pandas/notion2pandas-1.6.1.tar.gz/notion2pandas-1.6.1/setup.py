from setuptools import setup

def get_description():
    with open("README.md") as file:
        return file.read()

setup(
    name='notion2pandas',
    version='1.6.1',
    description='Notion Client extension to import notion Database into pandas Dataframe',
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url='https://gitlab.com/Jaeger87/notion2pandas',
    author='Andrea Rosati',
    author_email='rosati.1595834@gmail.com',
    license='MIT',
    packages=['notion2pandas'],
    python_requires=">=3.7, <= 3.13",
    install_requires=[
    'notion-client == 2.5.0',
    'pandas == 2.3.3'
                      ],

    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",       
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ],
)
