from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as fh:
    long_desc = fh.read()

setup(
    name='netbox_scion',
    version='1.4',
    description='NetBox plugin for managing SCION Links',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/anapaya/netbox-scion',
    author='Anapaya Systems AG',
    author_email='ops@anapaya.net',
    license='Apache-2.0',
    python_requires='>=3.8',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords='netbox netbox-plugin scion',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

