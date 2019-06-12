import logging
import boto3
import botocore
from multiprocessing.dummy import Pool
from typing import List
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily


class GuardDutyMetricsCollector():
    def __init__(self, regions: List[str]):
        self.regions = regions
        self.pool = Pool(len(self.regions))
        self.scrapeErrors = {region: 0 for region in regions}

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

        results = [self.pool.apply_async(self._collectMetricsByRegion, [region]) for region in self.regions]
        for result in results:
            region, regionStats = result.get()
            if not regionStats:
                self.scrapeErrors[region] += 1
            else:
                for severity, count in regionStats.items():
                    currentFindingsMetric.add_metric(value=count, labels=[region, severity])

            scrapeErrorsMetric.add_metric(value=self.scrapeErrors[region], labels=[region])

        return [currentFindingsMetric, scrapeErrorsMetric]

    def _collectMetricsByRegion(self, region):
        botoConfig = botocore.client.Config(connect_timeout=2, read_timeout=10, retries={"max_attempts": 2})
        session = boto3.session.Session()
        client = session.client("guardduty", config=botoConfig, region_name=region)
        regionStats = {"low": 0, "medium": 0, "high": 0}

        try:
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
        except Exception as error:
            logging.getLogger().error(f"Unable to scrape GuardDuty statistics from {region} because of error: {str(error)}")

            # We return False on error so we can increase the errors_total metric
            regionStats = False

        return (region, regionStats)
