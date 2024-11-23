"""
Esporta i campi ["time", "cpu_usage", "memory_usage"] dai singoli workerX.json in workerX.csv per plot
"""
import json
import pandas as pd



def json_to_csv(input_json_file, output_csv_file):
    """
    Legge un file JSON, estrae le colonne time, cpu_usage e memory_usage
    dalla tag resource_usage, ordina i dati per time e li salva in un CSV.

    Args:
        input_json_file (str): Percorso al file JSON di input.
        output_csv_file (str): Percorso al file CSV di output.
    """
    # Legge il file JSON
    with open(input_json_file, 'r') as f:
        data = json.load(f)
    
    # Estrae la tag resource_usage
    resource_usage_data = data.get("resource_usage", [])
    
    # Converte in DataFrame
    df = pd.DataFrame(resource_usage_data)
    
    # Controlla che le colonne esistano
    columns_to_extract = ["time", "cpu_usage", "memory_usage"]
    if all(col in df.columns for col in columns_to_extract):
        # Filtra e ordina per time
        sorted_df = df[columns_to_extract].sort_values(by="time")
        # Salva nel CSV
        sorted_df.to_csv(output_csv_file, index=False)
    else:
        raise ValueError(f"Il file JSON non contiene tutte le colonne richieste: {columns_to_extract}")

# Esempio di utilizzo
# json_to_csv("input.json", "output.csv")
