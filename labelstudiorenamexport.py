import os
import json

def rename_photos(json_file, photos_folder):
    # Carica il contenuto del file JSON
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Itera attraverso gli elementi nel file JSON
    for item in data:
        # Ottieni il percorso dell'immagine dal file JSON
        image_path = item.get('image', None)
        
        if image_path:
            # Estrai il nome del file dall'immagine
            base_name = os.path.basename(image_path)

            # Converti l'estensione in minuscolo
            extension = base_name.split('.')[-1].lower()
            base_name = base_name.rsplit('.', 1)[0] + '.' + extension
            
            # Gestisci sia .png che .jpg
            if base_name.endswith('.png'):
                new_name = base_name.split('-')[-1].replace('.png', '_mask.png')
            elif base_name.endswith('.jpg'):
                new_name = base_name.split('-')[-1].replace('.jpg', '_mask.png')
            else:
                print("Estenzioni nel formato non conforme")
                break
            
            # Ottieni il valore di brushlabels all'interno di tag
            brushlabels = item['tag'][0]['brushlabels'][0]
            
            # Costruisci il nome del file originale basato sui campi del JSON
            old_name = f"task-{item['id']}-annotation-{item['annotation_id']}-by-{item['annotator']}-tag-{brushlabels}-0.png"
            
            # Ottieni il percorso completo del file nella cartella delle foto
            old_file_path = os.path.join(photos_folder, old_name)
            new_file_path = os.path.join(photos_folder, new_name)
            
            # Rinomina il file se esiste nella cartella delle foto
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
                print(f'Rinominato {old_name} in {new_name}')
            else:
                print(f'{old_name} non trovato nella cartella delle foto')

# Esempio di utilizzo
json_file = 'path to .json'
photos_folder = 'path to photos folder'
rename_photos(json_file, photos_folder)
