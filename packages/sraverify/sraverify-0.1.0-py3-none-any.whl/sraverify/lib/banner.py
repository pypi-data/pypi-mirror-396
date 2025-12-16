from colorama import Fore, Style
import datetime
import os
import boto3

def print_banner(profile: str, region: str, session: boto3.Session = None):
    """Print the SRAVerify banner and initial execution information."""
    # ASCII art banner with version
    print(f"""
                    _____ _____         ___       ___        _  __       
                   / ____|  __ \     /\ \  \     /  /       (_)/ _|      
                  | (___ | |__) |   /  \ \  \   /  /__  _ __ _| |_ _   _ 
                   \___ \|  _  /   / /\ \ \   v   / _ \| '__| |  _| | | |
                   ____) | | \ \  / ____ \ \     /  __/| |  | | | | |_| |
                  |_____/|_|  \_\/_/    \_\ \___/ \___||_|  |_|_|  \__, |
                                                                   __/ |
                                                                  |___/ {Fore.BLUE}
                                     the security architecture verifier tool{Style.RESET_ALL}
    """)

    print(f"{Fore.YELLOW}Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")

    # Print AWS credentials information
    print("-> Using the AWS credentials below:")
    print(f"  · AWS-CLI Profile: {profile}")
    print(f"  · AWS Region: {region}")
    
    if session:
        try:
            sts = session.client('sts')
            caller_identity = sts.get_caller_identity()
            print(f"  · AWS Account: {caller_identity['Account']}")
            print(f"  · User Id: {caller_identity['UserId']}")
            print(f"  · Caller Identity ARN: {caller_identity['Arn']}")
        except Exception as e:
            print(f"  · Unable to retrieve identity information: {str(e)}")
    
    print("\n-> Using the following configuration:")
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    print(f"  · Config File: {os.path.join(config_dir, 'config.yaml')}")
    print(f"  · Mutelist File: {os.path.join(config_dir, 'mutelist.yaml')}")
    print("  · Scanning unused services and resources: False\n")