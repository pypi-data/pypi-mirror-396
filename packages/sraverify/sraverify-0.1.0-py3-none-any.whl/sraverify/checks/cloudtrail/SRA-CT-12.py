from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError
import logging

class SRACT12(SecurityCheck):
    """SRA-CT-12: CloudTrail Delegated Administrator Configuration"""
    
    def __init__(self, check_type="organization"):
        """Initialize the check with organization type"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CT-12"
        self.check_name = "Delegated Administrator set for CloudTrail"
        self.description = ('This check verifies whether CloudTrail service administration for the AWS Organization '
                          'is delegated out to AWS Organization management account. The delegated administrator has '
                          'permissions to create and manage analyzers with the AWS organization as the zone of trust.')
        self.service = "CloudTrail"
        self.severity = "MEDIUM"
        self.check_type = check_type
        self.check_logic = ('1. Verify execution from Organization Management Account | '
                          '2. Get management account ID from Organizations | '
                          '3. List CloudTrail delegated administrators | '
                          '4. Check passes if at least one delegated administrator is configured')
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
                # Step 2: Get management account ID from Organizations
                organizations_client = session.client('organizations')
                
                # Step 3: List CloudTrail delegated administrators
                try:
                    delegated_admins = organizations_client.list_delegated_administrators(
                        ServicePrincipal='cloudtrail.amazonaws.com'
                    )
                    admin_accounts = delegated_admins.get('DelegatedAdministrators', [])
                    
                    # Step 4: Check if at least one delegated administrator is configured
                    if admin_accounts:
                        # Format account list for actual value
                        admin_list = ', '.join([f"{admin['Id']}" for admin in admin_accounts])
                        status = "PASS"
                        actual_value = f"CloudTrail delegated administrators configured: {admin_list}"
                        remediation = "None required"
                    else:
                        status = "FAIL"
                        actual_value = "No CloudTrail delegated administrators configured"
                        remediation = "Configure at least one delegated administrator for CloudTrail using the CloudTrail console or AWS CLI"
                    
                    self.findings.append({
                        "CheckId": self.check_id,
                        "Status": status,
                        "Region": region,
                        "Severity": self.severity,
                        "Title": f"{self.check_id} {self.check_name}",
                        "Description": self.description,
                        "ResourceId": "cloudtrail-delegated-admin",
                        "ResourceType": "AWS::Organizations::Account",
                        "AccountId": account_id,
                        "CheckedValue": "Delegated Administrator Configuration",
                        "ActualValue": actual_value,
                        "Remediation": remediation,
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
                "ResourceType": "AWS::CloudTrail::Trail",
                "AccountId": account_id if 'account_id' in locals() else "unknown",
                "CheckedValue": "Check Execution",
                "ActualValue": f"Unexpected error: {str(e)}",
                "Remediation": "Contact support team",
                "Service": self.service,
                "CheckLogic": self.check_logic,
                "CheckType": self.check_type
            })
