import os
from setuptools import find_packages, setup

package_name = 'esp32_cam_slam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/slam.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xenox',
    maintainer_email='gyawalipradip846@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fetcher = esp32_cam_slam.fetcher:main',
            'mapper = esp32_cam_slam.mapper:main',
            'processor = esp32_cam_slam.processor:main',
        ],
    },
)
