from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
import logging
from datetime import datetime, timezone

class SRACT9(SecurityCheck):
    """SRA-CT-9: Organization Trail CloudWatch Logs Delivery Status"""
    
    def __init__(self, check_type="organization"):
        """Initialize the check with organization type"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-9"
        self.check_name = "Organization trail is publishing logs to CloudWatch Logs"
        self.description = ('This check verifies that last attempt to send CloudTrail logs to CloudWatch Logs was successful. '
                          'Successful delivery of CloudTrails logs to CloudWatch ensures later availability for monitoring. '
                          'CloudTrail requires right permission to send log events to CloudWatch Logs.')
        self.service = "CloudTrail"
        self.severity = "HIGH"
        self.check_type = check_type
        self.check_logic = ('1. Verify execution from Organization Management Account | '
                          '2. List CloudTrail trails in current region | '
                          '3. Check for organization trail with IsOrganizationTrail=true | '
                          '4. Verify CloudWatch Logs configuration and successful delivery by checking: '
                          'a) CloudWatch Logs group is configured, b) IAM role is configured, '
                          'c) No delivery errors exist, d) Latest delivery was successful within 24 hours')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings = []

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings"""
        return self.findings

    def check_cloudwatch_delivery_status(self, cloudtrail_client, trail_name: str) -> tuple:
        """Check CloudWatch Logs delivery status and return status details"""
        try:
            status = cloudtrail_client.get_trail_status(Name=trail_name)
            latest_delivery_time = status.get('LatestCloudWatchLogsDeliveryTime')
            latest_delivery_error = status.get('LatestCloudWatchLogsDeliveryError', '')
            is_logging = status.get('IsLogging', False)
            

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


            # Check if delivery is recent (within 24 hours)
            current_time = datetime.now(timezone.utc)
            is_recent = False
            if latest_delivery_time:
                time_difference = current_time - latest_delivery_time
                is_recent = time_difference.total_seconds() < 86400  # 24 hours
            
            return is_logging, is_recent, latest_delivery_error
            
        except ClientError as e:
            self.logger.error(f"Error getting trail status for {trail_name}: {str(e)}")
            return False, False, str(e)

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
                        "Remediation": "Create an organization trail with CloudWatch Logs configuration",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return

                # Check each organization trail for CloudWatch Logs delivery status
                valid_trail = None
                for trail in org_trails:
                    trail_name = trail['Name']
                    cloudwatch_logs_group = trail.get('CloudWatchLogsLogGroupArn')
                    cloudwatch_logs_role = trail.get('CloudWatchLogsRoleArn')
                    
                    # Skip if CloudWatch Logs is not configured
                    if not (cloudwatch_logs_group and cloudwatch_logs_role):
                        continue
                    
                    is_logging, is_recent, delivery_error = self.check_cloudwatch_delivery_status(cloudtrail_client, trail_name)
                    
                    if is_logging and is_recent and not delivery_error:
                        valid_trail = trail
                        self.logger.debug(f"Found valid trail with successful CloudWatch Logs delivery: {trail_name}")
                        break

                # Create finding based on CloudWatch Logs delivery status
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
                        "CheckedValue": "CloudWatch Logs Delivery Status",
                        "ActualValue": f"Organization trail {valid_trail['Name']} is successfully delivering logs to CloudWatch Logs group",
                        "Remediation": "None required",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                else:
                    actual_value = "No organization trail found with successful recent CloudWatch Logs delivery"
                    remediation = "Verify CloudWatch Logs configuration and permissions"
                    if org_trails:
                        trail = org_trails[0]
                        if not (trail.get('CloudWatchLogsLogGroupArn') and trail.get('CloudWatchLogsRoleArn')):
                            actual_value = f"Trail {trail['Name']} has incomplete CloudWatch Logs configuration"
                            remediation = "Configure CloudWatch Logs group and IAM role for the organization trail"
                        elif delivery_error:
                            actual_value = f"Trail {trail['Name']} has delivery error: {delivery_error}"
                            remediation = "Resolve CloudWatch Logs delivery errors (check IAM role permissions)"
                        elif not is_recent:
                            actual_value = f"Trail {trail['Name']} has no recent CloudWatch Logs delivery"
                            remediation = "Verify trail logging is enabled and check CloudWatch Logs permissions"

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
                        "CheckedValue": "CloudWatch Logs Delivery Status",
                        "ActualValue": actual_value,
                        "Remediation": remediation,
                        "Service": self.service,
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
