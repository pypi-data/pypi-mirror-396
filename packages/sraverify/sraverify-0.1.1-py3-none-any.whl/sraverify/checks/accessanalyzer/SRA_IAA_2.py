from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError

class SRAIAA2(SecurityCheck):
    """SRA-IAA-2: IAM Access Analyzer Delegated Administration"""
    
    def __init__(self, check_type="organization"):
        # Ensure parent class is initialized first
        super().__init__(check_type=check_type)
        self.check_id = "SRA-IAA-2"
        self.check_name = "IAM Access Analyzer Delegated Administration"
        self.severity = "HIGH"
        self.description = ('This check verifies whether IAA service administration for your AWS Organization is '
                          'delegated out of your AWS Organization management account. The delegated administrator '
                          'has permissions to create and manage analyzers with the AWS organization as the zone of trust.')
        self.check_logic = ('1. Verify execution from Organization Management account | '
                          '2. Check for delegated administrator for IAA service | '
                          '3. Confirm that delegated administrator is not management account | '
                          '4. Check passes if IAA delegated administrator is not in management account')
        self.service = 'IAM'

    def run(self, session):
        """Run the security check"""
        try:
            region = session.region_name
            account_id = session.client('sts').get_caller_identity()['Account']

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

            # Step 2: Check for delegated administrator
            try:
                org_client = session.client('organizations')
                delegated_admins = org_client.list_delegated_administrators(
                    ServicePrincipal='access-analyzer.amazonaws.com'
                ).get('DelegatedAdministrators', [])

                if not delegated_admins:
                    finding = {
                        'CheckId': self.check_id,
                        'Status': 'FAIL',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': account_id,
                        'ResourceType': 'AWS::Organizations::Account',
                        'AccountId': account_id,
                        'CheckedValue': 'IAA Delegated Administrator',
                        'ActualValue': 'No delegated administrator configured',
                        'Remediation': 'Configure a member account as IAA delegated administrator',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    }
                    self.findings.append(finding)
                    return self.findings

                # Step 3: Confirm delegated administrator is not management account
                delegated_admin = delegated_admins[0]
                if delegated_admin['Id'] == account_id:
                    finding = {
                        'CheckId': self.check_id,
                        'Status': 'FAIL',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': account_id,
                        'ResourceType': 'AWS::Organizations::Account',
                        'AccountId': account_id,
                        'CheckedValue': 'IAA Delegated Administrator Configuration',
                        'ActualValue': f'Delegated administrator is management account: {account_id}',
                        'Remediation': 'Configure a member account (not management account) as IAA delegated administrator',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    }
                    self.findings.append(finding)
                else:
                    # Step 4: Check passes if delegated administrator is not management account
                    finding = {
                        'CheckId': self.check_id,
                        'Status': 'PASS',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': delegated_admin['Id'],
                        'ResourceType': 'AWS::Organizations::Account',
                        'AccountId': account_id,
                        'CheckedValue': 'IAA Delegated Administrator Configuration',
                        'ActualValue': f'Delegated administrator account: {delegated_admin["Id"]}',
                        'Remediation': 'None required',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    }
                    self.findings.append(finding)

            except ClientError as e:
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
                    'CheckedValue': 'Delegated Administrator Access',
                    'ActualValue': f'Error checking delegated administrator: {str(e)}',
                    'Remediation': 'Verify Organizations permissions',
                    'Service': self.service,
                    'CheckLogic': self.check_logic,
                    'CheckType': self.check_type
                }
                self.findings.append(finding)

        except Exception as e:
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
                'CheckedValue': 'Check Execution',
                'ActualValue': f'Error: {str(e)}',
                'Remediation': 'Check logs for more details',
                'Service': self.service,
                'CheckLogic': self.check_logic,
                'CheckType': self.check_type
            }
            self.findings.append(finding)

        return self.findings
