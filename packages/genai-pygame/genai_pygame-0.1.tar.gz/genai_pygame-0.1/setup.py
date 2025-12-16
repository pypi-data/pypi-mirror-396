from setuptools import setup, find_packages

setup(
    name="GenAI-PyGame",
    description='A helpful PyGame tool for intergrating Generative AI models into game projects.',
    author='Alex Khon',
    author_email='alexoverkode@hotmail.com',
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'transformers'
    ],
)