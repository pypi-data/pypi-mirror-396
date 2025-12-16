# sraverify/lib/audit_info.py
from typing import List, Optional
import boto3
from .session import get_session
from .regions import validate_regions
from .org_mgmt_checker import OrgMgmtChecker

class AuditInfo:
    """Class to hold audit context information"""
    def __init__(self, 
                 regions: Optional[List[str]] = None,
                 profile: Optional[str] = None,
                 session: Optional[boto3.Session] = None):
        self.session = session or get_session(profile=profile)
        self.regions = self._initialize_regions(regions)
        self.profile = profile
        self.account_id = self._get_account_id()
        self.org_checker = OrgMgmtChecker()
        if session:
            self.org_checker.initialize(session)
            
    def _initialize_regions(self, specified_regions: Optional[List[str]] = None) -> List[str]:
        """Initialize and validate regions"""
        return validate_regions(specified_regions, self.session)

    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            return self.session.client('sts').get_caller_identity()['Account']
        except Exception as e:
            raise Exception(f"Failed to get AWS account ID: {str(e)}")

    def get_regional_session(self, region: str) -> boto3.Session:
        """Get a session for a specific region"""
        if region not in self.regions:
            raise ValueError(f"Region {region} is not in the list of validated regions")
        return get_session(region=region, profile=self.profile)
