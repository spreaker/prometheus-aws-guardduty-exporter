# Prometheus exporter for AWS GuardDuty


## Features

- Exports the number of current (unarchived) findings from AWS GuardDuty, splitted by region and severity
- Supports multiple AWS regions


## Exported metrics

The exporter exports the following metrics:

| Metric name                          | Type     | Labels               | Description      |
| ------------------------------------ | -------- | -------------------- | ---------------- |
| `aws_guardduty_exporter_up`          | gauge    | _None_               | Always `1`: can be used to check if it's running |
| `aws_guardduty_current_findings`     | gauge    | `region`, `severity` | The current number of unarchived findings |
| `aws_guardduty_scrape_errors_total`  | counter  | `region`, `severity` | The total number of scrape errors |


## How to run it

You have two options to run it:

1. Manually install and run the [`prometheus-aws-guardduty-exporter` Python package](https://pypi.org/project/prometheus-aws-guardduty-exporter/)
   ```
   pip3 install prometheus-aws-guardduty-exporter

   prometheus-aws-guardduty-exporter --region us-east-1
   ```

2. Use the [Docker image available on Docker hub](https://hub.docker.com/r/spreaker/prometheus-aws-guardduty-exporter/)
   ```
   docker run --env AWS_ACCESS_KEY_ID="id" --env AWS_SECRET_ACCESS_KEY="secret" spreaker/prometheus-aws-guardduty-exporter --region us-east-1
   ```

The cli supports the following arguments:

| Argument                       | Required | Description |
| ------------------------------ | -------- | ----------- |
| `--region REGION [REGION ...]` | yes      | AWS GuardDuty region (can specify multiple space separated regions) |
| `--role-arn`                   |          | The ARN of an AWS role to assume |
| `--exporter-host`              |          | The host at which the Prometheus exporter should listen to. Defaults to `127.0.0.1` |
| `--exporter-port`              |          | The port at which the Prometheus exporter should listen to. Defaults to `9100` |
| `--log-level LOG_LEVEL`        |          | Minimum log level. Accepted values are: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Defaults to `INFO` |

## Building and pushing to ECR

Prerequisites:
- Docker installed
- AWS CLI installed and configured (with `aws_profile=infra-prod`)

Example variables (use your ECR endpoint / repo):
```
export AWS_PROFILE=infra-prod
export AWS_REGION=eu-west-1
export ECR_REPO=886614085053.dkr.ecr.eu-west-1.amazonaws.com/prometheus-aws-guardduty-exporter
export ECR_REGISTRY=886614085053.dkr.ecr.eu-west-1.amazonaws.com
```

1. Login to ECR:
```
aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"
```

2. Build and push (amd64 example):
```
docker build -t prometheus-aws-guardduty-exporter:amd64 --build-arg ARCH=amd64/ .
docker tag prometheus-aws-guardduty-exporter:amd64 "$ECR_REPO:latest"
docker push "$ECR_REPO:latest"
```


## Required IAM privileges

In order to successfully run, this application requires the following IAM privileges:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid":    "ListDetectorsAndGetFindingsStatisticsInAnyRegion",
      "Effect": "Allow",
      "Action": [
        "guardduty:ListDetectors",
        "guardduty:GetFindingsStatistics"
      ],
      "Resource": "*"
    }
  ]
}
```

## Build & Push (Public ECR)

Build the Docker image from this directory, then push it to `public ECR` for `spreaker`.

Public ECR is located in the `infrastructure prod` AWS account so we need to use corresponding AWS Profile.

### Commands example

```sh
# Make sure you use the infra-prod AWS profile (used for `aws ecr-public login`).
# Option 1:
aws ecr-public get-login-password --profile infra-prod --region us-east-1 \
  | docker login --username AWS --password-stdin public.ecr.aws/spreaker

# Option 2 (equivalent):
# export AWS_PROFILE=infra-prod
# aws ecr-public get-login-password --region us-east-1 \
#   | docker login --username AWS --password-stdin public.ecr.aws/spreaker

# 1) Build
docker build -t prometheus-aws-guardduty-exporter:3.0.0 .

# 2) Tag
docker tag prometheus-aws-guardduty-exporter:3.0.0 \
  public.ecr.aws/spreaker/prometheus-aws-guardduty-exporter:3.0.0

# 3) Push
docker push public.ecr.aws/spreaker/prometheus-aws-guardduty-exporter:3.0.0
```


## Development

Run the development environment:

```
docker-compose build dev && docker-compose run --rm dev
```

Run tests in the dev environment:

```
python3 -m unittest
```


## License

This software is released under the [MIT license](LICENSE.txt).
