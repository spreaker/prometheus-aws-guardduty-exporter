# How to publish a new version

**Release python package**:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. [Release new version on GitHub](https://github.com/spreaker/prometheus-aws-guardduty-exporter/releases)
4. Build package `rm -f dist/* && python3 setup.py sdist`
5. Publish package `twine upload dist/*`

**Release Docker image**:

1. Update package version in `Dockerfile`
2. Build image
   ```
   docker rmi -f prometheus-aws-guardduty-exporter && \
   docker build -t prometheus-aws-guardduty-exporter .
   ```
3. Tag the image and push it to Docker Hub
   ```
   docker tag prometheus-aws-guardduty-exporter spreaker/prometheus-aws-guardduty-exporter:latest && \
   docker push spreaker/prometheus-aws-guardduty-exporter:latest

   docker tag prometheus-aws-guardduty-exporter spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION && \
   docker push spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION
   ```
