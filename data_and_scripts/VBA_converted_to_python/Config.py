import os
import platform
import json
from typing import Dict, Optional, Any
from pathlib import Path
import pandas as pd

class ConfigManager:
    def __init__(self, workbook_path: Optional[str] = None):
        self.workbook_path = workbook_path
        self.is_mac = platform.system() == 'Darwin'
        
    def get_directory_path(self) -> str:
        """Equivalent to GetDirectoryPath() in VBA"""
        if self.workbook_path:
            return os.path.dirname(self.workbook_path)
        return ""
        
    def get_config_file_path(self) -> str:
        """Equivalent to GetConfigFilePath() in VBA"""
        if self.is_mac:
            # Mac paths
            home = os.path.expanduser("~")
            # Check if running in sandbox (Office 15+)
            if os.path.exists(f"{home}/Library/Containers/com.microsoft.Excel"):
                return f"{home}/Library/Containers/com.microsoft.Excel/Data/xlwings.conf"
            else:
                return f"{home}/.xlwings/xlwings.conf"
        else:
            # Windows path
            return os.path.join(os.environ.get('USERPROFILE', ''), '.xlwings', 'xlwings.conf')
            
    def get_directory_config_file_path(self) -> str:
        """Equivalent to GetDirectoryConfigFilePath() in VBA"""
        separator = '/' if self.is_mac else '\\'
        return f"{self.get_directory_path()}{separator}xlwings.conf"
        
    def get_config_from_sheet(self, worksheet) -> Dict[str, str]:
        """Equivalent to GetConfigFromSheet() in VBA"""
        config_dict = {}
        
        # Read configuration from worksheet
        if worksheet is not None:
            df = pd.read_excel(worksheet, usecols=[0, 1], header=None)
            for _, row in df.iterrows():
                if pd.notna(row[0]):  # Check if key is not empty
                    config_dict[row[0].upper()] = str(row[1]) if pd.notna(row[1]) else ""
                    
        return config_dict
        
    def save_config_to_file(self, filename: str, name: str, value: Optional[str] = None) -> bool:
        """Equivalent to SaveConfigToFile() in VBA"""
        try:
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            config_dict = {}
            # Read existing config if file exists
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    try:
                        config_dict = json.load(f)
                    except json.JSONDecodeError:
                        pass
                        
            # Update or add new value
            config_dict[name] = value
            
            # Write updated config
            with open(filename, 'w') as f:
                json.dump(config_dict, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
            
    def get_config_from_file(self, filename: str, name: str) -> Optional[str]:
        """Equivalent to GetConfigFromFile() in VBA"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    config_dict = json.load(f)
                    return config_dict.get(name)
            return None
            
        except Exception as e:
            print(f"Error reading config: {e}")
            return None
            
    def get_config(self, config_key: str, default: str = "") -> str:
        """Equivalent to GetConfig() in VBA"""
        config_value = ""
        
        # Try getting config from worksheet if available
        if hasattr(self, 'workbook') and 'xlwings.conf' in self.workbook.sheetnames:
            sheet_config = self.get_config_from_sheet(self.workbook['xlwings.conf'])
            config_value = sheet_config.get(config_key.upper(), "")
            
        # Try directory config file
        if not config_value:
            dir_config_path = self.get_directory_config_file_path()
            if os.path.exists(dir_config_path):
                config_value = self.get_config_from_file(dir_config_path, config_key) or ""
                
        # Try global config file
        if not config_value:
            global_config_path = self.get_config_file_path()
            if os.path.exists(global_config_path):
                config_value = self.get_config_from_file(global_config_path, config_key) or ""
                
        # Use default if still no value
        if not config_value:
            config_value = default
            
        # Expand environment variables
        return os.path.expandvars(config_value)

def example_usage():
    # Initialize config manager
    config_manager = ConfigManager("path/to/workbook.xlsx")
    
    # Get configuration value
    python_path = config_manager.get_config("PYTHON_PATH", default="python")
    print(f"Python Path: {python_path}")
    
    # Save configuration
    success = config_manager.save_config_to_file(
        "path/to/config.json",
        "PYTHON_PATH",
        "/usr/local/bin/python3"
    )
    print(f"Config saved successfully: {success}")

if __name__ == "__main__":
    example_usage()