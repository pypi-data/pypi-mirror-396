from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError

class SRACT3(SecurityCheck):
    """SRA-CT-3: Organization Trail Log File Validation"""
    
    def __init__(self, check_type="organization"):
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-3"
        self.check_name = "Organization Trail Log File Validation"
        self.severity = 'HIGH'
        self.description = ('This check verifies that your organization trail has log file validation enabled. '
                         'Validated log files are especially valuable in security and forensic investigations. '
                         'CloudTrail log file integrity validation uses industry standard algorithms: SHA-256 '
                         'for hashing and SHA-256 with RSA for digital signing. This makes it computationally '
                         'unfeasible to modify, delete or forge CloudTrail log files without detection.')
        self.check_logic = ('1. Verify execution from Organization Management Account | '
                         '2. List CloudTrail trails in current region | '
                         '3. Check for organization trail with IsOrganizationTrail=true | '
                         '4. Verify trail configuration has EnableLogFileValidation=true | '
                         '5. Validate digest files are being delivered | '
                         '6. Check passes if organization trail has log file validation enabled and working')
        self.service = 'CloudTrail'

    def get_findings(self) -> List[Dict[str, Any]]:
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

            # Steps 2-6: List trails and check validation
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
                    'ActualValue': 'No organization trail found',
                    'Remediation': 'Create an organization-wide CloudTrail trail with log file validation enabled',
                    'Service': self.service,
                    'CheckLogic': self.check_logic,
                    'CheckType': self.check_type
                })
                return self.findings

            for trail in org_trails:
                trail_name = trail['Name']
                trail_arn = trail['TrailARN']

                # Check if logging is enabled
                trail_status = cloudtrail_client.get_trail_status(Name=trail_name)
                if not trail_status.get('IsLogging', False):
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
                        'CheckedValue': 'Trail Logging Status',
                        'ActualValue': 'Organization trail is not logging',
                        'Remediation': 'Enable logging for the organization trail',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    })
                    continue

                # Check log file validation
                if not trail.get('LogFileValidationEnabled', False):
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
                        'CheckedValue': 'Log File Validation',
                        'ActualValue': 'Log file validation is not enabled',
                        'Remediation': 'Enable log file validation on the organization CloudTrail trail',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    })
                else:
                    # Check if digest files are being delivered
                    if not trail_status.get('LatestDigestDeliveryTime'):
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
                            'CheckedValue': 'Digest File Delivery',
                            'ActualValue': 'No digest files have been delivered',
                            'Remediation': 'Verify S3 bucket permissions and trail configuration',
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
                            'CheckedValue': 'Log File Validation',
                            'ActualValue': 'Log file validation is enabled and digest files are being delivered',
                            'Remediation': None,
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
