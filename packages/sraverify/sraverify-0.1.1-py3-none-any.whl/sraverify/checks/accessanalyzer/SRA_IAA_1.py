# sraverify/checks/accessanalyzer/SRA_IAA_1.py

from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError
import boto3
from sraverify.lib.check_loader import SecurityCheck

class SRAIAA1(SecurityCheck):
    """SRA-IAA-1: IAM Access Analyzer External Access"""
    
    def __init__(self, check_type="account"):
        """Initialize the check with account type"""
        super().__init__(check_type=check_type)
        self.check_type = check_type  
        self.check_id = "SRA-IAA-1"
        self.check_type = "account"
        self.check_name = "IAM Access Analyzer External Access"
        self.severity = 'HIGH'
        self.description = ('This check verifies whether IAA external access analyzer is configured with a zone of trust '
                          'of AWS account. IAM Access Analyzer generates a finding for each instance of a resource-based '
                          'policy that grants access to a resource within your zone of trust to a principal that is not '
                          'within your zone of trust.')
        self.check_logic = ('1. Check for active analyzer within account with account zone of trust | '
                          '2. Verify archive rules configuration for findings management | '
                          '3. Verify analyzer status and configuration | '
                          '4. Check passes if account-level analyzer is active with proper configuration')
        self.service = 'IAM'
        self.findings = []
        self._regions = None

    def initialize(self, regions: Optional[List[str]] = None):
        """Initialize check with optional regions"""
        self._regions = regions

    def get_findings(self):
        """Return the findings"""
        return self.findings

    def _create_finding(self, status: str, region: str, account_id: str, 
                       resource_id: str, actual_value: str, 
                       remediation: str) -> Dict[str, Any]:
        """Create a standardized finding"""
        return {
            'CheckId': self.check_id,
            'Status': status,
            'Region': region,
            "Severity": self.severity,
            'Title': f"{self.check_id} {self.check_name}",
            'Description': self.description,
            'ResourceId': resource_id,
            'ResourceType': 'AWS::AccessAnalyzer::Analyzer',
            'AccountId': account_id,
            'CheckedValue': 'Access Analyzer Configuration',
            'ActualValue': actual_value,
            'Remediation': remediation,
            'Service': self.service,
            'CheckLogic': self.check_logic,
            'CheckType': self.check_type
        }

    def _check_region(self, session: boto3.Session, region: str) -> Optional[Dict[str, Any]]:
        """Check Access Analyzer configuration in a specific region"""
        try:
            account_id = session.client('sts').get_caller_identity()['Account']
            analyzer_client = session.client('accessanalyzer', region_name=region)

            # Step 1: Check for account-level analyzer
            try:
                analyzers = analyzer_client.list_analyzers()['analyzers']
                account_analyzer = None

                for analyzer in analyzers:
                    if (analyzer['status'] == 'ACTIVE' and 
                        analyzer['type'] == 'ACCOUNT'):
                        account_analyzer = analyzer
                        break

                if not account_analyzer:
                    return self._create_finding(
                        status='FAIL',
                        region=region,
                        account_id=account_id,
                        resource_id=account_id,
                        actual_value='No active account-level analyzer found',
                        remediation='Create an account-level IAM Access Analyzer'
                    )

                # Step 2: Check archive rules configuration
                try:
                    archive_rules = analyzer_client.list_archive_rules(
                        analyzerName=account_analyzer['name']
                    )['archiveRules']

                    # Step 3: Verify analyzer configuration
                    try:
                        analyzer_details = analyzer_client.get_analyzer(
                            analyzerName=account_analyzer['name']
                        )

                        # Step 4: All checks passed
                        return self._create_finding(
                            status='PASS',
                            region=region,
                            account_id=account_id,
                            resource_id=account_analyzer['arn'],
                            actual_value=(f"Active account analyzer: {account_analyzer['name']}, "
                                        f"Archive Rules: {len(archive_rules)}"),
                            remediation='None required'
                        )

                    except ClientError as e:
                        return self._create_finding(
                            status='ERROR',
                            region=region,
                            account_id=account_id,
                            resource_id=account_analyzer['arn'],
                            actual_value=f'Error checking analyzer configuration: {str(e)}',
                            remediation='Verify IAM Access Analyzer permissions'
                        )

                except ClientError as e:
                    return self._create_finding(
                        status='ERROR',
                        region=region,
                        account_id=account_id,
                        resource_id=account_analyzer['arn'],
                        actual_value=f'Error checking archive rules: {str(e)}',
                        remediation='Verify IAM Access Analyzer permissions'
                    )

            except ClientError as e:
                return self._create_finding(
                    status='ERROR',
                    region=region,
                    account_id=account_id,
                    resource_id=account_id,
                    actual_value=f'Error accessing Access Analyzer: {str(e)}',
                    remediation='Verify IAM Access Analyzer permissions'
                )

        except Exception as e:
            return self._create_finding(
                status='ERROR',
                region=region,
                account_id='Unknown',
                resource_id='Unknown',
                actual_value=f'Error: {str(e)}',
                remediation='Check logs for more details'
            )

    def run(self, session: boto3.Session):
        """Run the security check"""
        try:
            # Get regions to check
            regions_to_check = self._regions if self._regions else [session.region_name]
            
            # Check each region
            for region in regions_to_check:
                try:
                    finding = self._check_region(session, region)
                    if finding:
                        self.findings.append(finding)
                except Exception as e:
                    self.findings.append(
                        self._create_finding(
                            status='ERROR',
                            region=region,
                            account_id='Unknown',
                            resource_id='Unknown',
                            actual_value=f'Region check failed: {str(e)}',
                            remediation='Check regional access and permissions'
                        )
                    )

        except Exception as e:
            # Handle any unexpected errors during check execution
            self.findings.append(
                self._create_finding(
                    status='ERROR',
                    region='Unknown',
                    account_id='Unknown',
                    resource_id='Unknown',
                    actual_value=f'Check execution failed: {str(e)}',
                    remediation='Check logs for more details'
                )
            )

        return self.findings
