from setuptools import setup, find_packages

setup(
    name='tingpy',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'firebase-admin',
        'segno'
    ],
    author='TingPy Team',
    author_email='team@tingpy.com',
    description='A developer-friendly wrapper for Firebase Cloud Messaging with QR code pairing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/shithaarthan/tingpy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
