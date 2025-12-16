from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
import logging

class SRACT11(SecurityCheck):
    """SRA-CT-11: Organization Trail Log Archive Configuration"""
    
    def __init__(self, check_type="organization"):
        """Initialize the check with organization type"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-11"
        self.check_name = "Organization trail Logs are delivered to a centralized S3 bucket in the Log Archive Account"
        self.description = ('This check verifies whether the corresponding S3 buckets that stores organization trail logs in created in Log Archive account. '
                          'This separates the management and usage of CloudTrail log privileges. The Log Archive account is dedicated to '
                          'ingesting and archiving all security-related logs and backups.')
        self.service = "CloudTrail"
        self.severity = "HIGH"
        self.check_type = check_type
        self.check_logic = ('1. Verify execution from Organization Management Account | '
                           '2. Identify Log Archive account in the organization | '
                           '3. List CloudTrail trails and identify organization trails | '
                           '4. Verify S3 bucket is in Log Archive account | '
                           '5. Check passes if organization trail logs are delivered to Log Archive account S3 bucket')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings = []

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings"""
        return self.findings

    def find_log_archive_account(self, organizations_client) -> str:
        """Find the Log Archive account ID in the organization"""
        try:
            paginator = organizations_client.get_paginator('list_accounts')
            for page in paginator.paginate():
                for account in page['Accounts']:
                    # Check account name for "log" pattern (case insensitive)
                    if 'log' in account.get('Name', '').lower():
                        self.logger.debug(f"Found Log Archive account: {account['Name']} ({account['Id']})")
                        return account['Id']

                    # Check account tags as backup method
                    try:
                        tags = organizations_client.list_tags_for_resource(ResourceId=account['Id'])
                        for tag in tags.get('Tags', []):
                            if (tag.get('Key') == 'aws-control-tower' and 
                                'log' in tag.get('Value', '').lower()):
                                self.logger.debug(f"Found Log Archive account by tag: {account['Name']} ({account['Id']})")
                                return account['Id']
                    except ClientError:
                        continue
                    
            self.logger.error("No account found with 'log' in the name or tags")
            return None

        except ClientError as e:
            self.logger.error(f"Error listing organization accounts: {str(e)}")
            return None

    def run(self, session) -> None:
        """Run the security check"""
        try:
            # Get account information
            sts_client = session.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            region = session.region_name
            self.logger.debug(f"Running check for account: {account_id} in region: {region}")
            
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
            
            # Initialize clients
            organizations_client = session.client('organizations')
            cloudtrail_client = session.client('cloudtrail')
            
            try:
                # Find Log Archive account
                log_archive_account = self.find_log_archive_account(organizations_client)
                if not log_archive_account:
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "ERROR",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": "log-archive-account",
                        "ResourceType": "AWS::Organizations::Account",
                        "AccountId": account_id,
                        "CheckedValue": "Log Archive Account Identification",
                        "ActualValue": "Could not identify Log Archive account",
                        "Remediation": "Verify Control Tower setup and Log Archive account existence",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return
    
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
                        "Remediation": "Create an organization trail with S3 bucket in Log Archive account",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return
    
                # Check each organization trail for S3 bucket location
                valid_trail = None
                for trail in org_trails:
                    s3_bucket = trail.get('S3BucketName')
                    if not s3_bucket:
                        continue
                    
                    # Check if the bucket name contains the Log Archive account ID
                    if f"aws-controltower-logs-{log_archive_account}" in s3_bucket:
                        valid_trail = trail
                        self.logger.debug(f"Found trail with S3 bucket in Log Archive account: {trail['Name']}")
                        break
                    
                # Create finding based on S3 bucket location
                if valid_trail:
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "PASS",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": valid_trail['TrailARN'],
                        "ResourceType": "AWS::CloudTrail::Trail",
                        "AccountId": account_id,
                        "CheckedValue": "S3 Bucket Location",
                        "ActualValue": f"Organization trail {valid_trail['Name']} delivers logs to S3 bucket {valid_trail['S3BucketName']} in Log Archive account ({log_archive_account})",
                        "Remediation": "None required",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                else:
                    actual_value = f"Trail S3 bucket is not in Log Archive account ({log_archive_account})"
                    remediation = "Configure organization trail to deliver logs to S3 bucket in Log Archive account"
                    if org_trails:
                        trail = org_trails[0]
                        if not trail.get('S3BucketName'):
                            actual_value = f"Trail {trail['Name']} has no S3 bucket configured"
                            remediation = "Configure S3 bucket in Log Archive account for the organization trail"

                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "FAIL",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": (valid_trail or org_trails[0])['TrailARN'],
                        "ResourceType": "AWS::CloudTrail::Trail",
                        "AccountId": account_id,
                        "CheckedValue": "S3 Bucket Location",
                        "ActualValue": actual_value,
                        "Remediation": remediation,
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })

            except ClientError as e:
                self.logger.error(f"Error accessing AWS services: {str(e)}")
                self.findings.append({
                    "CheckId": self.check_id,
                    "Status": "ERROR",
                    "Region": region,
                    "Severity": self.severity,
                    "Title": f"{self.check_id} {self.check_name}",
                    "Description": self.description,
                    "ResourceId": "aws-services",
                    "ResourceType": "AWS::CloudTrail::Trail",
                    "AccountId": account_id,
                    "CheckedValue": "AWS Services Access",
                    "ActualValue": f"Error accessing AWS services: {str(e)}",
                    "Remediation": "Verify required permissions",
                    "Service": self.service,
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
                "Service": self.service,
                "CheckLogic": self.check_logic,
                "CheckType": self.check_type
            })
