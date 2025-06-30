import Metashape
import os, sys
import argparse
assert Metashape.app.version.startswith("2."), "Update Metashape Pro"

CLASS_MAPPING = {
    "created": Metashape.PointClass.Created,
    "unclassified": Metashape.PointClass.Unclassified,
    "ground": Metashape.PointClass.Ground,
    "low_vegetation": Metashape.PointClass.LowVegetation,
    "medium_vegetation": Metashape.PointClass.MediumVegetation,
    "high_vegetation": Metashape.PointClass.HighVegetation,
    "building": Metashape.PointClass.Building,
    "low_point": Metashape.PointClass.LowPoint,
    "model_key_point": Metashape.PointClass.ModelKeyPoint,
    "water": Metashape.PointClass.Water,
    "rail": Metashape.PointClass.Rail,
    "road_surface": Metashape.PointClass.RoadSurface,
    "overlap_points": Metashape.PointClass.OverlapPoints,
    "wire_guard": Metashape.PointClass.WireGuard,
    "wire_conductor": Metashape.PointClass.WireConductor,
    "transmission_tower": Metashape.PointClass.TransmissionTower,
    "wire_connector": Metashape.PointClass.WireConnector,
    "bridge_deck": Metashape.PointClass.BridgeDeck,
    "high_noise": Metashape.PointClass.HighNoise,
    "car": Metashape.PointClass.Car,
    "manmade": Metashape.PointClass.Manmade
}

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
    
def invert_masks(chunk: Metashape.Chunk):
    """
    Invert masks for all cameras in the specified chunk.
    Args:
        chunk (Metashape.Chunk): The chunk containing the cameras with masks to invert.
    """
    for camera in chunk.cameras:
        if camera.mask is not None:
            try:
                camera.mask = camera.mask.invert()
                # print(f"Mask inverted for {camera.label}")
            except Exception as e:
                print(f"Error inverting mask for {camera.label}: {e}")

def select_points_by_mask(chunk: Metashape.Chunk, softness: float = 4, only_visible: bool = True):
    """
    Selects the dense cloud points that correspond to the camera masks.

    Args:
        chunk (Metashape.Chunk): The chunk containing the dense cloud and the cameras.
        softness (float): Softness of the mask edges (default: 4).
        only_visible (bool): Select only visible points (default: True).

    The function sets the 'selected' attribute of the points corresponding to the mask.
    """
    if not chunk.point_cloud:
        raise RuntimeError("No Dense Cloud on chunk.")
    
    cameras = [camera for camera in chunk.cameras if camera.mask is not None]
    print("#cameras:", len(cameras))
    if not cameras:
        raise RuntimeError("No cameras with masks found.")

    try:
        chunk.point_cloud.selectMaskedPoints(cameras, softness=softness, only_visible=only_visible, progress=progress_callback)
        print("Points successfully selected based on masks.")

    except Exception as e:
        print(f"Error while selecting points: {e}")

def classify_selected_points(chunk: Metashape.Chunk, class_type=Metashape.PointClass.Ground):
    """
    Classifies the selected points in the dense cloud and prints the number of classified points.

    Args:
        chunk (Metashape.Chunk): The chunk containing the dense cloud.
        class_type (Metashape.PointClass): The class to assign to the selected points (default: Created).
    """
    if not chunk.point_cloud:
        raise RuntimeError("Dense cloud not present in chunk.")

    try:
        # Assign class to selected points
        chunk.point_cloud.assignClassToSelection(target=class_type, progress=progress_callback)
        
    except Exception as e:
        print(f"Error while classifying points: {e}")

# Not a solution - better generate and align model with mask already imported
#def clean_point_cloud_using_masks(chunk: Metashape.Chunk):
#    """
#    Cleans the dense cloud by removing points covered by image masks.
#    """
#    if not chunk.point_cloud:
#        raise RuntimeError("Dense cloud not present in chunk.")

#    point_cloud = chunk.point_cloud

#    for i, camera in enumerate(chunk.cameras, start=1):
#        if camera.mask is None:
#            continue

