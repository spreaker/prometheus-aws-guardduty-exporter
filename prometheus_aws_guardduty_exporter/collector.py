import logging
import boto3
import botocore
import threading
from typing import List
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily


class GuardDutyMetricsCollector():
    def __init__(self, regions: List[str]):
        self.regions = regions
        self.scrapeErrors = {region: 0 for region in regions}
        self.botoConfig = None
        self.lock = threading.Lock()

    def scrape_metric_in_region(self, metric, region):
        try:
            # Scrape GuardDuty statistics from the region
            regionStats = self._collectMetricsByRegion(region)
            # Add the findings to the exporterd metric
            for severity, count in regionStats.items():
                self.lock.acquire()
                try:
                    metric.add_metric(value=count, labels=[region, severity])
                finally:
                    self.lock.release()
        except Exception as error:
            logging.getLogger().error(f"Unable to scrape GuardDuty statistics from {region} because of error: {str(error)}")

            # Increase the errors count
            self.scrapeErrors[region] += 1

    def collect(self):
        # Init metrics
        currentFindingsMetric = GaugeMetricFamily(
            "aws_guardduty_current_findings",
            "The current number of unarchived findings",
            labels=["region", "severity"])

        scrapeErrorsMetric = CounterMetricFamily(
            "aws_guardduty_scrape_errors_total",
            "The total number of scrape errors",
            labels=["region"])

        # Customize the boto client config
        self.botoConfig = botocore.client.Config(connect_timeout=2, read_timeout=10, retries={"max_attempts": 2})

        threads = []
        for region in self.regions:
            # We start one thread per region.
            process = threading.Thread(target=self.scrape_metric_in_region, args=[currentFindingsMetric, region])
            threads.append(process)

        for process in threads:
            process.start()

        for process in threads:
            process.join()

        # Update the scrape errors metric
        for region, errorsCount in self.scrapeErrors.items():
            scrapeErrorsMetric.add_metric(value=errorsCount, labels=[region])

        return [currentFindingsMetric, scrapeErrorsMetric]

    def _collectMetricsByRegion(self, region):
        client = boto3.client("guardduty", config=self.botoConfig, region_name=region)
        regionStats = {"low": 0, "medium": 0, "high": 0}

        # List GuardDuty detectors
        detectorIds = client.list_detectors()["DetectorIds"]

        # Get statistics
        for detectorId in detectorIds:
            countBySeverity = client.get_findings_statistics(
                DetectorId=detectorId,
                FindingCriteria={"Criterion": {"service.archived": {"Eq": ["false"]}}},
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
