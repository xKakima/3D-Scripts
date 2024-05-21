"""
Script created by Michael James Munar
Email: mjmunar.dev@gmail.com
"""
import maya.cmds as cmds
import os

def set_playback_range(start_frame, end_frame):
    cmds.playbackOptions(min=start_frame, max=end_frame)
    cmds.playbackOptions(animationStartTime=start_frame, animationEndTime=end_frame)
    cmds.currentTime(start_frame)

def setup_render_settings(render_mode, width, height):
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mayaHardware2', type='string')
    cmds.setAttr('hardwareRenderingGlobals.multiSampleEnable', 1)
    cmds.setAttr('hardwareRenderingGlobals.ssaoEnable', 1)
    cmds.setAttr('hardwareRenderingGlobals.motionBlurEnable', 0)
    cmds.setAttr('defaultResolution.width', width)
    cmds.setAttr('defaultResolution.height', height)

    # Get the current active panel
    panel = cmds.getPanel(withFocus=True)

    if render_mode == 'wireframe':
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=True)
        cmds.modelEditor(panel, edit=True, wireframeOnShaded=True)  # Wireframe on Shaded
    else:
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=True)  # Shaded and Textured
        cmds.modelEditor(panel, edit=True, wireframeOnShaded=False)  # Ensure wireframe overlay is off

def capture_screenshot(render_mode, output_path):
    setup_render_settings(render_mode, 4096, 4096)
    cmds.playblast(completeFilename=output_path, forceOverwrite=True, format='image', widthHeight=[4096, 4096], showOrnaments=False, offScreen=True, viewer=False)

def render_screenshots(isLOD=False, layerName=None):
    bookmarks = cmds.ls(type='cameraView')
    if not bookmarks:
        cmds.confirmDialog(title='Error', message="No bookmarks found in the scene.", button=['OK'])
        return

    documents_path = os.path.expanduser('~\\Documents')

    output_dir = os.path.join(documents_path, 'Maya_Renders')

    if not os.path.exists(output_dir):
        print("Maya_Renders folder does not exists, will be creating one")
        os.makedirs(output_dir)

    set_playback_range(1, 2)
    for bookmark in bookmarks:
        camera_view_name = os.path.join(output_dir, bookmark)
        shaded_output = camera_view_name + '_shaded.png'
        wire_output = camera_view_name + '_wireframe.png'

        if isLOD:
            wire_output = f"{camera_view_name}_{layerName}.png"

        cmds.cameraView(bookmark, e=True, camera='persp', sc=True )
        print(f"Changing Camera view to {bookmark}")

        if isLOD:
            capture_screenshot('wireframe', wire_output)
        else:
            capture_screenshot('wireframe', wire_output)
            capture_screenshot('shaded', shaded_output)

    cmds.inViewMessage(amg='Render Bookmarks: Render complete!', pos='topCenter', fade=True)
    os.startfile(output_dir)

def render_lods():
    print("Rendering LODs...")
    display_layers = cmds.ls(type='displayLayer')
    display_layers.remove('defaultLayer') if 'defaultLayer' in display_layers else None
    
    visibility_states = {}
    
    # Hide all display layers
    for layer in display_layers:
        visibility_states[layer] = cmds.getAttr(f"{layer}.visibility")
        cmds.setAttr(f"{layer}.visibility", False)
    
    # The actual render loop
    for layer in display_layers:
        cmds.setAttr(f"{layer}.visibility", True)
        render_screenshots(isLOD=True, layerName=layer)
        cmds.setAttr(f"{layer}.visibility", False)
        
    # Reset state of display layers' visibility
    for layer, state in visibility_states.items():
        cmds.setAttr(f"{layer}.visibility", state)
    

def prompt_render_choice():
    result = cmds.confirmDialog(
        title='Render Options',
        message='Choose a render option:',
        button=['Render LODs', 'Render Lowpoly'],
        defaultButton='Render Lowpoly',
        cancelButton='Cancel',
        dismissString='Cancel'
    )

    if result == 'Render LODs':
        render_lods()
    elif result == 'Render Lowpoly':
        render_screenshots()
    elif result == 'Cancel':
        print("Render operation cancelled.")

# Create a shelf button for the script
def create_shelf_button():
    shelf = "VenTools" 
    button_name = "Render Bookmarks"
    
    if not cmds.shelfLayout(shelf, q=True, ex=True):
        cmds.confirmDialog(title='Error', message=f"Shelf '{shelf}' does not exist.", button=['OK'])
        return

    # Check if the button already exists in the shelf
    shelf_buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in shelf_buttons:
        if cmds.objectTypeUI(btn) == 'shelfButton' and cmds.shelfButton(btn, query=True, label=True) == button_name:
            cmds.deleteUI(btn)
    
    # Create the button if it does not exist
    cmds.shelfButton(
        parent=shelf,
        label=button_name,
        image1="render.png",
        command="import maya.cmds as cmds; from __main__ import prompt_render_choice; prompt_render_choice()"  # Call the prompt function
    )
    cmds.confirmDialog(title='Success', message="Shelf button created.", button=['OK'])

# Run the function to create the shelf button
create_shelf_button()
