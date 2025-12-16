from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError
import logging
from sraverify.lib.check_loader import SecurityCheck

class SRACONFIG1(SecurityCheck):
    """SRA-CONFIG-1: AWS Config recorder configuration check"""
    
    def __init__(self, check_type="account"):
        """Initialize the check with account type"""
        super().__init__(check_type=check_type)
        self.check_id = "SRA-CONFIG-1"
        self.check_name = "AWS Config recorder is configured in this region"
        self.description = ('This check verifies that a configuration recorders exists in the AWS Region. '
                          'AWS Config uses the configuration recorder to detect changes in your resource '
                          'configurations and capture these changes as configuration items. You must create '
                          'a configuration recorder in every AWS Region for AWS Config can track your '
                          'resource configurations in the region.')
        self.service = "Config"
        self.severity = "HIGH"
        self.check_type = check_type
        self.check_logic = ('1. List Config recorders in current region | '
                          '2. Verify at least one recorder exists | '
                          '3. Check recorder configuration status')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings = []
        self._regions = None

    def initialize(self, regions: Optional[List[str]] = None):
        """Initialize check with optional regions"""
        self._regions = regions

    def get_findings(self) -> List[Dict[str, Any]]:
        """Return the findings"""
        return self.findings

    def _create_finding(self, status: str, region: str, account_id: str,
                       resource_id: str, actual_value: str,
                       remediation: str) -> Dict[str, Any]:
        """Create a standardized finding"""
        return {
            "CheckId": self.check_id,
            "Status": status,
            "Region": region,
            "Severity": self.severity,
            "Title": f"{self.check_id} {self.check_name}",
            "Description": self.description,
            "ResourceId": resource_id,
            "ResourceType": "AWS::Config::ConfigurationRecorder",
            "AccountId": account_id,
            "CheckedValue": "Configuration Recorder Status",
            "ActualValue": actual_value,
            "Remediation": remediation,
            "Service": self.service,
            "CheckLogic": self.check_logic,
            "CheckType": self.check_type
        }

    def check_recorder_status(self, config_client, recorder_name: str) -> tuple:
        """Check Config recorder status and return details"""
        try:
            status = config_client.describe_configuration_recorder_status(
                ConfigurationRecorderNames=[recorder_name]
            )
            if status['ConfigurationRecordersStatus']:
                recorder_status = status['ConfigurationRecordersStatus'][0]
                return (
                    recorder_status.get('recording', False),
                    recorder_status.get('lastStatus', 'ERROR'),
                    recorder_status.get('lastErrorCode', ''),
                    recorder_status.get('lastErrorMessage', '')
                )
            return False, 'ERROR', 'NO_STATUS', 'No recorder status found'
            
        except ClientError as e:
            self.logger.error(f"Error getting recorder status for {recorder_name}: {str(e)}")
            return False, 'ERROR', str(e), 'Error getting recorder status'

    def _check_region(self, session, region: str) -> Optional[Dict[str, Any]]:
        """Check Config configuration in a specific region"""
        try:
            account_id = session.client('sts').get_caller_identity()['Account']
            self.logger.debug(f"Checking region: {region}")
            
            # Initialize Config client for the specific region
            config_client = session.client('config', region_name=region)
            
            try:
                # List configuration recorders
                recorders = config_client.describe_configuration_recorders()
                if not recorders['ConfigurationRecorders']:
                    return self._create_finding(
                        status="FAIL",
                        region=region,
                        account_id=account_id,
                        resource_id="config-recorder",
                        actual_value="No configuration recorder found in region",
                        remediation="Create a configuration recorder in this region"
                    )

                # Check each recorder's status
                valid_recorder = None
                for recorder in recorders['ConfigurationRecorders']:
                    recorder_name = recorder['name']
                    is_recording, last_status, error_code, error_message = self.check_recorder_status(
                        config_client, 
                        recorder_name
                    )
                    
                    if is_recording and last_status == 'SUCCESS':
                        valid_recorder = recorder
                        self.logger.debug(f"Found active recorder: {recorder_name}")
                        break

                if valid_recorder:
                    return self._create_finding(
                        status="PASS",
                        region=region,
                        account_id=account_id,
                        resource_id=valid_recorder['name'],
                        actual_value=f"Configuration recorder {valid_recorder['name']} is active and recording",
                        remediation="None required"
                    )
                else:
                    recorder = recorders['ConfigurationRecorders'][0]
                    actual_value = f"Configuration recorder {recorder['name']} exists but "
                    if not is_recording:
                        actual_value += "is not recording"
                    else:
                        actual_value += f"has status: {last_status}"
                        if error_code:
                            actual_value += f" (Error: {error_code} - {error_message})"

                    return self._create_finding(
                        status="FAIL",
                        region=region,
                        account_id=account_id,
                        resource_id=recorder['name'],
                        actual_value=actual_value,
                        remediation="Start the configuration recorder or fix configuration errors"
                    )

            except ClientError as e:
                return self._create_finding(
                    status="ERROR",
                    region=region,
                    account_id=account_id,
                    resource_id="config",
                    actual_value=f"Error accessing Config: {str(e)}",
                    remediation="Verify Config permissions"
                )

        except Exception as e:
            return self._create_finding(
                status="ERROR",
                region=region,
                account_id="Unknown",
                resource_id="check-execution",
                actual_value=f"Error: {str(e)}",
                remediation="Check logs for more details"
            )

    def run(self, session) -> None:
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
                            status="ERROR",
                            region=region,
                            account_id="Unknown",
                            resource_id="Unknown",
                            actual_value=f"Region check failed: {str(e)}",
                            remediation="Check regional access and permissions"
                        )
                    )

        except Exception as e:
            self.findings.append(
                self._create_finding(
                    status="ERROR",
                    region="Unknown",
                    account_id="Unknown",
                    resource_id="Unknown",
                    actual_value=f"Check execution failed: {str(e)}",
                    remediation="Check logs for more details"
                )
            )
