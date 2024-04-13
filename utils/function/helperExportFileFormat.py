import os
import pandas as pd

def export_excel_to_csv(input_file):
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        # Extract the directory and file name from the input file path
        directory = os.path.dirname(input_file)
        file_name = os.path.basename(input_file)
        
        # Create the output file path by replacing the extension with ".csv"
        output_file_path = os.path.join(directory, os.path.splitext(file_name)[0] + '.csv')
        
        # Write the data to a semicolon-separated CSV file
        df.to_csv(output_file_path, sep=';', index=False)
        
        print("Output file path:", output_file_path)
        print("Conversion successful.")
        
        return output_file_path
    except Exception as e:
        print("Error:", e)