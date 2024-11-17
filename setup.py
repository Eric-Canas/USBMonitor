from setuptools import setup, find_packages

setup(
    name='usb-monitor',
    version='1.23',
    author='Eric-Canas',
    author_email='eric@ericcanas.com',
    url='https://github.com/Eric-Canas/USBMonitor',
    description='USBMonitor is an easy-to-use cross-platform library for USB device monitoring that simplifies '
                'tracking of connections, disconnections, and examination of connected device attributes on '
                'Windows, Linux and MacOs, freeing the user from platform-specific details or incompatibilities.',

    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'pyudev; platform_system=="Linux"',
        'pywin32; platform_system=="Windows"',
        'wmi; platform_system=="Windows"',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Operating System',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)