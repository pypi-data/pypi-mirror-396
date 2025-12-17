from setuptools import setup, find_packages
import d2l

requirements = [
    'jupyter==1.0.0',
    'numpy==1.26.3',
    'matplotlib==3.8.2',
    'matplotlib-inline==0.1.6',
    'requests==2.31.0',
    'pandas==2.2.0',
    'scipy==1.12.0'
]

setup(
    name='d2dl',
    version=1.0,
    python_requires='>=3.8',
    author='D2L Developers',
    author_email='d2l.devs@gmail.com',
    url='https://d2l.ai',
    description='Dive into Deep Learning',
    license='MIT-0',
    packages=find_packages(),
    zip_safe=True,
    install_requires=requirements,
)
