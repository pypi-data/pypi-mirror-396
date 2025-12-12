from setuptools import setup, find_packages
import sys

install_requires = [
    'zeep',
    'python-dateutil',
    'pytz',
    'unidecode',
    'requests',
    'lxml',
    'qrcode'
]

if sys.version_info[:2] >= (3, 10):
    install_requires.append('cryptography')
else:
    install_requires.extend(['M2Crypto', 'pyopenssl==22.1.0'])

if sys.version_info[0] >= 3:
    install_requires.append('bs4')
else:
    install_requires.append('BeautifulSoup')

setup(
    name='l10n_ar_api',
    version='2.11.1',
    description='Libreria para localizacion Argentina',
    long_description='Libreria para localizacion Argentina',
    url='https://github.com/odoo-arg/l10n_ar_api',
    author='BLUEORANGE GROUP SRL',
    author_email='daniel@blueorange.com.ar',
    license='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Libreria para localizacion Argentina',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
