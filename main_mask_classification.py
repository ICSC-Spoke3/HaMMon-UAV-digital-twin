import Metashape
import os, sys
assert Metashape.app.version.startswith("2."), "Update Metashape Pro"

def progress_callback(pct):
    print(f"Progress: {pct:.2f}% complete")

def load_project(project_path: str) -> Metashape.Document:
    """
    Load a Metashape project (.psx)
    Args:
        project_path (str): The path to the .psx file
    Returns:
        Metashape.Document: The loaded Metashape document object
    Raises:
        FileNotFoundError: If the file does not exist
        RuntimeError: If the project cannot be opened
    """
    if not isinstance(project_path, str):
        raise TypeError("The project path must be a string.")
    if not project_path.endswith((".psx", ".psz")):
        raise ValueError("The project file must be a .psx/.psz format")
    
    try:
        doc = Metashape.Document()
        doc.open(project_path, read_only=False)
        return doc
    except Exception as e:
        raise RuntimeError(f"Loading error project: {e}")
    
def check_camera(doc: Metashape.Document) -> bool:
    """Check if the project contains cameras to apply the mask to"""
    chunk = doc.chunk
    if chunk and chunk.cameras:
        return True
    return False

def check_dense_cloud(doc: Metashape.Document) -> bool:
    """Check if there is a dense cloud"""
    chunk = doc.chunk
    if chunk and chunk.point_cloud and chunk.point_cloud.point_count > 0:
        print("Point Cloud Dense #:", chunk.point_cloud.point_count)
        return True
    return False

#def check_model(doc: Metashape.Document) -> bool:
    """Verifica se presente un modello"""

def import_masks(chunk: Metashape.Chunk, masks_directory: str):
    """
    Import image masks into the specified chunk
    Args:
        chunk (Metashape.Chunk): the chunk to import masks into
        masks_directory (str): path to folders containing photo masks (png)
    """
    if not os.path.isdir(masks_directory):
        raise NotADirectoryError(f"Mask folder '{masks_directory}' it is not a valid directory")
    
    for camera in chunk.cameras:
        if camera.label:
            # Builds the mask file path using the camera name
            mask_file_name = f"{camera.label}_mask.png" # mask name format
            mask_file_path = os.path.join(masks_directory, mask_file_name)
            if os.path.isfile(mask_file_path):
                try:
                    chunk.generateMasks(path=mask_file_path, masking_mode=Metashape.MaskingMode.MaskingModeFile, mask_operation=Metashape.MaskOperation.MaskOperationReplacement, tolerance=10, cameras=[camera], replace_asset = True)
                    #print(f"import mask-th for {camera.label}")
                except Exception as e:
                    print(f"Error importing mask for {camera.label}: {e}")
            else:
                print(f"Mask not found for {camera.label}") # on {mask_file_path}")
    
    # Invert masks
    for camera in chunk.cameras:
        if camera.mask is not None:
            camera.mask = camera.mask.invert()

def select_points_by_mask(chunk: Metashape.Chunk, softness: float = 4, only_visible: bool = True):
    """
    Seleziona i punti della nuvola densa che corrispondono alle maschere delle camere.
    
    Args:
        chunk (Metashape.Chunk): il chunk contenente la nuvola densa e le camere.
        softness (float): Morbidezza dei bordi della maschera (default: 4).
        only_visible (bool): Selezionare solo punti visibili (default: False).
    
    La funzione imposta l'attributo 'selected' dei punti corrispondenti alla maschera.
    """
    if not chunk.point_cloud:
        raise RuntimeError("Nuvola densa non presente nel chunk.")
    
    cameras = [camera for camera in chunk.cameras if camera.mask is not None]
    print("totale maskere inserite:", len(cameras))
    if not cameras:
        raise RuntimeError("No cameras with masks found.")

    try:
        chunk.point_cloud.selectMaskedPoints(cameras, softness=softness, only_visible=only_visible, progress=progress_callback)
        print("Punti selezionati con successo basandosi sulle maschere.")
        
        """
        if not chunk.shapes:
            chunk.shapes = Metashape.Shapes()
            chunk.shapes.crs = chunk.crs
        shape = chunk.shapes.addShape()
        shape.type = Metashape.Shape.Polygon
        shape.vertices = chunk.point_cloud
        shape.label = "TESTO" """

    except Exception as e:
        print(f"Errore durante la selezione dei punti: {e}")


