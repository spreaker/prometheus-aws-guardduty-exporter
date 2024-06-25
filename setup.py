import sys
from setuptools import setup

# Version
version = "3.0.0"

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
  author                        = 'Spreaker',
  author_email                  = 'dev@spreaker.com',
  url                           = 'https://github.com/spreaker/prometheus-aws-guardduty-exporter',
  download_url                  = f'https://github.com/spreaker/prometheus-aws-guardduty-exporter/archive/{version}.tar.gz',
  keywords                      = ['prometheus', 'aws', 'guardduty'],
  classifiers                   = [],
  python_requires               = ' >= 3.11',
  install_requires              = ["boto3==1.28.53", "python-json-logger==2.0.7", "prometheus_client==0.17.1"],
  extras_require = {
    'dev': [
      'flake8==6.1.0',
      'twine==4.0.2'
    ]
  },
  entry_points = {
    'console_scripts': [
        'prometheus-aws-guardduty-exporter=prometheus_aws_guardduty_exporter.cli:run',
    ]
  }
)
