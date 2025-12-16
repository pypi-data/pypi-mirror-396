# sraverify/checks/__init__.py
"""
Base classes for security checks
"""
from typing import List, Optional
import boto3
from sraverify.lib.org_mgmt_checker import OrgMgmtChecker


class SecurityCheck:
    """Base class for all security checks"""
    def __init__(self, check_type="account"):
        self.check_type = check_type
        self.check_id = None
        self.title = None
        self.description = None
        self.rationale = None
        self.remediation = None
        self.impact = "Unknown"
        self.findings = []
        self._regions = None
        self.org_checker = OrgMgmtChecker()

    def initialize(self, regions: Optional[List[str]] = None):
        """Initialize check with optional regions"""
        if self.check_type == "account":
            self._regions = regions if regions else self._get_enabled_regions()
        # Organization checks don't use regions, so we don't set them

    def _get_enabled_regions(self) -> List[str]:
        """Get all enabled regions in the AWS account"""
        try:
            session = boto3.Session()
            ec2_client = session.client('ec2', region_name='us-east-1')
            response = ec2_client.describe_regions(AllRegions=False)
            return [region['RegionName'] for region in response['Regions']]
        except Exception as e:
            raise Exception(f"Failed to get enabled regions: {str(e)}")

    def validate_regions(self, regions: List[str]) -> bool:
        """Validate if specified regions are valid and enabled"""
        enabled_regions = set(self._get_enabled_regions())
        return all(region in enabled_regions for region in regions)

    @property
    def regions(self) -> List[str]:
        """Get regions for this check"""
        return self._regions if self._regions else []

    def run(self, session):
        """Run the security check"""
        raise NotImplementedError("Subclasses must implement run()")

    def get_findings(self):
        """Return findings from the check"""
        return self.findings
