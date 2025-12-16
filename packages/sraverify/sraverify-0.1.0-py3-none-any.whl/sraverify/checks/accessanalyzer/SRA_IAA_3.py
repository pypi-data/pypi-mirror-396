from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError

class SRAIAA3(SecurityCheck):
    """SRA-IAA-3: IAM Access Analyzer Security Tooling Admin"""
    
    def __init__(self, check_type="organization", security_ou_name=None):
        super().__init__(check_type=check_type)
        self.check_id = "SRA-IAA-3"
        self.check_name = "IAM Access Analyzer Security Tooling Admin"
        self.severity = "HIGH"
        self.security_ou_name = security_ou_name.lower() if security_ou_name else None
        self.description = ('This check verifies whether IAA delegated admin account is the security tooling account of '
                          'your AWS organization. Security Tooling account is dedicated to operating security services + '
                          'monitoring AWS accounts + automating security alerting and response. IAA helps monitor '
                          'resources shared outside zone of trust.')
        self.check_logic = ('1. Verify execution from Organization Management account | '
                          '2. List all Organization Units and find specified OU (via flag --security-ou-name) or OU containing "security" | '
                          '3. Create list of all accounts in Security OU | '
                          '4. List delegated administrators for IAM Access Analyzer service | '
                          '5. Verify delegated admin account exists in specified Security OU or OU containing "security" | '
                          '6. Check passes if delegated admin is found in Security OU account list')
        self.service = 'IAM'

    def get_findings(self):
        """Return the findings"""
        return self.findings

    def find_security_ou(self, org_client, root_id):
        """Find the security OU based on name parameter or default search"""
        paginator = org_client.get_paginator('list_organizational_units_for_parent')
        search_term = self.security_ou_name if self.security_ou_name else 'security'
        
        for page in paginator.paginate(ParentId=root_id):
            for ou in page['OrganizationalUnits']:
                # If security_ou_name is provided, use exact match
                if self.security_ou_name and self.security_ou_name == ou['Name'].lower():
                    return ou['Id'], ou['Name'], search_term
                # If no security_ou_name provided, look for 'security' in name
                elif not self.security_ou_name and 'security' in ou['Name'].lower():
                    return ou['Id'], ou['Name'], search_term
        
        return None, None, search_term

    def run(self, session):
        """Run the security check and return findings"""
        try:
            region = session.region_name
            account_id = session.client('sts').get_caller_identity()['Account']
            org_client = session.client('organizations')

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

            # Step 2 & 3: Find Security OU and list all accounts in it
            security_ou_accounts = []
            try:
                root_id = org_client.list_roots()['Roots'][0]['Id']
                
                # Find Security OU using the helper method
                security_ou_id, ou_name, search_term = self.find_security_ou(org_client, root_id)

                if not security_ou_id:
                    finding = {
                        'CheckId': self.check_id,
                        'Status': 'FAIL',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': account_id,
                        'ResourceType': 'AWS::Organizations::OrganizationalUnit',
                        'AccountId': account_id,
                        'CheckedValue': 'Security OU',
                        'ActualValue': f'No OU matching "{search_term}" found',
                        'Remediation': f'Create appropriate OU matching "{search_term}"',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    }
                    self.findings.append(finding)
                    return self.findings

                # Get all accounts in Security OU
                accounts_paginator = org_client.get_paginator('list_accounts_for_parent')
                for accounts_page in accounts_paginator.paginate(ParentId=security_ou_id):
                    security_ou_accounts.extend(accounts_page['Accounts'])

                if not security_ou_accounts:
                    finding = {
                        'CheckId': self.check_id,
                        'Status': 'FAIL',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': security_ou_id,
                        'ResourceType': 'AWS::Organizations::OrganizationalUnit',
                        'AccountId': account_id,
                        'CheckedValue': f'Accounts in {ou_name} OU',
                        'ActualValue': f'OU: {ou_name}, No accounts found',
                        'Remediation': f'Add accounts to {ou_name} OU',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    }
                    self.findings.append(finding)
                    return self.findings

                # Step 4 & 5: Check IAA delegated administrator and verify it's in Security OU
                try:
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
                            'ResourceId': security_ou_id,
                            'ResourceType': 'AWS::Organizations::Account',
                            'AccountId': account_id,
                            'CheckedValue': 'IAA Delegated Administrator',
                            'ActualValue': f'OU: {ou_name}, No delegated administrator configured',
                            'Remediation': f'Configure an account from {ou_name} OU as IAA delegated administrator',
                            'Service': self.service,
                            'CheckLogic': self.check_logic,
                            'CheckType': self.check_type
                        }
                        self.findings.append(finding)
                        return self.findings

                    delegated_admin = delegated_admins[0]
                    security_ou_account_ids = [acc['Id'] for acc in security_ou_accounts]

                    if delegated_admin['Id'] not in security_ou_account_ids:
                        finding = {
                            'CheckId': self.check_id,
                            'Status': 'FAIL',
                            'Region': region,
                            "Severity": self.severity,
                            'Title': f"{self.check_id} {self.check_name}",
                            'Description': self.description,
                            'ResourceId': delegated_admin['Id'],
                            'ResourceType': 'AWS::Organizations::Account',
                            'AccountId': account_id,
                            'CheckedValue': f'IAA Delegated Administrator Configuration in {ou_name} OU',
                            'ActualValue': f'OU: {ou_name}, Account: {delegated_admin["Id"]} (not in OU)',
                            'Remediation': f'Configure an account from {ou_name} OU as IAA delegated administrator',
                            'Service': self.service,
                            'CheckLogic': self.check_logic,
                            'CheckType': self.check_type
                        }
                        self.findings.append(finding)
                    else:
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
                            'CheckedValue': f'IAA Delegated Administrator Configuration in {ou_name} OU',
                            'ActualValue': f'OU: {ou_name}, Account: {delegated_admin["Id"]}',
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

            except ClientError as e:
                finding = {
                    'CheckId': self.check_id,
                    'Status': 'ERROR',
                    'Region': region,
                    "Severity": self.severity,
                    'Title': f"{self.check_id} {self.check_name}",
                    'Description': self.description,
                    'ResourceId': account_id,
                    'ResourceType': 'AWS::Organizations::OrganizationalUnit',
                    'AccountId': account_id,
                    'CheckedValue': 'Organizations Structure',
                    'ActualValue': f'Error accessing Organizations structure: {str(e)}',
                    'Remediation': 'Verify Organizations permissions and structure',
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
