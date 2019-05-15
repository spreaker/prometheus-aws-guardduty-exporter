import logging
import boto3
import botocore
from typing import List
from prometheus_client import Counter
from prometheus_client.core import GaugeMetricFamily


class GuardDutyMetricsCollector():
    def __init__(self, regions: List[str]):
        self.regions = regions

        # Init a metric used to keep the count of errors while
        # fetching statistics from GuardDuty
        self.scrapeErrorsMetric = Counter(
            "aws_guardduty_scrape_errors_total",
            "The total number of scrape errors",
            labelnames=["region"])

        for region in regions:
            self.scrapeErrorsMetric.labels(region).inc(amount=0)

    def collect(self):
        # Reset findings metric
        currentFindingsMetric = GaugeMetricFamily(
            "aws_guardduty_current_findings",
            "The current number of unarchived findings",
            labels=["region", "severity"])

        # Customize the boto client config
        botoConfig = botocore.client.Config(connect_timeout=2, read_timeout=10, retries={"max_attempts": 2})

        for region in self.regions:
            try:
                # Scrape GuardDuty statistics from the region
                regionStats = self._collectMetricsByRegion(region, botoConfig)

                # Add the findings to the exporterd metric
                for severity, count in regionStats.items():
                    currentFindingsMetric.add_metric(value=count, labels=[region, severity])
            except Exception as error:
                logging.getLogger().error(f"Unable to scrape GuardDuty statistics from {region} because of error: {str(error)}")

                # Increase the errors count
                self.scrapeErrorsMetric.labels(region).inc();

        return [currentFindingsMetric]

    def _collectMetricsByRegion(self, region, botoConfig):
        client = boto3.client("guardduty", config=botoConfig, region_name=region)
        regionStats = {"low": 0, "medium": 0, "high": 0}

        # List GuardDuty detectors
        detectorIds = client.list_detectors()["DetectorIds"]

        # Get statistics
        for detectorId in detectorIds:
            countBySeverity = client.get_findings_statistics(
                DetectorId=detectorId,
                FindingCriteria={"Criterion":{"service.archived":{"Eq":["false"]}}},
                FindingStatisticTypes=["COUNT_BY_SEVERITY"])["FindingStatistics"]["CountBySeverity"]

            for severity, count in countBySeverity.items():
                severity = float(severity)

                # Group severity levels into low, medium and high according to this doc:
                # https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html#guardduty_findings-severity
                if severity < 4:
                    regionStats["low"] += count
                elif severity < 7:
                    regionStats["medium"] += count
                else:
                    regionStats["high"] += count

        return regionStats
