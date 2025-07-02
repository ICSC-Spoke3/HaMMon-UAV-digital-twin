import os
import json


def rename_photos(json_file, photos_folder):
    
    try:
        # Load the contents of the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(e)
        return

    # Iterate through elements in the JSON file
    for item in data:
        try:
            # Get image path from JSON file
            image_path = item.get('image', None)
            
            if image_path:
                # Extract file name from image
                base_name = os.path.basename(image_path)

                # Convert the extension to lowercase
                extension = base_name.split('.')[-1].lower()
                base_name = base_name.rsplit('.', 1)[0] + '.' + extension
                
                # Manage .png and .jpg
                if base_name.endswith('.png'):
                    new_name = base_name.split('-')[-1].replace('.png', '_mask.png')
                elif base_name.endswith('.jpg'):
                    new_name = base_name.split('-')[-1].replace('.jpg', '_mask.png')
                else:
                    print("Extension in non-compliant format")
                    continue
                
                # Check if the required fields are present in the JSON-mini
                if 'tag' in item and item['tag'] and 'brushlabels' in item['tag'][0]:
                    brushlabels = item['tag'][0]['brushlabels'][0]
                else:
                    print("Missing JSON fields: tags or item[tag] or brushlabels")
                    continue
                
                # Costruisci il nome del file originale basato sui campi del JSON
                old_name = f"task-{item['id']}-annotation-{item['annotation_id']}-by-{item['annotator']}-tag-{brushlabels}-0.png"
                
                # Get the full path of the file in the photos folder
                old_file_path = os.path.join(photos_folder, old_name)
                new_file_path = os.path.join(photos_folder, new_name)
                
                # Rename the file if it exists in the photos folder
                if os.path.exists(old_file_path):
                    os.rename(old_file_path, new_file_path)
                    print(f'Rename {old_name} in {new_name}')
                else:
                    print(f'{old_name} not found in photos folder')
        except Exception as e:
            print(f"Error while renaming file: {e}")


# main
json_file = 'path/to/.json'
photos_folder = 'path/to/photo/folder'
rename_photos(json_file, photos_folder)
