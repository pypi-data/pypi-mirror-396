"""Organization Management Account Checker"""

from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError
import logging

class OrgMgmtChecker:
    """Singleton class to check and cache organization management account status"""
    
    _instance = None
    _initialized = False
    _is_org_management = False
    _management_account_id = None
    _current_account_id = None
    _error_message = None
    _logger = logging.getLogger(__name__)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OrgMgmtChecker, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

    def initialize(self, session: boto3.Session) -> None:
        """Initialize the checker with a session"""
        try:
            # Get current account ID
            sts_client = session.client('sts')
            self._current_account_id = sts_client.get_caller_identity()['Account']
            
            # Get organization details
            org_client = session.client('organizations')
            try:
                org_details = org_client.describe_organization()['Organization']
                self._management_account_id = org_details.get('MasterAccountId')  # For older API versions
                if not self._management_account_id:
                    self._management_account_id = org_details.get('ManagementAccountId')  # For newer API versions
                
                # Check if current account is management account
                self._is_org_management = self._current_account_id == self._management_account_id
                self._error_message = None
                
                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.debug(f"Current Account: {self._current_account_id}")
                    self._logger.debug(f"Management Account: {self._management_account_id}")
                    self._logger.debug(f"Is Management: {self._is_org_management}")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AWSOrganizationsNotInUseException':
                    self._error_message = "AWS Organizations is not in use for this account"
                else:
                    self._error_message = f"Organizations API error: {str(e)}"
                self._is_org_management = False
                self._management_account_id = None
                
        except Exception as e:
            self._error_message = str(e)
            self._is_org_management = False
            self._management_account_id = None
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(f"Error during initialization: {str(e)}")

    def verify_org_management(self) -> Tuple[bool, Optional[str]]:
        """
        Verify if current account is organization management account
        Returns: (is_management_account, error_message)
        """
        return self._is_org_management, self._error_message

    def get_management_account_id(self) -> Optional[str]:
        """Get the management account ID if available"""
        return self._management_account_id

    def get_current_account_id(self) -> Optional[str]:
        """Get the current account ID"""
        return self._current_account_id

    @property
    def is_initialized(self) -> bool:
        """Check if the checker has been initialized"""
        return self._initialized
