from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError

class SRACT2(SecurityCheck):
    """SRA-CT-2: Organization trail is encrypted with KMS"""
    
    def __init__(self, check_type="organization"):
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-2"
        self.check_name = "Organization trail is encrypted with KMS"
        self.severity = 'HIGH'
        self.description = ('This check verifies that your organization trail is encrypted with a KMS key. '
                          'Log files delivered by CloudTrail to your bucket should be encrypted by using SSE-KMS. '
                          'This is selected by default in the console but can be altered by users. With SSE-KMS '
                          'you create and manage the KMS key yourself with the ability to manage permissions on '
                          'who can use the key. For a user to read log files they must have read permissions to '
                          'the bucket and have permissions that allows decrypt permission on the key applied by '
                          'the KMS key policy.')
        self.check_logic = ('1. Verify execution from Organization Management account | '
                          '2. List all CloudTrail trails in the region | '
                          '3. Identify organization trail | '
                          '4. Check if trail is enabled and logging | '
                          '5. Verify KMS encryption is enabled on the trail | '
                          '6. Validate KMS key exists and is accessible | '
                          '7. Check passes if organization trail uses KMS encryption')
        self.service = 'CloudTrail'

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings of the check"""
        return self.findings

    def run(self, session):
        """Run the CloudTrail organization trail encryption check"""
        try:
            cloudtrail_client = session.client('cloudtrail')
            account_id = session.client('sts').get_caller_identity()['Account']
            region = session.region_name

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
                # Step 2: List all CloudTrail trails in the region
                trails = cloudtrail_client.list_trails()

                if not trails['Trails']:
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
                        'CheckedValue': 'Organization CloudTrail',
                        'ActualValue': 'No trails found',
                        'Remediation': 'Create an organization-level CloudTrail with KMS encryption enabled',
                        'Service': 'CloudTrail',
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    })
                    return self.findings

                org_trail_found = False
                
                for trail in trails['Trails']:
                    trail_name = trail['Name']
                    trail_arn = trail['TrailARN']
                    
                    # Step 3: Identify organization trail
                    trail_info = cloudtrail_client.get_trail(Name=trail_name)['Trail']
                    
                    if trail_info.get('IsOrganizationTrail'):
                        org_trail_found = True
                        
                        # Step 4: Check if trail is enabled and logging
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
                                'Service': 'CloudTrail',
                                'CheckLogic': self.check_logic,
                                'CheckType': self.check_type
                            })
                            continue

                        # Step 5: Verify KMS encryption is enabled on the trail
                        # Step 6: Validate KMS key exists and is accessible
                        if not trail_info.get('KmsKeyId'):
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
                                'CheckedValue': 'KMS Encryption',
                                'ActualValue': 'Organization trail is not KMS encrypted',
                                'Remediation': 'Enable KMS encryption for the organization trail',
                                'Service': 'CloudTrail',
                                'CheckLogic': self.check_logic,
                                'CheckType': self.check_type
                            })
                        else:
                            # Step 7: Check passes if organization trail uses KMS encryption
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
                                'CheckedValue': 'KMS Encryption',
                                'ActualValue': f"Organization trail is encrypted with key: {trail_info['KmsKeyId']}",
                                'Remediation': 'None required',
                                'Service': 'CloudTrail',
                                'CheckLogic': self.check_logic,
                                'CheckType': self.check_type
                            })

                if not org_trail_found:
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
                        'Remediation': 'Create an organization-level CloudTrail with KMS encryption enabled',
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
                    'ActualValue': f"Error: {str(e)}",
                    'Remediation': 'Check CloudTrail permissions and try again',
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
                'ActualValue': f"Error: {str(e)}",
                'Remediation': 'Check permissions and try again',
                'Service': 'CloudTrail',
                'CheckLogic': self.check_logic,
                'CheckType': self.check_type
            })
            
        return self.findings
