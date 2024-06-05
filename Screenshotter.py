"""
Script created by Michael James Munar
Email: mjmunar.dev@gmail.com
"""
import maya.cmds as cmds
import maya.mel as mel
import os

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
    button_name = "Render Bookmarks"
    
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
        
    script_path = os.path.join(scripts_folder, 'screenshot_tool.py')
    
    script = """import maya.cmds as cmds
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

    panel = cmds.getPanel(withFocus=True)

    if render_mode == 'wireframe':
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=True)
        cmds.modelEditor(panel, edit=True, wireframeOnShaded=True)
    else:
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=True)
        cmds.modelEditor(panel, edit=True, wireframeOnShaded=False)

def capture_screenshot(render_mode, output_path):
    setup_render_settings(render_mode, 4096, 4096)
    cmds.playblast(completeFilename=output_path, forceOverwrite=True, format='image', widthHeight=[4096, 4096], showOrnaments=False, offScreen=True, viewer=False)

def render_screenshots(isLOD=False, layerName=None):
    cmds.lookThru('persp')
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
    
    for layer in display_layers:
        visibility_states[layer] = cmds.getAttr(f"{layer}.visibility")
        cmds.setAttr(f"{layer}.visibility", False)
    
    for layer in display_layers:
        cmds.setAttr(f"{layer}.visibility", True)
        render_screenshots(isLOD=True, layerName=layer)
        cmds.setAttr(f"{layer}.visibility", False)
        
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
        print("Render operation cancelled.")"""
    with open(script_path, 'w') as f:
        f.write(script)

    shelf_buttons = cmds.shelfLayout(shelf, query=True, childArray=True) or []
    for btn in shelf_buttons:
        if cmds.objectTypeUI(btn) == 'shelfButton' and cmds.shelfButton(btn, query=True, label=True) == button_name:
            cmds.deleteUI(btn)

    cmds.shelfButton(
        parent=shelf,
        label=button_name,
        image1="render.png",
        command=f"import maya.cmds as cmds\nimport screenshot_tool\n\nscreenshot_tool.prompt_render_choice()"
    )
    
    mel.eval('saveAllShelves $gShelfTopLevel')
    
    cmds.confirmDialog(title='Success', message="Shelf button created.", button=['OK'])

create_shelf_button()
