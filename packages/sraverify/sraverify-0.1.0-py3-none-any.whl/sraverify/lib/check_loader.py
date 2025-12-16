# sraverify/lib/check_loader.py

import os
import importlib.util
from typing import List, Type, Dict
from sraverify.checks import SecurityCheck

def discover_checks(check_type: str = "all", debug: bool = False, security_ou_name: str = None) -> List[Type[SecurityCheck]]:
    """
    Discover and load all security check classes.
    
    Args:
        check_type: Type of check to run ("all", "account" or "organization")
        debug: Whether to print debug information
        security_ou_name: Optional name of security OU to search for
    
    Returns:
        List of security check classes
    """
    check_classes = []
    checks_dir = os.path.join(os.path.dirname(__file__), '..', 'checks')
    
    # Keep track of loaded check IDs to avoid duplicates
    loaded_check_ids = set()
    
    for root, _, files in os.walk(checks_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                
                try:
                    # Import the module
                    spec = importlib.util.spec_from_file_location(
                        f"sraverify.checks.{file[:-3]}", 
                        file_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find security check classes in the module
                        for item_name in dir(module):
                            item = getattr(module, item_name)
                            if (isinstance(item, type) and 
                                issubclass(item, SecurityCheck) and 
                                item != SecurityCheck):
                                
                                # Create an instance to check its type
                                check_instance = item()
                                
                                check_id = getattr(check_instance, 'check_id', None)
                                instance_check_type = getattr(check_instance, 'check_type', 'account')
                                
                                # Skip if we've already loaded this check
                                if check_id in loaded_check_ids:
                                    continue
                                
                                # Filter based on check_type parameter
                                if check_type != "all" and instance_check_type != check_type:
                                    if debug:
                                        print(f"Debug: Skipping {check_id} (type: {instance_check_type}) - not matching requested type: {check_type}")
                                    continue
                                
                                loaded_check_ids.add(check_id)
                                check_classes.append(item)
                                
                                if debug:
                                    print(f"Debug: Loaded check {check_id} (type: {instance_check_type}) from {file}")
                                
                except Exception as e:
                    if debug:
                        print(f"Debug: Error loading {file}: {str(e)}")
                    continue
    
    if debug:
        print(f"\nDebug: Total checks loaded: {len(check_classes)}")
        if check_type != "all":
            print(f"Debug: Filtered for check_type: {check_type}")
    
    return check_classes
