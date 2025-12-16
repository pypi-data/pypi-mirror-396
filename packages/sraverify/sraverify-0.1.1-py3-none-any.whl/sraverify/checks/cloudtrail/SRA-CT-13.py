from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
import logging

class SRACT13(SecurityCheck):
    """SRA-CT-13: Security Tooling Account CloudTrail Delegated Administrator"""
    
    def __init__(self, check_type="organization", security_ou_name=None):
        """Initialize the check with organization type and optional security OU name"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-13"
        self.check_name = "The Security Tooling Account is the Delegated Administrator set for CloudTrail"
        self.description = ('This check verifies whether CloudTrail delegated admin account is the security tooling account '
                          'of your AWS organization. Security Tooling account is dedicated to operating security services, '
                          'monitoring AWS accounts, and automating security alerting and response. CloudTrail helps monitor '
                          'API activities across all your AWS accounts and regions.')
        self.service = "CloudTrail"
        self.severity = "HIGH"
        self.check_type = check_type
        self.check_logic = ('1. Verify execution from Organization Management Account | '
                          '2. List all Organization Units and find specified OU (via flag --security-ou-name) or OU containing "security" | '
                          '3. List accounts in Security OU | '
                          '4. List CloudTrail delegated administrators | '
                          '5. Verify delegated admin account exists in Security OU')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings = []
        self.security_ou_name = security_ou_name.lower() if security_ou_name else None

    def get_findings(self) -> List[Dict[str, Any]]:
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

    def get_accounts_in_ou(self, organizations_client, ou_id: str) -> List[str]:
        """Get list of account IDs in the specified OU"""
        try:
            account_ids = []
            paginator = organizations_client.get_paginator('list_accounts_for_parent')
            
            for page in paginator.paginate(ParentId=ou_id):
                for account in page['Accounts']:
                    account_ids.append(account['Id'])
            
            return account_ids
            
        except ClientError as e:
            self.logger.error(f"Error listing accounts in OU: {str(e)}")
            return []

    def run(self, session) -> None:
        """Run the security check"""
        try:
            # Get account information
            sts_client = session.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            region = session.region_name
            self.logger.debug(f"Running check for account: {account_id} in region: {region}")
            
            # Step 1: Verify execution from Organization Management Account
            is_management, error_message = self.org_checker.verify_org_management()
            if not is_management:
                self.findings.append({
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
                })
                return self.findings
            
            try:
                # Initialize Organizations client
                organizations_client = session.client('organizations')
                
                # Step 2: List all Organization Units and find Security OU
                root_id = organizations_client.list_roots()['Roots'][0]['Id']
                security_ou_id, security_ou_name, search_term = self.find_security_ou(organizations_client, root_id)
                
                if not security_ou_id:
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "ERROR",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": "security-ou",
                        "ResourceType": "AWS::Organizations::OrganizationalUnit",
                        "AccountId": account_id,
                        "CheckedValue": "Security OU Existence",
                        "ActualValue": f"No OU found matching search term: {search_term}",
                        "Remediation": "Verify Security OU name or existence of OU containing 'security'",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return

                # Step 3: List accounts in Security OU
                security_accounts = self.get_accounts_in_ou(organizations_client, security_ou_id)
                if not security_accounts:
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": "FAIL",
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": security_ou_id,
                        "ResourceType": "AWS::Organizations::OrganizationalUnit",
                        "AccountId": account_id,
                        "CheckedValue": "Security OU Accounts",
                        "ActualValue": f"No accounts found in Security OU: {security_ou_name}",
                        "Remediation": "Verify Security OU configuration and account assignments",
                        "Service": self.service,
                        "CheckLogic": self.check_logic,
                        "CheckType": self.check_type
                    })
                    return

                # Step 4: List CloudTrail delegated administrators
                try:
                    delegated_admins = organizations_client.list_delegated_administrators(
                        ServicePrincipal='cloudtrail.amazonaws.com'
                    )
                    admin_accounts = delegated_admins.get('DelegatedAdministrators', [])
                    
                    if not admin_accounts:
                        self.findings.append({
                            "CheckId": self.check_id,
                            "Status": "FAIL",
                            "Region": region,
                            "Severity": self.severity,
                            "Title": f"{self.check_id} {self.check_name}",
                            "Description": self.description,
                            "ResourceId": "cloudtrail-delegated-admin",
                            "ResourceType": "AWS::Organizations::Account",
                            "AccountId": account_id,
                            "CheckedValue": "Delegated Administrator Configuration",
                            "ActualValue": "No CloudTrail delegated administrators configured",
                            "Remediation": "Configure a Security Tooling account as CloudTrail delegated administrator",
                            "Service": self.service,
                            "CheckLogic": self.check_logic,
                            "CheckType": self.check_type
                        })
                        return

                    # Step 5: Verify delegated admin account exists in Security OU
                    valid_admin = None
                    for admin in admin_accounts:
                        if admin['Id'] in security_accounts:
                            valid_admin = admin
                            break

                    if valid_admin:
                        self.findings.append({
                            "CheckId": self.check_id,
                            "Status": "PASS",
                            "Region": region,
                            "Severity": self.severity,
                            "Title": f"{self.check_id} {self.check_name}",
                            "Description": self.description,
                            "ResourceId": valid_admin['Id'],
                            "ResourceType": "AWS::Organizations::Account",
                            "AccountId": account_id,
                            "CheckedValue": "CloudTrail Delegated Administrator",
                            "ActualValue": f"CloudTrail delegated administrator {valid_admin['Id']} is in Security OU {security_ou_name}",
                            "Remediation": "None required",
                            "Service": self.service,
                            "CheckLogic": self.check_logic,
                            "CheckType": self.check_type
                        })
                    else:
                        admin_list = ', '.join([admin['Id'] for admin in admin_accounts])
                        self.findings.append({
                            "CheckId": self.check_id,
                            "Status": "FAIL",
                            "Region": region,
                            "Severity": self.severity,
                            "Title": f"{self.check_id} {self.check_name}",
                            "Description": self.description,
                            "ResourceId": "cloudtrail-delegated-admin",
                            "ResourceType": "AWS::Organizations::Account",
                            "AccountId": account_id,
                            "CheckedValue": "CloudTrail Delegated Administrator",
                            "ActualValue": f"CloudTrail delegated administrators ({admin_list}) are not in Security OU {security_ou_name}",
                            "Remediation": f"Configure a Security Tooling account from Security OU {security_ou_name} as CloudTrail delegated administrator",
                            "Service": self.service,
                            "CheckLogic": self.check_logic,
                            "CheckType": self.check_type
                        })

                except ClientError as e:
                    if 'AccessDeniedException' in str(e):
                        self.findings.append({
                            "CheckId": self.check_id,
                            "Status": "ERROR",
                            "Region": region,
                            "Severity": self.severity,
                            "Title": f"{self.check_id} {self.check_name}",
                            "Description": self.description,
                            "ResourceId": "organizations-permissions",
                            "ResourceType": "AWS::Organizations::Account",
                            "AccountId": account_id,
                            "CheckedValue": "Organizations Permissions",
                            "ActualValue": "Insufficient permissions to list delegated administrators",
                            "Remediation": "Verify Organizations permissions in management account",
                            "Service": self.service,
                            "CheckLogic": self.check_logic,
                            "CheckType": self.check_type
                        })
                    else:
                        raise e

            except ClientError as e:
                self.logger.error(f"Error accessing Organizations: {str(e)}")
                self.findings.append({
                    "CheckId": self.check_id,
                    "Status": "ERROR",
                    "Region": region,
                    "Severity": self.severity,
                    "Title": f"{self.check_id} {self.check_name}",
                    "Description": self.description,
                    "ResourceId": "organizations",
                    "ResourceType": "AWS::Organizations::Account",
                    "AccountId": account_id,
                    "CheckedValue": "Organizations API Access",
                    "ActualValue": f"Error accessing Organizations: {str(e)}",
                    "Remediation": "Verify Organizations permissions",
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
                "ResourceType": "AWS::Organizations::Account",
                "AccountId": account_id if 'account_id' in locals() else "unknown",
                "CheckedValue": "Check Execution",
                "ActualValue": f"Unexpected error: {str(e)}",
                "Remediation": "Contact support team",
                "Service": self.service,
                "CheckLogic": self.check_logic,
                "CheckType": self.check_type
            })