#        print(f"[{i}/{len(chunk.cameras)}] Processing the mask for the chamber: {camera.label}")

        # Select points covered by the mask of the current camera.
#        point_cloud.selectMaskedPoints([camera])

#    try:
#        point_cloud.removeSelectedPoints()
#        print(f"Points removed for the room: {camera.label}")
#    except RuntimeError as e:
#        print(f"Error while removing for {camera.label}: {e}")

#    print("Dense cloud clearing completed.")
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Metashape script for mask import, optional inversion, and dense cloud cleaning.")

    # Obligatory arguments
    parser.add_argument('--project', required=True, type=str,
                        help='Path to the Metashape project file (.psx).')
    parser.add_argument('--output_dir', required=True, type=str,
                        help='Path to the output directory for cleaned dense cloud export.')
    parser.add_argument('--masks_dir', required=True, type=str,
                        help='Path to the directory containing image masks (PNG files).')
    parser.add_argument('--classification_type', required=True, type=str,
                        help='Specifies the type of classification to apply (e.g., "ground", "building", "vegetation").')
    
    # Optional argument (flag)
    parser.add_argument('--invert_masks', action='store_true',
                        help='If set, imported masks will be inverted after import.')

    args = parser.parse_args()

    project_path = args.project
    output_directory = args.output_dir
    masks_directory = args.masks_dir
    invert_imported_masks = args.invert_masks
    classification_type_str = args.classification_type

    # --- Path Validation ---
    if not os.path.isfile(project_path):
        raise FileNotFoundError(f"Project file not found: {project_path}")
    
    if not os.path.isdir(output_directory):
        print(f"Output directory '{output_directory}' does not exist. Creating it...")
        os.makedirs(output_directory)
    
    if not os.path.isdir(masks_directory):
        raise NotADirectoryError(f"Masks directory not found: {masks_directory}")
    
    # Validate classification_type and convert to enum
    if classification_type_str.lower() not in CLASS_MAPPING:
        raise ValueError(f"Invalid classification type: '{classification_type_str}'. "
                         f"Supported types are: {', '.join(CLASS_MAPPING.keys())}")
    
    selected_class_type = CLASS_MAPPING[classification_type_str.lower()]
    print(f"Classification type specified: {classification_type_str}")

    # --- Metashape Operations ---
    print(f"Loading project: {project_path}")
    doc = load_project(project_path)
    if len(doc.chunks) == 0:    
        raise RuntimeError("No chunk found")
    chunk = doc.chunk

    if not len(doc.chunks):
        raise RuntimeError("No chunks found in the project.")

    chunk = doc.chunks[0]

    # check steps
    status = {
        "Camera": check_camera(doc),
        "Dense Cloud": check_dense_cloud(doc)
    }

    missing_steps = [key for key, value in status.items() if not value]
    if missing_steps:
        print("Error: The project is incomplete.")
        for step in missing_steps:
            print(f"    - {step}")
        Metashape.app.quit()
        sys.exit(1)

    import_masks(chunk=chunk, masks_directory=masks_directory)
    doc.save()

    if invert_imported_masks:
        print("Option --invert_masks was set. Inverting masks...")
        invert_masks(chunk=chunk)
        print("Mask inversion finished.")
        doc.save()

    select_points_by_mask(chunk=chunk, softness=4, only_visible=True)
    doc.save()

    classify_selected_points(chunk=chunk, class_type=selected_class_type)
    doc.save()

    # Count the points in the assigned class
    classified_count = chunk.point_cloud.point_count_by_class
    print(f"Points classified as: {classified_count} / {chunk.point_cloud.point_count}")

    #clean_point_cloud_using_masks(chunk=chunk)
    #doc.save()

    dense_cloud_export_path = os.path.join(output_directory, f"{classification_type_str}_cloud.las")
    try:
        chunk.exportPointCloud(path=dense_cloud_export_path, source_data = Metashape.PointCloudData, classes=[selected_class_type], progress=progress_callback)
        print(f"Cleaned dense cloud exported to: {dense_cloud_export_path}")
    except Exception as e:
        print(f"Error exporting dense cloud: {e}")

    Metashape.app.quit()
    sys.exit(0)