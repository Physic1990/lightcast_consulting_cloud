import pandas as pd
import numpy as np
from openpyxl import load_workbook
from scipy.stats import norm

class CreditEngine:
    def __init__(self, workbook_path):
        """Initialize with path to Excel workbook"""
        self.wb = load_workbook(workbook_path)
        self.continuing_feed = self.wb['ContinuingFeed']  # Assuming sheet names
        self.credit_engine = self.wb['CreditEngine']
        self.ins = self.wb['Instructions']

    def call_credit_engine(self):
        """Main entry point - equivalent to callCreditEngine() in VBA"""
        # Clear the cumulative che vector
        for row in range(4, 10000):
            self.continuing_feed[f'AB{row}'] = None

        # Check each education level and run credit engine
        education_levels = {
            7: "Professional",
            8: "Ph.D.",
            9: "Masters",
            10: "Bachelors",
            11: "Associates",
            12: "Certificate"
        }

        for row, level in education_levels.items():
            if self.continuing_feed[f'C{row}'].value != 0:
                self.ins['M8'] = f"Running Credit Engine at {level} Level"
                self.credit_engine(row)

    def credit_engine(self, category_row):
        """Main credit engine calculation - equivalent to creditEngine() in VBA"""
        # Get initial parameters based on education level
        if self.continuing_feed[f'B{category_row}'].value == "Professional":
            start_row = 275
            achievement_row = 334
        else:
            start_row = self.continuing_feed[f'G{category_row}'].value
            achievement_row = self.continuing_feed[f'H{category_row}'].value

        cur_mean = self.continuing_feed[f'D{category_row}'].value
        range_length = 42
        chi_start_row = 18

        # Update mean for this category
        self.continuing_feed['C14'] = cur_mean
        
        # First phase: Chi-squared distribution calculations
        self._process_chi_distribution(start_row, achievement_row, range_length, 
                                    chi_start_row, category_row)
        
        # Second phase: Normal distribution calculations
        self._process_normal_distribution(category_row, achievement_row, start_row)

    def _process_chi_distribution(self, start_row, achievement_row, range_length, 
                                chi_start_row, category_row):
        """Handle the chi-squared distribution portion of calculations"""
        students_col = self.continuing_feed[f'I{category_row}'].value
        
        for i in range(start_row, achievement_row - range_length - 3):
            num_students = self.continuing_feed[f'{students_col}{i}'].value
            
            # Update first two rows
            for j in range(i + 1, i + 3):
                current_val = self.continuing_feed[f'AB{j}'].value or 0
                self.continuing_feed[f'AB{j}'] = current_val + num_students
            
            # Process distribution
            chi_counter = chi_start_row
            last_num_students = num_students
            last_end_yr_pos = 0
            
            for j in range(i + 3, i + range_length):
                end_yr_pos = self.continuing_feed[f'D{chi_counter}'].value * num_students
                chi_counter += 1
                
                current_val = self.continuing_feed[f'AB{j}'].value or 0
                cur_num_students = last_num_students - last_end_yr_pos
                
                self.continuing_feed[f'AB{j}'] = cur_num_students + current_val
                
                last_end_yr_pos = end_yr_pos
                last_num_students = cur_num_students

    def _process_normal_distribution(self, category_row, achievement_row, start_row):
        """Handle the normal distribution portion of calculations"""
        if self.continuing_feed[f'B{category_row}'].value == "Professional":
            self._process_professional_distribution(category_row, achievement_row)
        else:
            self._process_standard_distribution(category_row, achievement_row, start_row)

    def _process_professional_distribution(self, category_row, achievement_row):
        """Process distribution for professional level"""
        students_col = self.continuing_feed[f'I{category_row}'].value
        
        for i in range(achievement_row - 60 - 2, achievement_row - 4):
            num_students = self.continuing_feed[f'{students_col}{i-60}'].value
            available_range = achievement_row - i - 3
            custom_mean = (available_range - 3) / 2
            
            self._calculate_distribution(i, available_range, num_students, custom_mean)

    def _process_standard_distribution(self, category_row, achievement_row, start_row):
        """Process distribution for non-professional levels"""
        students_col = self.continuing_feed[f'I{category_row}'].value
        range_length = 42
        
        for i in range(achievement_row - range_length - 2, achievement_row - 4):
            num_students = self.continuing_feed[f'{students_col}{i}'].value
            available_range = achievement_row - i - 3
            custom_mean = (available_range - 3) / 2
            
            self._calculate_distribution(i, available_range, num_students, custom_mean)

    def _calculate_distribution(self, i, available_range, num_students, custom_mean):
        """Calculate normal distribution for a given range"""
        std_dev = np.std(range(1, available_range + 1))
        
        # Calculate normal distribution
        x = np.arange(available_range)
        dist = norm.pdf(x, custom_mean, std_dev)
        normalized_dist = dist / np.sum(dist)
        student_dist = normalized_dist * num_students
        
        # Update final CHE column
        deflator = 0
        for j in range(i, i + available_range):
            final_che = self.continuing_feed[f'AB{j}'].value or 0
            
            if j <= i + 2 or available_range <= 4:
                self.continuing_feed[f'AB{j}'] = final_che + num_students
            else:
                cur_deflator = student_dist[j - (i + 3)]
                deflator += cur_deflator
                self.continuing_feed[f'AB{j}'] = final_che + (num_students - deflator)