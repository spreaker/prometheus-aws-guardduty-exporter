import sys
from setuptools import setup

# Version
version = "1.0.0"

# Requires Python 3
if sys.version_info.major < 3:
    raise RuntimeError('Installing requires Python 3 or newer')

# Read the long description from README.md
with open('README.md') as file:
    long_description = file.read()

setup(
  name                          = 'prometheus-aws-guardduty-exporter',
  packages                      = ['prometheus_aws_guardduty_exporter'],
  version                       = version,
  description                   = 'Prometheus exporter for AWS GuardDuty',
  long_description              = long_description,
  long_description_content_type = 'text/markdown',
  author                        = 'Marco Pracucci',
  author_email                  = 'marco@pracucci.com',
  url                           = 'https://github.com/spreaker/prometheus-aws-guardduty-exporter',
  download_url                  = f'https://github.com/spreaker/prometheus-aws-guardduty-exporter/archive/{version}.tar.gz',
  keywords                      = ['prometheus', 'aws', 'guardduty'],
  classifiers                   = [],
  python_requires               = ' >= 3',
  install_requires              = ["boto3==1.9.148", "python-json-logger==0.1.11", "prometheus_client==0.6.0"],
  extras_require = {
    'dev': [
      'flake8==3.7.7',
      'twine==1.13.0'
    ]
  },
  entry_points = {
    'console_scripts': [
        'prometheus-aws-guardduty-exporter=prometheus_aws_guardduty_exporter.cli:run',
    ]
  }
)
