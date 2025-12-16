from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
import logging

class SRACT4(SecurityCheck):
    """SRA-CT-4: Organization Trail Multi-Region Configuration"""
    
    def __init__(self, check_type="organization"):
        """Initialize the check with organization type"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-4"
        self.check_name = "Organization Trail Multi-Region Configuration"
        self.severity = "HIGH"
        self.description = ('This check verifies that your organization trail is configured as a multi-region trail. '
                          'This helps ensure you have visibility across your entire AWS environment.')
        self.check_logic = ('1. Verify execution from Organization Management account | '
                          '2. List CloudTrail trails in current region | '
                          '3. Check for organization trail with IsOrganizationTrail=true | '
                          '4. Verify trail configuration has IsMultiRegionTrail=true | '
                          '5. Verify trail is recording in all regions | '
                          '6. Check passes if organization trail is properly configured for multi-region logging')
        self.service = 'CloudTrail'
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings = []

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings"""
        return self.findings

    def run(self, session) -> None:
        """Run the security check"""
        try:
            # Get account information
            sts_client = session.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            region = session.region_name
            self.logger.debug(f"Running check for account: {account_id} in region: {region}")
            
            # Initialize CloudTrail client
            cloudtrail_client = session.client('cloudtrail')
            
             # Step 1: Verify we're in management account using org_mgmt_checker
            is_management, error_message = self.org_checker.verify_org_management()
            if not is_management:
                finding = {
                    'CheckId': self.check_id,
                    'Status': 'ERROR',
                    'Region': region,
                    "Severity": self.severity,
                    'Title': f"{self.check_id} {self.check_name}",
                    'Description': self.description,
                    'ResourceId': account_id,
                    'ResourceType': 'AWS::Organizations::Account',
                    'AccountId': account_id,
                    'CheckedValue': 'Management Account Access',
                    'ActualValue': error_message if error_message else 'Not running from management account',
                    'Remediation': 'Run this check from the Organization Management Account',
                    'Service': self.service,
                    'CheckLogic': self.check_logic,
                    'CheckType': self.check_type
                }
                self.findings.append(finding)
                return self.findings

            try:
                # List trails and find organization trails
                trails = cloudtrail_client.describe_trails(includeShadowTrails=True)
                org_trails = [t for t in trails['trailList'] if t.get('IsOrganizationTrail')]
                self.logger.debug(f"Found {len(org_trails)} organization trails")

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
                        "Remediation": "Create an organization trail with multi-region logging enabled",
                        "Service": "CloudTrail",
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return

                # Check multi-region configuration for organization trails
                multi_region_trail = None
                for trail in org_trails:
                    if trail.get('IsMultiRegionTrail'):
                        multi_region_trail = trail
                        self.logger.debug(f"Found multi-region organization trail: {trail['Name']}")
                        break

                # Create finding based on multi-region configuration
                status = "PASS" if multi_region_trail else "FAIL"
                actual_value = (f"Organization trail {multi_region_trail['Name'] if multi_region_trail else org_trails[0]['Name']} "
                              f"{'is' if multi_region_trail else 'is not'} configured for multi-region logging")
                
                self.findings.append({
                    "CheckId": self.check_id,
                    "Status": status,
                    "Region": region,
                    "Severity": self.severity,
                    "Title": f"{self.check_id} {self.check_name}",
                    "Description": self.description,
                    "ResourceId": (multi_region_trail or org_trails[0])['TrailARN'],
                    "ResourceType": "AWS::CloudTrail::Trail",
                    "AccountId": account_id,
                    "CheckedValue": "Multi-Region Configuration",
                    "ActualValue": actual_value,
                    "Remediation": "None required" if multi_region_trail else "Enable multi-region logging for the organization trail",
                    "Service": "CloudTrail",
                    "CheckLogic": self.check_logic,
                    "CheckType": self.check_type
                })

            except ClientError as e:
                self.logger.error(f"Error accessing CloudTrail: {str(e)}")
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
                    "Service": "CloudTrail",
                    "CheckLogic": self.check_logic,
                    "CheckType": self.check_type
                })

        except Exception as e:
            self.logger.error(f"Unexpected error in check: {str(e)}")
            self.findings.append({
                "CheckId": self.check_id,
                "Status": "ERROR",
                "Region": region if 'region' in locals() else session.region_name,
                "Severity": self.severity,
                "Title": f"{self.check_id} {self.check_name}",
                "Description": self.description,
                "ResourceId": "check-execution",
                "ResourceType": "AWS::CloudTrail::Trail",
                "AccountId": account_id if 'account_id' in locals() else "unknown",
                "CheckedValue": "Check Execution",
                "ActualValue": f"Unexpected error: {str(e)}",
                "Remediation": "Contact support team",
                "Service": "CloudTrail",
                "CheckLogic": self.check_logic,
                "CheckType": self.check_type
            })
