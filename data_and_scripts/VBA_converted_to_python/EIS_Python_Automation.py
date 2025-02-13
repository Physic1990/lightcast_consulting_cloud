import sys
from pathlib import Path
import win32com.client
from openpyxl import load_workbook
import os

class EISOperations:
    def __init__(self, excel_path):
        """Initialize with path to Excel workbook"""
        self.wb = load_workbook(excel_path)
        self.ins_sheet = self.wb['Ins']  # Assuming sheet name is "Ins"
        self.excel_app = win32com.client.Dispatch("Excel.Application")
        self.wb_excel = self.excel_app.Workbooks.Open(excel_path)
        
        # Ensure EIS path is in system path
        sys.path.append('C:\\EIS')
        
    def define_sheet_names(self):
        """Equivalent to Main.DefineSheetNames in VBA"""
        # This would need to be implemented based on the Main module's functionality
        pass

    def update_status(self, cell, value="Done!"):
        """Update status in Excel sheet"""
        self.ins_sheet[cell] = value
        self.wb.save()

    def clear_cell(self, cell):
        """Clear specific cell content"""
        self.ins_sheet[cell] = ""
        self.wb.save()

    def run_eis(self):
        """Run EIS operation"""
        from Processes.eis_automation.new_run_eis import run_eis
        run_eis()

    def run_pseis(self):
        """Run PSEIS operation"""
        from Processes.eis_automation.new_run_eis import run_pseis
        run_pseis()

    def run_region_and_state_income(self):
        """Run Region and State Income operation"""
        self.excel_app.Calculation = -4135  # xlManual
        self.define_sheet_names()
        from Processes.eis_automation.new_run_eis import import_state_and_region_incomes
        import_state_and_region_incomes()
        self.update_status('M8')
        self.excel_app.Calculation = -4105  # xlAutomatic

    def run_credit_engine(self):
        """Run Credit Engine operation"""
        self.define_sheet_names()
        self.clear_cell('M10')
        from Processes.eis_automation.new_run_eis import import_credit_engine
        import_credit_engine()
        self.update_status('M8')

    def run_config(self):
        """Run Config operation"""
        self.define_sheet_names()
        self.clear_cell('M12')
        from Processes.eis_automation.new_run_eis import import_config
        import_config()
        self.update_status('M8')

    def run_pseis_operations(self):
        """Run PSEIS related operations"""
        self.define_sheet_names()
        operations = {
            'P11': 'import_pseis_occ_data',
            'P12': 'import_pseis_occ_ed_data',
            'P13': 'import_pseis_ed_demo_data',
            'P14': 'import_pseis_completions_data',
            'P15': 'import_pseis_occ_mapping',
            'P16': 'import_pseis_job_growth_data',
            'P17': 'import_pseis_unique_postings_data',
            'P18': 'import_pseis_top_employers_data',
            'P19': 'import_pseis_occ_demo_data'
        }
        
        for cell, function_name in operations.items():
            self.clear_cell(cell)
            module = __import__(f'Processes.eis_automation.new_run_eis', fromlist=[function_name])
            getattr(module, function_name)()
            self.update_status('P9')

    def run_formula_insertion_for_income_sheet(self):
        """Run formula insertion for income sheet"""
        self.define_sheet_names()
        active_sheet = self.wb_excel.ActiveSheet.Name
        from Processes.eis_automation.region_and_state_income.xl_formula_revert import main
        main(income_sheet_name=active_sheet)

    def write_short_results(self):
        """Write short results"""
        self.define_sheet_names()
        from Processes.eis_automation.eis_api.short_sheet import main
        main()

    def calculate_data_run(self):
        """Calculate data run value"""
        if self.ins_sheet['G3'].value == 1:
            datarun = self.ins_sheet['F20'].value
        else:
            datarun_row = 18 + self.ins_sheet['G3'].value
            datarun = self.ins_sheet[f'F{datarun_row}'].value
        
        datarun = datarun.replace('.', '')
        datarun = int(datarun)
        
        return 'eis_automation'

    def __del__(self):
        """Cleanup Excel application"""
        try:
            self.wb_excel.Close(SaveChanges=False)
            self.excel_app.Quit()
        except:
            pass