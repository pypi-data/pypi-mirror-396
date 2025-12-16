from typing import Dict, List, Any
from sraverify.checks import SecurityCheck
from botocore.exceptions import ClientError

class SRAIAA4(SecurityCheck):
    """SRA-IAA-4: IAM Access Analyzer Organization Zone of Trust"""
    
    def __init__(self, check_type="organization"):
        super().__init__(check_type=check_type)
        self.check_id = "SRA-IAA-4"
        self.check_name = "IAM Access Analyzer Organization Zone of Trust"
        self.severity = "HIGH"
        self.description = ('This check verifies whether IAA external access analyzer is configured with a zone of trust '
                          'of your AWS organization. IAM Access Analyzer generates a finding for each instance of a '
                          'resource-based policy that grants access to a resource within your zone of trust to a principal '
                          'that is not within your zone of trust. When you configure an organization as the zone of trust '
                          'for an analyzer- IAA generates findings or each instance of a resource-based policy that grants '
                          'access to a resource within your AWS organization to a principal that is not within your AWS '
                          'organization.')
        self.check_logic = ('1. Verify execution from Organization Management account  | '
                          '2. List IAM Access Analyzers in current region | '
                          '3. Check for analyzer with type=ORGANIZATION and status=ACTIVE | '
                          '4. Verify IAM Analyzer configuration has Organization scope | '
                          '5. Check passes if organization-level analyzer is properly configured')
        self.service = 'IAM'

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
            analyzer_client = session.client('accessanalyzer')

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

            # Steps 2 & 3: Check for organization-level analyzer
            try:
                analyzers = analyzer_client.list_analyzers()['analyzers']
                org_analyzer = None
                account_analyzers = []

                for analyzer in analyzers:
                    if analyzer['type'] == 'ORGANIZATION' and analyzer['status'] == 'ACTIVE':
                        org_analyzer = analyzer
                        break
                    elif analyzer['type'] == 'ACCOUNT':
                        account_analyzers.append(analyzer['name'])

                if not org_analyzer:
                    failure_details = []
                    if not analyzers:
                        failure_details.append("No analyzers found in the region")
                    if account_analyzers:
                        failure_details.append(f"Found account-level analyzers instead of organization-level: {', '.join(account_analyzers)}")
                    
                    self.findings.append({
                        'CheckId': self.check_id,
                        'Status': 'FAIL',
                        'Region': region,
                        "Severity": self.severity,
                        'Title': f"{self.check_id} {self.check_name}",
                        'Description': self.description,
                        'ResourceId': account_id,
                        'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
                        'AccountId': account_id,
                        'CheckedValue': 'Organization-level Access Analyzer',
                        'ActualValue': ' | '.join(failure_details) if failure_details else 'No active organization-level analyzer found',
                        'Remediation': 'Create an active organization-level IAM Access Analyzer in this region',
                        'Service': self.service,
                        'CheckLogic': self.check_logic,
                        'CheckType': self.check_type
                    })
                    return self.findings

                # Step 4: Verify analyzer configuration
                try:
                    analyzer_details = analyzer_client.get_analyzer(
                        analyzerName=org_analyzer['name']
                    )['analyzer']

                    # Verify organization scope
                    if analyzer_details.get('type') != 'ORGANIZATION':
                        self.findings.append({
                            'CheckId': self.check_id,
                            'Status': 'FAIL',
                            'Region': region,
                            "Severity": self.severity,
                            'Title': f"{self.check_id} {self.check_name}",
                            'Description': self.description,
                            'ResourceId': org_analyzer['arn'],
                            'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
                            'AccountId': account_id,
                            'CheckedValue': 'Analyzer Organization Scope',
                            'ActualValue': f"Analyzer type is {analyzer_details.get('type')} instead of ORGANIZATION",
                            'Remediation': 'Reconfigure analyzer with organization scope or create new organization-level analyzer',
                            'Service': self.service,
                            'CheckLogic': self.check_logic,
                            'CheckType': self.check_type
                        })
                    else:
                        # Step 5: All checks passed
                        self.findings.append({
                            'CheckId': self.check_id,
                            'Status': 'PASS',
                            'Region': region,
                            "Severity": self.severity,
                            'Title': f"{self.check_id} {self.check_name}",
                            'Description': self.description,
                            'ResourceId': org_analyzer['arn'],
                            'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
                            'AccountId': account_id,
                            'CheckedValue': 'Organization-level Access Analyzer Configuration',
                            'ActualValue': (f"Active organization analyzer: {org_analyzer['name']} | "
                                        f"Type: {analyzer_details['type']} | "
                                        f"Status: {analyzer_details['status']}"),
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
                        'ResourceId': org_analyzer['arn'],
                        'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
                        'AccountId': account_id,
                        'CheckedValue': 'Analyzer Configuration',
                        'ActualValue': f'Error checking analyzer configuration: {str(e)}',
                        'Remediation': 'Verify IAM Access Analyzer permissions',
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
                    'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
                    'AccountId': account_id,
                    'CheckedValue': 'Access Analyzer Access',
                    'ActualValue': f'Error accessing Access Analyzer: {str(e)}',
                    'Remediation': 'Verify IAM Access Analyzer permissions and service availability',
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
                'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
                'AccountId': account_id,
                'CheckedValue': 'Check Execution',
                'ActualValue': f'Error: {str(e)}',
                'Remediation': 'Review error logs and verify AWS credentials and permissions',
                'Service': self.service,
                'CheckLogic': self.check_logic,
                'CheckType': self.check_type
            })
            
        return self.findings
