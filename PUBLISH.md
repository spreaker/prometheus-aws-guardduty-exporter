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
   docker rmi -f prometheus-aws-guardduty-exporter
   docker build -t prometheus-aws-guardduty-exporter:amd64 --build-arg ARCH=amd64/ .
   docker build -t prometheus-aws-guardduty-exporter:arm32v7 --build-arg ARCH=arm32v7/ .
   docker build -t prometheus-aws-guardduty-exporter:arm64v8 --build-arg ARCH=arm64v8/ .
   ```
3. Tag and push it to Docker Hub
   ```
   docker tag prometheus-aws-guardduty-exporter:amd64 spreaker/prometheus-aws-guardduty-exporter:latest-amd64
   docker tag prometheus-aws-guardduty-exporter:arm32v7 spreaker/prometheus-aws-guardduty-exporter:latest-arm32v7
   docker tag prometheus-aws-guardduty-exporter:arm64v8 spreaker/prometheus-aws-guardduty-exporter:latest-arm64v8

   docker tag prometheus-aws-guardduty-exporter:amd64 spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-amd64
   docker tag prometheus-aws-guardduty-exporter:arm32v7 spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-arm32v7
   docker tag prometheus-aws-guardduty-exporter:arm64v8 spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-arm64v8

   docker push spreaker/prometheus-aws-guardduty-exporter:latest-amd64
   docker push spreaker/prometheus-aws-guardduty-exporter:latest-arm32v7
   docker push spreaker/prometheus-aws-guardduty-exporter:latest-arm64v8

   docker push spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-amd64
   docker push spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-arm32v7
   docker push spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-arm64v8
   ```

3. Create and push multi-arch manifests
   ```
   docker manifest create spreaker/prometheus-aws-guardduty-exporter:latest \
      --amend spreaker/prometheus-aws-guardduty-exporter:latest-amd64 \
      --amend spreaker/prometheus-aws-guardduty-exporter:latest-arm32v7 \
      --amend spreaker/prometheus-aws-guardduty-exporter:latest-arm64v8
   docker manifest push spreaker/prometheus-aws-guardduty-exporter:latest

   docker manifest create spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION \
      --amend spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-amd64 \
      --amend spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-arm32v7 \
      --amend spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION-arm64v8
   docker manifest push spreaker/prometheus-aws-guardduty-exporter:REPLACE-VERSION
   ```