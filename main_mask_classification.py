#  python -m unittest discover -s test -p "test_*.py"
# run vscode
import Metashape
import os, sys
assert Metashape.app.version.startswith("2."), "Update Metashape Pro"

def progress_callback(pct):
    print(f"Progresso: {pct:.2f}% completato")

def load_project(percorso_progetto: str) -> Metashape.Document:
    """
    Carica un progetto Metashape (.psx)
    Args:
        percorso_progetto (str): Il percorso del file .psx
    Returns:
        Metashape.Document: L'oggetto documento Metashape caricato
    Raises:
        FileNotFoundError: Se il file non esiste
        RuntimeError: Se il progetto non può essere aperto
    """
    if not isinstance(percorso_progetto, str):
        raise TypeError("The project path must be a string.")
    if not percorso_progetto.endswith((".psx", ".psz")):
        raise ValueError("The project file must be a .psx/.psz format")
    
    try:
        doc = Metashape.Document()
        doc.open(percorso_progetto, read_only=False)
        return doc
    except Exception as e:
        raise RuntimeError(f"Loading error project: {e}")
    
def check_camera(doc: Metashape.Document) -> bool:
    """Verifica se il progetto contiene camere su cui applicare la maschera"""
    chunk = doc.chunk
    if chunk and chunk.cameras:
        return True
    return False

def check_dense_cloud(doc: Metashape.Document) -> bool:
    """Verifica se presente una nuvola densa"""
    chunk = doc.chunk
    if chunk and chunk.point_cloud and chunk.point_cloud.point_count > 0:
        print("Nuvola di punti totale:", chunk.point_cloud.point_count)
        return True
    return False

#def check_model(doc: Metashape.Document) -> bool:
    """Verifica se presente un modello"""

def import_masks(chunk: Metashape.Chunk, masks_directory: str):
    """
    Importa le maschere per le immagini nel chunk specificato
    Args:
        chunk (Metashape.Chunk): il chunk su cui importare le maschere
        mask_path (str): percorso cartelle contenenti le maschere delle foto (png)
    """
    if not os.path.isdir(masks_directory):
        raise NotADirectoryError(f"Il percorso delle maschere '{masks_directory}' non è una directory valida")
    
    for camera in chunk.cameras:
        if camera.label:
            # Costruisce il percorso del file maschera usando il nome della camera
            mask_file_name = f"{camera.label}_mask.png" # nome formato maschere
            mask_file_path = os.path.join(masks_directory, mask_file_name)
            if os.path.isfile(mask_file_path):
                try:
                    chunk.generateMasks(path=mask_file_path, masking_mode=Metashape.MaskingMode.MaskingModeFile, mask_operation=Metashape.MaskOperation.MaskOperationReplacement, tolerance=10, cameras=[camera], replace_asset = True)
                    #print(f"Maschera importata per {camera.label}")
                except Exception as e:
                    print(f"Errore nell'importazione della maschera per {camera.label}: {e}")
            else:
                print(f"Maschera non trovata per {camera.label}") # al percorso {mask_file_path}")
    
    # Inverto maschera di selezione
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

    

def select_classif_points_by_mask_iterations(chunk: Metashape.Chunk, softness: float = 4, only_visible: bool = False):
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
    print("Totale maschere inserite:", len(cameras))
    if not cameras:
        raise RuntimeError("No cameras with masks found.")

    try:
        point_cloud = chunk.point_cloud

        for i in cameras:   # itero per sole camere avente la maschera
            print('Selezione la maschera di camera: ', i)
            point_cloud.selectMaskedPoints([i], softness=softness, only_visible=only_visible)#, progress=progress_callback)

            try:
                print('Classificazione nuvola di punti di camera: ', i)
                point_cloud.assignClassToSelection(target=2)

            except Exception:
                print('There was no point selected, moving on')
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
    percorso_progetto = "progetto_ottignana/progetto_ottignana.psx"
    percorso_maschere = "Maschere Ottignana"
    percorso_output = "output"

    # workflow
    doc = load_project(percorso_progetto)
    if len(doc.chunks) == 0:    
        raise RuntimeError("Nessun chunk presente nel documento.")
    chunk = doc.chunk

    

    # check steps
    stato = {
        "Camera": check_camera(doc),
        "Nuvola Densa": check_dense_cloud(doc),
        # "Modello 3D": check
    }

    missing_steps = [key for key, value in stato.items() if not value]

    if missing_steps:
        print("Error: The project is incomplete.")
        for step in missing_steps:
            print(f"    - {step}")
        Metashape.app.quit()
        sys.exit(1)

    # Importa le maschere sulle camere
    import_masks(chunk=chunk, masks_directory=percorso_maschere)
    doc.save()

    #select_classif_points_by_mask_iterations(chunk=chunk, softness=4, only_visible=True)
    #doc.save()

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