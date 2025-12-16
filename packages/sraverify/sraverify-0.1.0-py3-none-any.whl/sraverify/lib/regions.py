# sraverify/lib/regions.py
from typing import List, Optional
import boto3

def get_enabled_regions(session: boto3.Session) -> List[str]:
    """Get all enabled regions in the AWS account"""
    try:
        ec2_client = session.client('ec2', region_name='us-east-1')
        response = ec2_client.describe_regions(AllRegions=False)
        return [region['RegionName'] for region in response['Regions']]
    except Exception as e:
        raise Exception(f"Failed to get enabled regions: {str(e)}")

def validate_regions(regions: List[str], session: boto3.Session) -> List[str]:
    """Validate if specified regions are valid and enabled"""
    try:
        enabled_regions = set(get_enabled_regions(session))
        
        if regions:
            invalid_regions = set(regions) - enabled_regions
            if invalid_regions:
                raise ValueError(f"Invalid or disabled regions: {', '.join(invalid_regions)}")
            return regions
        
        return list(enabled_regions)
    except Exception as e:
        raise Exception(f"Failed to validate regions: {str(e)}")
