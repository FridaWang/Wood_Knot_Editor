import sys

import maya.OpenMaya as OpenMaya
import maya.cmds as cmds

class TexturePlugin:
    def __init__(self):
        self.window_name = "Texture Plugin"
        self.image_path = None
        self.default_path = 'D:/Upenn/Spring2023/CIS660/Authoring_tool/Textures/light_wood_texture.jpg'

    def create_ui(self):
        # Create a window with a file browser
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        window = cmds.window(self.window_name, title="Texture Generator")
        cmds.columnLayout(adjustableColumn=True)
        cmds.textFieldButtonGrp("file_path", label='Image File', text = self.default_path, buttonLabel='Browse', bc=self.load_image_file)
        cmds.floatSliderGrp("transparency_slider", label="Transparency", min=0.0, max=1.0, value=0.0, step=0.1)
        cmds.button(label="Apply Texture", command=self.apply_texture)
        cmds.showWindow(window)

    def apply_texture(self, *args):
        if not self.image_path:
            # Use default texture
            self.image_path = self.default_path

        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("Please select at least one object.")
            return

        print(self.image_path)

        # Load the image file
        file_node = cmds.shadingNode('file', asTexture=True)
        cmds.setAttr(file_node + '.fileTextureName', self.image_path, type='string')

        # Create a new shading node
        surface_shader = cmds.shadingNode('surfaceShader', asShader=True)

        # Create a new shading group and assign the material to it
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(surface_shader + '.outColor', shading_group + '.surfaceShader')
        cmds.connectAttr(file_node + '.outColor', surface_shader + '.outColor')

        transparency_value = cmds.floatSliderGrp("transparency_slider", q=True, value=True)
        cmds.setAttr(surface_shader + ".outTransparency", transparency_value, transparency_value, transparency_value, type="double3")

        cmds.sets(selected_objects, edit=True, forceElement=shading_group)

    def load_image_file(self, *args):
        file_path = cmds.fileDialog2(fileMode=1, caption="Select Image File", fileFilter="Image Files (*.jpg *.png *.bmp)")
        if file_path:
            self.image_path = file_path[0]
            cmds.textFieldButtonGrp("file_path", edit=True, text=self.image_path)


def load_plugin(*args):
    tp = TexturePlugin()
    tp.create_ui()

## store the menu name
menuName = "Wood Tex"

def createMenu():
    if cmds.menu(menuName, exists=True):
        cmds.deleteUI(menuName)

    menu = cmds.menu(menuName, label="Procedural Wood Texture", parent="MayaWindow")
    cmds.menuItem(label="Apply defult texture", command=load_plugin, parent=menu)

def deleteMenu():
    if cmds.menu(menuName, exists=True):
        cmds.deleteUI(menuName)

# Register the plug-in
def initializePlugin(plugin):
    print("Initializing plugin...")
    try:
        createMenu()
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
       
# Unregister the plug-in
def uninitializePlugin(plugin):
    try:
        print("Uninitializing plugin...")
        deleteMenu()
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        


