"""
Script created by Michael James Munar
Email: mjmunar.dev@gmail.com
"""
import maya.cmds as cmds
import maya.mel as mel
import os

# Shelf button creation function

def get_maya_version():
    result = cmds.promptDialog(
        title='Enter Maya Version',
        message='Enter Version:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'OK':
        maya_version = cmds.promptDialog(query=True, text=True)
        if not maya_version.isdigit():
            cmds.confirmDialog(title='Error', message="Invalid Maya version. Please enter a number.", button=['OK'])
            return None
        return maya_version
    return None

def get_shelf_name():
    result = cmds.promptDialog(
        title='Enter the Shelf name you want to add your render button',
        message='Enter Shelf Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == 'OK':
        shelf_name = cmds.promptDialog(query=True, text=True)
        if not shelf_name:
            cmds.confirmDialog(title='Error', message="Shelf name cannot be empty.", button=['OK'])
            return None
        return shelf_name
    return None

def create_shelf_button():
    shelf = get_shelf_name()
    button_name = "Apex Overseer"
    
    if not cmds.shelfLayout(shelf, q=True, ex=True):
        cmds.confirmDialog(title='Error', message=f"Shelf '{shelf}' does not exist.", button=['OK'])
        return
    
    maya_version = get_maya_version()
    if not maya_version:
        return
    
    maya_app_dir = os.environ.get('MAYA_APP_DIR')
    scripts_folder = os.path.join(maya_app_dir, f"{maya_version}\\scripts")
    
    if not os.path.exists(scripts_folder):
        os.makedirs(scripts_folder)
        
    script_path = os.path.join(scripts_folder, 'apex_overseer.py')
    if os.path.exists(script_path):
        try:
        # Delete the file
            os.remove(script_path)
            print(f"File {script_path} deleted successfully.")
        except OSError as e:
            print(f"Error: {script_path} : {e.strerror}")
    script = """import maya.cmds as cmds
import maya.mel as mel
import os

warning_background_color = (1, 0, 0)  # Red color (RGB)
done_background_color = (0, 1, 0)  # Green color (RGB)


window_name = "ApexOverseer"

character_mesh_path = r"\\192.168.8.90\Apex Environment\Documentation\Guidelines\Character Reference\Female_Character.obj"  # Update this to your actual file path
character_mesh_name = "scale_ref_human"  # Update this to your expected node name in Maya


# region Layers
def clean_layer():
    layers = cmds.ls(type="displayLayer")
    for layer in layers:
        if layer != "defaultLayer":
            cmds.delete(layer)
    print("Layers cleaned.")
    cmds.button("layers_status_button", edit=True, label="DONE", backgroundColor=done_background_color) 
    
def check_layer():
    layers = cmds.ls(type="displayLayer")
    if len(layers) == 1:
        return True
    else:
        return False

def create_layer_button():
    layer_response = check_layer()
    if layer_response:
        cmds.button("layers_status_button", label="DONE", width=100, height=25, backgroundColor=done_background_color) 
    else:
        cmds.button("layers_status_button", label="WARNING!", width=100, height=25, backgroundColor=warning_background_color, command=lambda *args: clean_layer())
        
def refresh_layer_button():
    layers = cmds.ls(type="displayLayer")
    if len(layers) == 1:
        cmds.button("layers_status_button", edit=True, label="DONE", backgroundColor=done_background_color) 
    else:
        cmds.button("layers_status_button", edit=True, label="WARNING!", backgroundColor=warning_background_color, command=lambda *args: clean_layer()) 
# endregion

#region Hypershade
def clean_hypershade():
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes")')
    cmds.button("hypershade_status_button", edit=True, label="DONE", backgroundColor=done_background_color)  
# endregion

# region Character Mesh
def import_fbx(character_mesh_path):
    if os.path.exists(character_mesh_path) and os.access(character_mesh_path, os.R_OK):
        print(f"File found: {character_mesh_path}")
        
        # Proceed with importing the OBJ file in Maya
        cmds.file(character_mesh_path, i=True, type="OBJ", ignoreVersion=True, options="mo=1", pr=True)
        print("OBJ Import completed.")
    else:
        print(f"File not found or cannot be accessed: {character_mesh_path}")
        
def import_character_mesh():
    print(f"Importing {character_mesh_name}...")
    # Ensure the FBX plugin is loaded
    if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
        cmds.loadPlugin("fbxmaya")

    if not check_character_mesh():
        print(f"{character_mesh_name} not found. Importing from {character_mesh_path}...")
        
        import_fbx(character_mesh_path)
        cmds.evalDeferred(lambda: update_character_mesh_button())
    else:
        print(f"{character_mesh_name} already exists in the scene.")

        
def check_character_mesh():
    outliner_objects = cmds.ls(assemblies=True)
    character_meshes = [obj for obj in outliner_objects if character_mesh_name in obj]
    print(f"Found {character_mesh_name} meshes:", character_meshes)
    if len(character_meshes) >= 1:
        return True
    else:
        return False

def update_character_mesh_button():
    if check_character_mesh():
        cmds.button("character_mesh_status_button", edit=True, label="DONE", backgroundColor=done_background_color)
    else:
        cmds.button("character_mesh_status_button", edit=True, label="WARNING!", backgroundColor=warning_background_color, command=lambda *args: import_character_mesh())

def create_character_mesh_button():
    if check_character_mesh():
         cmds.button("character_mesh_status_button", label="DONE", width=100, height=25, backgroundColor=done_background_color)
    else:
        cmds.button("character_mesh_status_button", label="WARNING!", width=100, height=25, backgroundColor=warning_background_color, command=lambda *args: import_character_mesh())
# endregion

# region Proxy Mesh
def check_proxy_mesh():
    # List all nodes in the scene, including those inside groups
    all_objects = cmds.ls(dag=True, long=True)  # dag=True will list all DAG nodes, long=True returns full paths
    
    # Filter objects that contain '_proxy' in their name
    proxy_objects = [obj for obj in all_objects if '_proxy' in obj]
    print("Found proxy objects:", proxy_objects)
    
    if len(proxy_objects) >= 1:
        return True
    else:
        return False
    
def create_proxy_mesh_button():
    if check_proxy_mesh():
        cmds.button("proxy_mesh_status_button", label="DONE", width=100, height=25, backgroundColor=done_background_color)
    else:
        cmds.button("proxy_mesh_status_button", label="WARNING!", width=100, height=25, backgroundColor=warning_background_color, command=lambda *args: update_proxy_mesh_status())
        
def update_proxy_mesh_status():
    if check_proxy_mesh():
        cmds.button("proxy_mesh_status_button", edit=True, label="DONE", backgroundColor=done_background_color)
    else:
        cmds.button("proxy_mesh_status_button", edit=True, label="WARNING!", backgroundColor=warning_background_color, command=lambda *args: update_proxy_mesh_status())
        cmds.confirmDialog(title='Proxy Mesh', message="No proxy mesh found. Please import the proxy mesh.", button=['OK'])

# endregion
# region Main
def run_all_checks():
    print("Starting clean_layer operation...")
    cmds.evalDeferred(lambda: clean_layer_and_continue())

def clean_layer_and_continue():
    clean_layer()
    print("clean_layer completed.")
    # Proceed to next task
    cmds.evalDeferred(lambda: clean_hypershade_and_continue())

def clean_hypershade_and_continue():
    clean_hypershade()
    print("clean_hypershade completed.")
    # Proceed to the next task
    cmds.evalDeferred(lambda: import_character_mesh_and_continue())

def import_character_mesh_and_continue():
    import_character_mesh()
    print("import_character_mesh completed.")
    # Proceed to the next task
    cmds.evalDeferred(lambda: update_proxy_mesh_status_and_finish())

def update_proxy_mesh_status_and_finish():
    update_proxy_mesh_status()
    print("update_proxy_mesh_status completed.")
    print("All tasks completed.")


# Refresh the UI by closing and reopening the window
def refresh_ui():
    print("Starting UI refresh...")
    # Refresh Layers button first
    cmds.evalDeferred(lambda: refresh_layers_and_continue())

def refresh_layers_and_continue():
    refresh_status_button("layers_status_button", check_layer, clean_layer)
    print("Layers status refreshed.")
    # Proceed to Hypershade button
    cmds.evalDeferred(lambda: refresh_hypershade_and_continue())

def refresh_hypershade_and_continue():
    refresh_status_button("hypershade_status_button", lambda: False, clean_hypershade)
    print("Hypershade status refreshed.")
    # Proceed to Character Mesh button
    cmds.evalDeferred(lambda: refresh_character_mesh_and_continue())

def refresh_character_mesh_and_continue():
    refresh_status_button("character_mesh_status_button", check_character_mesh, import_character_mesh)
    print("Character Mesh status refreshed.")
    # Proceed to Proxy Mesh button
    cmds.evalDeferred(lambda: refresh_proxy_mesh_and_finish())

def refresh_proxy_mesh_and_finish():
    refresh_status_button("proxy_mesh_status_button", check_proxy_mesh, update_proxy_mesh_status)
    print("Proxy Mesh status refreshed.")
    print("UI refresh completed.")

# Helper function to refresh the status of a button
def refresh_status_button(button_name, checker_function, clean_up_function):
    print(f"Refreshing {button_name} button...")
    if checker_function():
        cmds.button(button_name, edit=True, label="DONE", backgroundColor=done_background_color)
    else:
        cmds.button(button_name, edit=True, label="WARNING!", backgroundColor=warning_background_color, command=lambda *args: clean_up_function())

        
def refresh_status_button(button_name, checker_function_name, clean_up_function_name):
    print (f"Refreshing {button_name} button...")
    if checker_function_name():
        cmds.button(button_name, edit=True, label="DONE", backgroundColor=done_background_color)
    else:
        cmds.button(button_name, edit=True, label="WARNING!", backgroundColor=warning_background_color, command=lambda *args: clean_up_function_name())
        
# Main UI creation function
def apex_overseer_ui():
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)

    # Create the window
    window = cmds.window(window_name, title="Apex Overseer", widthHeight=(450, 250), sizeable=False)
    main_column = cmds.columnLayout(adjustableColumn=True)
    categories = ["Layers", "Hypershade", "Character Mesh", "Proxy Mesh"]
    
    for category in categories:
        cmds.frameLayout(labelVisible=False, borderVisible=True, mw=5, mh=5)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 100, 100), adjustableColumn=1)
        cmds.text(label=category, align='left')

        if category == "Layers":
            create_layer_button()
        elif category == "Hypershade":
            cmds.button("hypershade_status_button", label="WARNING!", width=100, height=25, backgroundColor=warning_background_color, command=lambda *args: clean_hypershade())
        elif category == "Character Mesh":
            create_character_mesh_button()
        elif category == "Proxy Mesh":
            create_proxy_mesh_button()

        cmds.setParent('..')
        cmds.setParent('..')
    
    cmds.frameLayout(labelVisible=False, borderVisible=True, mw=5, mh=5)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(350, 50), adjustableColumn=1)
    
    # "Fix all warnings" button
    cmds.button(label="Fix all warnings", width=300, height=30, command=lambda *args: run_all_checks())
    
    # "Refresh" button
    cmds.button(label="Refresh", width=100, height=30, command=lambda *args: refresh_ui()) 
    
    # Show the window
    cmds.showWindow(window_name)
# endregion"""

    with open(script_path, 'w') as f:
        f.write(script)

    shelf_buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in shelf_buttons:
        if cmds.objectTypeUI(btn) == 'shelfButton' and cmds.shelfButton(btn, query=True, label=True) == button_name:
            cmds.deleteUI(btn)

    cmds.shelfButton(
        parent=shelf,
        label=button_name,
        image1="eye.png",
        command=f"import maya.cmds as cmds\nimport apex_overseer\n\napex_overseer.apex_overseer_ui()"
    )
    
    mel.eval('saveAllShelves $gShelfTopLevel')
    
    cmds.confirmDialog(title='Success', message="Shelf button created.", button=['OK'])

create_shelf_button()
