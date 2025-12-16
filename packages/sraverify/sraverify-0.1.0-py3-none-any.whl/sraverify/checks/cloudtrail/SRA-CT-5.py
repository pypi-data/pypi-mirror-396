from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
from datetime import datetime, timezone

class SRACT5(SecurityCheck):
    """SRA-CT-5: Organization Trail CloudWatch Logs Delivery"""
    
    def __init__(self, check_type="organization"):
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-5"
        self.check_name = "Organization Trail CloudWatch Logs Delivery"
        self.severity = "HIGH"
        self.description = ('This check verifies that last delivery of cloudtrail logs to CloudWatch Logs was successful. '
                          'CloudWatch Logs enables you to centralize the cloudtrail logs from all your AWS accounts and '
                          'regions in the AWS Organization, to a single, highly scalable service. You can then easily view '
                          'them, search them for specific error codes or patterns, filter them based on specific fields, '
                          'or archive them securely for future analysis.')
        self.check_logic = ('1. Verify execution from Organization Management account | '
                          '2. List CloudTrail trails in current region and identify organization trails (IsOrganizationTrail=true) | '
                          '3. For each organization trail, verify CloudWatch Logs integration is configured (CloudWatchLogsLogGroupArn and CloudWatchLogsRoleArn exist) | '
                          '4. Get trail status and verify no CloudWatch Logs delivery errors (LatestCloudWatchLogsDeliveryError is empty) | '
                          '5. Verify latest CloudWatch Logs delivery time exists and occurred within last 24 hours | '
                          '6. Check passes if all above conditions are met for at least one organization trail')
        self.service = 'CloudTrail'

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings"""
        return self.findings

    def run(self, session):
        """Run the security check"""
        try:
            region = session.region_name
            account_id = session.client('sts').get_caller_identity()['Account']
            
            organizations = session.client('organizations')
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

            # Step 2: List trails and identify organization trails
            try:
                trails = cloudtrail_client.list_trails()['Trails']
                org_trails = []
                
                for trail in trails:
                    trail_info = cloudtrail_client.get_trail(Name=trail['Name'])['Trail']
                    if trail_info.get('IsOrganizationTrail', False):
                        org_trails.append(trail_info)

                if not org_trails:
                    self.findings.append({
                        'CheckId': self.check_id,
                        'Status': 'FAIL',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': account_id,
                        'ResourceType': 'AWS::CloudTrail::Trail',
                        'AccountId': account_id,
                        'CheckedValue': 'Organization Trail',
                        'ActualValue': 'No organization trails found in the current region',
                        'Remediation': 'Create an organization-wide CloudTrail trail with CloudWatch Logs integration enabled',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    })
                    return self.findings

                for trail in org_trails:
                    trail_name = trail['Name']
                    trail_arn = trail['TrailARN']
                    failures = []

                    # Step 3: Verify CloudWatch Logs integration configuration
                    cloudwatch_logs_group_arn = trail.get('CloudWatchLogsLogGroupArn')
                    cloudwatch_logs_role_arn = trail.get('CloudWatchLogsRoleArn')
                    
                    if not cloudwatch_logs_group_arn:
                        failures.append('CloudWatch Logs group ARN is not configured')
                    if not cloudwatch_logs_role_arn:
                        failures.append('CloudWatch Logs role ARN is not configured')

                    if cloudwatch_logs_group_arn and cloudwatch_logs_role_arn:
                        # Step 4: Check CloudWatch Logs delivery errors
                        trail_status = cloudtrail_client.get_trail_status(Name=trail_name)
                        delivery_error = trail_status.get('LatestCloudWatchLogsDeliveryError')
                        if delivery_error:
                            failures.append(f"CloudWatch Logs delivery error: {delivery_error}")
                        
                        # Step 5: Verify latest delivery time
                        latest_delivery_time = trail_status.get('LatestCloudWatchLogsDeliveryTime')
                        if not latest_delivery_time:
                            failures.append('No CloudWatch Logs deliveries found')
                        else:
                            current_time = datetime.now(timezone.utc)
                            time_difference = current_time - latest_delivery_time
                            if time_difference.total_seconds() > 86400:  # 24 hours in seconds
                                failures.append(f'Last CloudWatch Logs delivery was more than 24 hours ago: {latest_delivery_time.isoformat()}')

                    if failures:
                        self.findings.append({
                            'CheckId': self.check_id,
                            'Status': 'FAIL',
                            'Region': region,
                            "Severity": self.severity,
                            'Title': f"{self.check_id} {self.check_name}",
                            'Description': self.description,
                            'ResourceId': trail_arn,
                            'ResourceType': 'AWS::CloudTrail::Trail',
                            'AccountId': account_id,
                            'CheckedValue': 'CloudWatch Logs Integration Requirements',
                            'ActualValue': f'Trail "{trail_name}" has the following issues: {" | ".join(failures)}',
                            'Remediation': ('Ensure CloudWatch Logs integration is properly configured and delivering logs within 24 hours'),
                            'Service': self.service,
                            'CheckLogic': self.check_logic,
                            'CheckType': self.check_type
                        })
                    else:
                        self.findings.append({
                            'CheckId': self.check_id,
                            'Status': 'PASS',
                            'Region': region,
                            "Severity": self.severity,
                            'Title': f"{self.check_id} {self.check_name}",
                            'Description': self.description,
                            'ResourceId': trail_arn,
                            'ResourceType': 'AWS::CloudTrail::Trail',
                            'AccountId': account_id,
                            'CheckedValue': 'CloudWatch Logs Integration Requirements',
                            'ActualValue': f'Organization trail {trail_name} has properly configured CloudWatch Logs integration and successfully delivered logs within the last 24 hours',
                            'Remediation': 'None required',
                            'Service': self.service,
                            'CheckLogic': self.check_logic,
                            'CheckType': self.check_type
                        })


            except ClientError as e:
                self.findings.append({
                    'CheckId': self.check_id,
                    'Status': 'ERROR',
                    'Region': region,
                    "Severity": self.severity,
                    'Title': f"{self.check_id} {self.check_name}",
                    'Description': self.description,
                    'ResourceId': account_id,
                    'ResourceType': 'AWS::CloudTrail::Trail',
                    'AccountId': account_id,
                    'CheckedValue': 'API Access',
                    'ActualValue': f'Error accessing CloudTrail API: {str(e)}',
                    'Remediation': 'Verify CloudTrail API permissions and retry',
                    'Service': self.service,
                    'CheckLogic': self.check_logic,
                    'CheckType': self.check_type
                })

        except Exception as e:
            self.findings.append({
                'CheckId': self.check_id,
                'Status': 'ERROR',
                'Region': region,
                "Severity": self.severity,
                'Title': f"{self.check_id} {self.check_name}",
                'Description': self.description,
                'ResourceId': account_id,
                'ResourceType': 'AWS::CloudTrail::Trail',
                'AccountId': account_id,
                'CheckedValue': 'Check Execution',
                'ActualValue': f'Error running check: {str(e)}',
                'Remediation': 'Review the error message and try again',
                'Service': self.service,
                'CheckLogic': self.check_logic,
                'CheckType': self.check_type
            })
            
        return self.findings