def classify_selected_points(chunk: Metashape.Chunk, class_type=Metashape.PointClass.Ground):
    """
    Classifica i punti selezionati nella nuvola densa e stampa il numero di punti classificati.

    Args:
        chunk (Metashape.Chunk): il chunk contenente la nuvola densa.
        class_type (Metashape.PointClass): Classe da assegnare ai punti selezionati (default: Created).
    """
    if not chunk.point_cloud:
        raise RuntimeError("Nuvola densa non presente nel chunk.")

    try:
        # Assegna la classe ai punti selezionati
        chunk.point_cloud.assignClassToSelection(target=class_type, progress=progress_callback)
        
    except Exception as e:
        print(f"Errore durante la classificazione dei punti: {e}")


def clean_point_cloud_using_masks(chunk: Metashape.Chunk):
    """
    Pulisce la nuvola densa rimuovendo i punti coperti dalle maschere delle immagini.
    """
    if not chunk.point_cloud:
        raise RuntimeError("Nuvola densa non presente nel chunk.")

    point_cloud = chunk.point_cloud

    for i, camera in enumerate(chunk.cameras, start=1):
        if camera.mask is None:
            continue  # Salta le camere senza maschere

        print(f"[{i}/{len(chunk.cameras)}] Elaborazione della maschera per la camera: {camera.label}")
        point_cloud.selectMaskedPoints([camera])

        # Conta i punti selezionati
        selected_count = sum(1 for p in point_cloud.Points if p.selected)
        print(f"Punti selezionati dopo la maschera: {selected_count}")

        # Evita di rimuovere se nessun punto è selezionato
        if selected_count > 0:
            try:
                point_cloud.removeSelectedPoints()
                print(f"Punti rimossi per la camera: {camera.label}")
            except RuntimeError as e:
                print(f"Errore durante la rimozione per {camera.label}: {e}")
        else:
            print(f"Nessun punto selezionato per la camera: {camera.label}. Salto questa camera.")
    
def shape_creation_by_cloud(chunk: Metashape.Chunk, class_point: Metashape.PointClass = Metashape.PointClass.Ground):
     # Filtra i punti della classe "Ground" (esempio)
    ground_points = [point.coord for point in chunk.point_cloud 
                     if point.valid and point.classification == class_point]
    
    if ground_points:
        # Crea uno shape layer se non esiste
        if not chunk.shapes:
            chunk.shapes = Metashape.Shapes()
            chunk.shapes.crs = chunk.crs # usa lo stesso sistema di coordinate del chunk
        shape = chunk.shapes.addShape()
        shape.type = Metashape.Shape.Polygon
        shape.vertices = ground_points
        shape.label = "Regione Ground"
        print("Shape generato con successo dai punti classificati!")
    else:
        print("Nessun punto classificato come 'Ground' trovato.")

# assignClassToSelection
# assignClass
#cropSelectedPoints
# point_count_by_class
# renderMask



if __name__ == "__main__":
        
    # Project path to update
    project_path = "path/to/project.psx"
    mask_path = "path/to/mask/folder"
    output_path = "path/to/output/folder"

    # Workflow
    doc = load_project(project_path)
    if len(doc.chunks) == 0:    
        raise RuntimeError("No chunk found")
    chunk = doc.chunk

    # check steps
    stato = {
        "Camera": check_camera(doc),
        "Dense Cloud": check_dense_cloud(doc)
    }

    missing_steps = [key for key, value in stato.items() if not value]
    if missing_steps:
        print("Error: The project is incomplete.")
        for step in missing_steps:
            print(f"    - {step}")
        Metashape.app.quit()
        sys.exit(1)

    # Import Mask
    import_masks(chunk=chunk, masks_directory=mask_path)
    doc.save()

    # Seleziona i punti della nuvola densa che ricadono nelle maschere
    select_points_by_mask(chunk, softness=4, only_visible=True)
    doc.save()


    # Classificazione dei punti selezionati
    #classify_selected_points(chunk, class_type=Metashape.PointClass.Ground)
    #doc.save()

    # Conta i punti nella classe assegnata
    #classified_count = chunk.point_cloud.point_count_by_class
    #print(f"Punti classificati come: {classified_count} / {chunk.point_cloud.point_count}")




    print()
    Metashape.app.quit()
    sys.exit(0)