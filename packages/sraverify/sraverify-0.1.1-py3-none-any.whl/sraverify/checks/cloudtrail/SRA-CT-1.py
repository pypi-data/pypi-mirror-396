from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError

class SRACT1(SecurityCheck):
    """SRA-CT-1: Organization CloudTrail Configuration"""
    
    def __init__(self, check_type="organization"):
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-1"
        self.check_name = "Organization CloudTrail Configuration"
        self.severity = "HIGH"
        self.description = ('This check verifies that an organization trail is configured for your AWS Organization. '
                          'It is important to have uniform logging strategy for your AWS environment. Organization '
                          'trail logs all events for all AWS accounts in that organization and delivers logs to a '
                          'single S3 bucket, CloudWatch Logs and Event Bridge. Organization trails are automatically '
                          'applied to all member accounts in the organization. Member accounts can see the '
                          'organization trail, but can\'t modify or delete it. Organization trail should be '
                          'configured for all AWS regions even if you are not operating out of any region.')
        self.check_logic = ('1. Verify execution from Organization Management account | '  # Step 1: Check account permissions
                          '2. List CloudTrail trails in current region | '  # Step 2: Get all trails
                          '3. Check for organization trail with IsOrganizationTrail=true and IsMultiRegionTrail=true | '  # Step 3: Verify organization trail exists
                          '4. Verify trail configuration (S3 bucket, CloudWatch Logs, EventBridge) | '  # Step 4: Check trail settings
                          '5. Check passes if organization trail is properly configured')  # Step 5: All checks must pass
        self.service = 'CloudTrail'

    def get_findings(self):
        """Return the findings"""
        return self.findings

    def run(self, session):
        """Run the security check"""
        try:
            region = session.region_name
            account_id = session.client('sts').get_caller_identity()['Account']
            
            # Initialize clients
            org_client = session.client('organizations')
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

            # Steps 2 & 3: Check for organization trail
            try:
                trails = cloudtrail_client.list_trails()['Trails']
                org_trail = None
                non_org_trails = []

                for trail in trails:
                    trail_info = cloudtrail_client.get_trail(Name=trail['Name'])['Trail']
                    if (trail_info.get('IsOrganizationTrail', False) and 
                        trail_info.get('IsMultiRegionTrail', False)):
                        org_trail = trail_info
                        break
                    else:
                        non_org_trails.append(trail['Name'])

                if not org_trail:
                    failure_details = []
                    if not trails:
                        failure_details.append("No trails found")
                    if non_org_trails:
                        failure_details.append(f"Found non-organization trails: {', '.join(non_org_trails)}")
                    
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
                        'CheckedValue': 'Organization Trail Configuration',
                        'ActualValue': ' | '.join(failure_details) if failure_details else 'No organization-wide trail found',
                        'Remediation': 'Create an organization trail that logs all regions',
                        'Service': 'CloudTrail',
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    })
                    return self.findings

                # Step 4: Verify trail configuration
                try:
                    trail_status = cloudtrail_client.get_trail_status(Name=org_trail['Name'])
                    
                    config_issues = []
                    
                    if not org_trail.get('CloudWatchLogsLogGroupArn'):
                        config_issues.append("CloudWatch Logs integration not configured")
                    
                    if not org_trail.get('S3BucketName'):
                        config_issues.append("S3 bucket not configured")
                    
                    if not trail_status.get('IsLogging', False):
                        config_issues.append("Trail logging is not enabled")
                    
                    if config_issues:
                        self.findings.append({
                            'CheckId': self.check_id,
                            'Status': 'FAIL',
                            'Region': region,
                            "Severity": self.severity,
                            'Title': f"{self.check_id} {self.check_name}",
                            'Description': self.description,
                            'ResourceId': org_trail['TrailARN'],
                            'ResourceType': 'AWS::CloudTrail::Trail',
                            'AccountId': account_id,
                            'CheckedValue': 'Trail Configuration Details',
                            'ActualValue': f"Configuration issues found: {' | '.join(config_issues)}",
                            'Remediation': 'Configure CloudWatch Logs, S3 bucket, and enable logging for the organization trail',
                            'Service': 'CloudTrail',
                            'CheckLogic': self.check_logic,
                            'CheckType': self.check_type
                        })
                        return self.findings

                    # All checks passed
                    self.findings.append({
                        'CheckId': self.check_id,
                        'Status': 'PASS',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': org_trail['TrailARN'],
                        'ResourceType': 'AWS::CloudTrail::Trail',
                        'AccountId': account_id,
                        'CheckedValue': 'Organization Trail Configuration',
                        'ActualValue': (f"Organization trail: {org_trail['Name']} | "
                                      f"Multi-region: {org_trail['IsMultiRegionTrail']} | "
                                      f"Logging Enabled: {trail_status['IsLogging']} | "
                                      f"S3 Bucket: {org_trail['S3BucketName']} | "
                                      f"CloudWatch Logs Configured: {'Yes' if org_trail.get('CloudWatchLogsLogGroupArn') else 'No'}"),
                        'Remediation': 'None required',
                        'Service': 'CloudTrail',
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
                        'ResourceId': org_trail['TrailARN'],
                        'ResourceType': 'AWS::CloudTrail::Trail',
                        'AccountId': account_id,
                        'CheckedValue': 'Trail Status',
                        'ActualValue': f'Error checking trail status: {str(e)} | Error Code: {e.response["Error"]["Code"]}',
                        'Remediation': 'Verify CloudTrail permissions and trail configuration',
                        'Service': 'CloudTrail',
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
                    'CheckedValue': 'CloudTrail Access',
                    'ActualValue': f'Error accessing CloudTrail: {str(e)} | Error Code: {e.response["Error"]["Code"]}',
                    'Remediation': 'Verify CloudTrail permissions and service availability',
                    'Service': 'CloudTrail',
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
                'ActualValue': f'Unexpected error during check execution: {str(e)}',
                'Remediation': 'Review error logs and verify AWS credentials and permissions',
                'Service': 'CloudTrail',
                'CheckLogic': self.check_logic,
                'CheckType': self.check_type
            })

        return self.findings
