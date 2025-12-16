from setuptools import setup, find_packages

setup(
    name='mmsw',
    version='0.0.15',
    description='Matilo (C) Deep-Learning Model Serving Worker Module',
    author='ryuvsken',
    author_email='ryuvskendev@gmail.com',
    url='https://github.com/ryuvsken',
    install_requires=[
        'sqlalchemy==2.0.44',
        'pymysql==1.1.2',
        'requests==2.32.5',
    ],
    keywords=['Deep-Learning', 'Model Serving', 'Matilo'],
    packages=find_packages(),
    #packages=find_packages(exclude=[]),
    #packages=['mmsw'],
    python_requires='>=3.11',
    include_package_data = True,
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.11',
    ],
)
