# sraverify/lib/session.py
import boto3
from typing import Optional

def get_session(region: Optional[str] = None, profile: Optional[str] = None) -> boto3.Session:
    """Get AWS session with optional region and profile"""
    try:
        return boto3.Session(region_name=region, profile_name=profile)
    except Exception as e:
        raise Exception(f"Failed to create AWS session: {str(e)}")

def get_regional_session(base_session: boto3.Session, region: str) -> boto3.Session:
    """Create a new session for a specific region while maintaining credentials"""
    try:
        credentials = base_session.get_credentials()
        return boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_session_token=credentials.token,
            region_name=region
        )
    except Exception as e:
        raise Exception(f"Failed to create regional session: {str(e)}")
