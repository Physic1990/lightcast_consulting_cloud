import pandas as pd
from openpyxl import load_workbook
import mysql.connector
from mysql.connector import Error
import os
import sys

class DatabaseOperations:
    def __init__(self, excel_path):
        """Initialize with path to Excel workbook"""
        self.wb = load_workbook(excel_path)
        self.ins_sheet = self.wb['Ins']  # Assuming sheet name is "Ins"
        self.db_name = None
        self.conn = None
        
    def get_connection_string(self):
        """Equivalent to ConnectionString() in VBA"""
        db_config = {
            'host': 'hqdb.ccb',
            'port': 3306,
            'database': 'hub',
            'user': 'seim',
            'password': 'report5',
        }
        return db_config

    def connect_to_database(self):
        """Create database connection"""
        try:
            self.conn = mysql.connector.connect(**self.get_connection_string())
            return self.conn
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def update_data_run_list(self):
        """Equivalent to updateDataRunList() in VBA"""
        # Original SQL query implementation
        """
        try:
            if self.conn is None:
                self.connect_to_database()
            
            cursor = self.conn.cursor()
            sql = """
            SELECT dbname 
            FROM hub.tbldataruns 
            WHERE isAvailable = 1 AND dbname LIKE 'sa_us_20__/__' 
            ORDER BY datarunID DESC
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # Clear existing content
            for row in range(20, 28):
                self.ins_sheet[f'F{row}'] = None
            
            # Update with new values
            current_row = 20
            for result in results:
                self.ins_sheet[f'F{current_row}'] = result[0]
                current_row += 1
                
            self.wb.save()
            
        except Error as e:
            print(f"Error updating data run list: {e}")
        """
        
        # Instead, call the Python script as in the original
        sys.path.append('C:\\EIS')
        from Processes.eis_automation.eis_api.get_datarun import get_datarun
        get_datarun()

    def set_data_run(self):
        """Equivalent to SetDataRun() in VBA"""
        try:
            if self.conn is None:
                self.connect_to_database()
                
            cursor = self.conn.cursor()
            
            if self.ins_sheet['G3'].value == 1:
                # Choose current data run
                sql = """
                SELECT dbname 
                FROM hub.tbldataruns 
                WHERE isCurrent = 1 
                AND nationid = 3 
                AND dbname LIKE 'sa_us_20__/__'
                """
                cursor.execute(sql)
                result = cursor.fetchone()
                
                if result:
                    self.db_name = result[0]
            else:
                data_run_row = 18 + self.ins_sheet['G3'].value
                db_name = self.ins_sheet[f'F{data_run_row}'].value
                self.db_name = f"sa_ca_{db_name.replace('.', '_')}"
                
        except Error as e:
            print(f"Error setting data run: {e}")

    def close_db_connection(self):
        """Equivalent to CloseDBConnection() in VBA"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Destructor to ensure database connection is closed"""
        self.close_db_connection()