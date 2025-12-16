from typing import Dict, List, Any, Optional
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
import logging

class SRACT7(SecurityCheck):
    """SRA-CT-7: Organization trail is actively publishing events"""
    
    def __init__(self, check_type="account"):
        """Initialize the check with account type"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-7"
        self.check_name = "Organization trail is actively publishing events from accounts"
        self.description = ('This check verifies that your organization trail is running and actively '
                          'logging events. If a trail is modified to stop logging, accidentally or by '
                          'malicious user, you will not have visibility into API activity.')
        self.service = "CloudTrail"
        self.severity = "HIGH"
        self.check_type = check_type
        self.check_logic = ('1. List CloudTrail trails in current region | '
                           '2. Check for organization trail with IsOrganizationTrail=true | '
                           '3. Verify trail is actively logging')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings = []
        self._regions = None

    def initialize(self, regions: Optional[List[str]] = None):
        """Initialize check with optional regions"""
        self._regions = regions

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings"""
        return self.findings

    def check_trail_status(self, cloudtrail_client, trail_name: str) -> bool:
        """Check if trail is actively logging"""
        try:
            status = cloudtrail_client.get_trail_status(Name=trail_name)
            return status.get('IsLogging', False)
        except ClientError as e:
            self.logger.error(f"Error getting trail status for {trail_name}: {str(e)}")
            return False

    def check_region(self, session, region: str, account_id: str):
        """Check CloudTrail configuration in a specific region"""
        try:
            # Initialize CloudTrail client for this region
            cloudtrail_client = session.client('cloudtrail', region_name=region)
            
            try:
                # List trails and find organization trails
                trails = cloudtrail_client.describe_trails(includeShadowTrails=True)
                org_trails = [t for t in trails['trailList'] if t.get('IsOrganizationTrail')]
                self.logger.debug(f"Found {len(org_trails)} organization trails in {region}")

                if not org_trails:
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "FAIL",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": "organization-trail",
                        "ResourceType": "AWS::CloudTrail::Trail",
                        "AccountId": account_id,
                        "CheckedValue": "Organization Trail Configuration",
                        "ActualValue": "No organization trail found",
                        "Remediation": "Create an organization trail",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return

                # Check each organization trail for logging status
                active_trail = None
                for trail in org_trails:
                    trail_name = trail['Name']
                    if self.check_trail_status(cloudtrail_client, trail_name):
                        active_trail = trail
                        self.logger.debug(f"Found active trail: {trail_name} in {region}")
                        break

                if active_trail:
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "PASS",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": active_trail['TrailARN'],
                        "ResourceType": "AWS::CloudTrail::Trail",
                        "AccountId": account_id,
                        "CheckedValue": "Trail Logging Status",
                        "ActualValue": f"Organization trail {active_trail['Name']} is actively logging",
                        "Remediation": "None required",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                else:
                    trail = org_trails[0]
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "FAIL",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": trail['TrailARN'],
                        "ResourceType": "AWS::CloudTrail::Trail",
                        "AccountId": account_id,
                        "CheckedValue": "Trail Logging Status",
                        "ActualValue": f"Organization trail {trail['Name']} is not actively logging",
                        "Remediation": "Start logging for the organization trail",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })

            except ClientError as e:
                self.findings.append({
                    "CheckId": self.check_id,
                    "Status": "ERROR",
                    "Region": region,
                    "Severity": self.severity,
                    "Title": f"{self.check_id} {self.check_name}",
                    "Description": self.description,
                    "ResourceId": "cloudtrail",
                    "ResourceType": "AWS::CloudTrail::Trail",
                    "AccountId": account_id,
                    "CheckedValue": "CloudTrail API Access",
                    "ActualValue": f"Error accessing CloudTrail: {str(e)}",
                    "Remediation": "Verify CloudTrail permissions",
                    "Service": self.service,
                    "CheckLogic": self.check_logic,
                    "CheckType": self.check_type
                })

        except Exception as e:
            self.findings.append({
                "CheckId": self.check_id,
                "Status": "ERROR",
                "Region": region,
                "Severity": self.severity,
                "Title": f"{self.check_id} {self.check_name}",
                "Description": self.description,
                "ResourceId": "check-execution",
                "ResourceType": "AWS::CloudTrail::Trail",
                "AccountId": account_id,
                "CheckedValue": "Check Execution",
                "ActualValue": f"Error: {str(e)}",
                "Remediation": "Check logs for more details",
                "Service": self.service,
                "CheckLogic": self.check_logic,
                "CheckType": self.check_type
            })

    def run(self, session):
        """Run the security check"""
        try:
            # Get account information
            sts_client = session.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            
            # Get regions to check
            regions_to_check = self._regions if self._regions else [session.region_name]
            self.logger.debug(f"Checking regions: {regions_to_check}")
            
            # Check each region
            for region in regions_to_check:
                self.check_region(session, region, account_id)

        except Exception as e:
            self.logger.error(f"Unexpected error in check: {str(e)}")
            self.findings.append({
                "CheckId": self.check_id,
                "Status": "ERROR",
                "Region": session.region_name,
                "Severity": self.severity,
                "Title": f"{self.check_id} {self.check_name}",
                "Description": self.description,
                "ResourceId": "check-execution",
                "ResourceType": "AWS::CloudTrail::Trail",
                "AccountId": account_id if 'account_id' in locals() else "unknown",
                "CheckedValue": "Check Execution",
                "ActualValue": f"Unexpected error: {str(e)}",
                "Remediation": "Contact support team",
                "Service": self.service,
                "CheckLogic": self.check_logic,
                "CheckType": self.check_type
            })
