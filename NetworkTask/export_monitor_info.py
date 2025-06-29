"""
Export fields ["time", "cpu_usage", "memory_usage"] from individual workerX.json to workerX.csv for plot
"""
import json
import pandas as pd



def json_to_csv(input_json_file, output_csv_file):
    """
    Reads a JSON file, extracts the time, cpu_usage and memory_usage columns
    from the resource_usage tag, sorts the data by time and saves it to a CSV.

    Args:
    input_json_file (str): Path to the input JSON file.
    output_csv_file (str): Path to the output CSV file.
    """
    with open(input_json_file, 'r') as f:
        data = json.load(f)
    
    # Give the resource_usage tag
    resource_usage_data = data.get("resource_usage", [])
    
    # Convert in DataFrame
    df = pd.DataFrame(resource_usage_data)
    
    # check columns exist
    columns_to_extract = ["time", "cpu_usage", "memory_usage"]
    if all(col in df.columns for col in columns_to_extract):
        # filter and order by time
        sorted_df = df[columns_to_extract].sort_values(by="time")
        # save on CSV
        sorted_df.to_csv(output_csv_file, index=False)
    else:
        raise ValueError(f"The JSON file does not contain all the required columns: {columns_to_extract}")

# Usage example
# json_to_csv("input.json", "output.csv")
