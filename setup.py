from setuptools import setup, find_packages

setup(
    name='usb-monitor',
    version='0.8',
    author='Eric-Canas',
    author_email='eric@ericcanas.com',
    url='https://github.com/Eric-Canas/USBMonitor',
    description='USBMonitor is an easy-to-use cross-platform library for USB device monitoring that simplifies '
                'tracking of connections, disconnections, and examination of connected device attributes on both '
                'Windows and Linux, freeing the user from platform-specific details or incompatibilities.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pyudev; platform_system=="Linux"',
        'pywin32; platform_system=="Windows"',
        'wmi; platform_system=="Windows"',
    ],
)