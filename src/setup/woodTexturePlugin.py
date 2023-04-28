import sys
sys.path.append(r'C:\Users\37978\AppData\Local\Programs\Python\Python39\Lib\site-packages')
#sys.path.append(r'C:\Users\54040\AppData\Roaming\Python\Python39\site-packages')
#sys.path.append(r'C:\Users\54040\AppData\Local\Programs\Python\Python39\lib\site-packages')
import os
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

import textureGenerator

import maya.mel as mel
import json

class WoodTexGenCmd(OpenMayaMPx.MPxCommand):
    kPluginCmdName = "WoodTexGenCmd"

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

        self.woodType = 1

        self.time = 0
        self.rMin = 0.0
        self.rMax = 0.0

        self.edgetightness = 0.0
        self.knotdistortion = 0.0
        self.liveKnots = 0.0
        self.thickness = 0.0
        
        self.texturePath = r'D:\Upenn\Spring2023\CIS660\Wood_Knot_Editor\src\setup\output.png'
        #self.texturePath = r'C:\Users\54040\Desktop\660\authoringTool\Wood_Knot_Editor\src\setup\output.png'

    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(WoodTexGenCmd())

    def doIt(self, args):
        # Add your command implementation here
        print("CALL WoodTexGenCmd!")
        argData = OpenMaya.MArgParser (self.syntax(), args)

        if argData.isFlagSet ('c'):
            self.woodType = argData.flagArgumentInt('c', 0)

        if argData.isFlagSet ('s'):
            self.time = argData.flagArgumentInt('s', 0)
        if argData.isFlagSet ('m'):
            self.rMin = argData.flagArgumentDouble('m', 0)
        if argData.isFlagSet ('x'):
            self.rMax = argData.flagArgumentDouble('x', 0)

        if argData.isFlagSet ('e'):
            self.edgetightness = argData.flagArgumentDouble('e', 0)
        if argData.isFlagSet ('k'):
            self.knotdistortion = argData.flagArgumentDouble('k', 0)
        if argData.isFlagSet ('l'):
            self.liveKnots = argData.flagArgumentDouble('l', 0)
        if argData.isFlagSet ('t'):
            self.thickness = argData.flagArgumentDouble('t', 0)    

        parameters = {
            'colorMap': self.woodType,
            'time': self.time,
            'rmin': self.rMin,
            'rmax': self.rMax,
            'edgetightness': self.edgetightness,
            'knotdistortion': self.knotdistortion,
            'liveknots': self.liveKnots,
            'thickness': self.thickness
        }

        json_filename = r'D:\Upenn\Spring2023\CIS660\Wood_Knot_Editor\src\setup\parameters.json'
        #json_filename = r'C:\Users\54040\Desktop\660\authoringTool\Wood_Knot_Editor\src\setup\parameters.json'

        with open(json_filename, 'w') as f:
            json.dump(parameters, f)
            print("Write parameters to file path..." + json_filename)

        # Apply the generated texture to the selected object in the scene
        self.apply_texture()

    def apply_texture(self, *args):
        # generate procedual texture
        try:
            print("run generator...")
            textureGenerator.main()
        except Exception as e:
            sys.stderr.write(str(e) + "\n")

        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("Please select at least one object.")
            return

        # Load the image file
        file_node = cmds.shadingNode('file', asTexture=True)
        cmds.setAttr(file_node + '.fileTextureName', self.texturePath, type='string')

        # Create a new shading node
        surface_shader = cmds.shadingNode('surfaceShader', asShader=True)

        # Create a new shading group and assign the material to it
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(surface_shader + '.outColor', shading_group + '.surfaceShader')
        cmds.connectAttr(file_node + '.outColor', surface_shader + '.outColor')

        cmds.sets(selected_objects, edit=True, forceElement=shading_group)

## store the menu name
menuLabel = "WoodTex"

def createMenu(pluginPath):
    woodTexProc = "woodTex"
    try:
        OpenMaya.MGlobal.executeCommand("source \"%s/%s.mel\";" % (pluginPath, woodTexProc))
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
    
def deleteMenu(pluginPath):
    command = "deleteUI \"%s\";" % (menuLabel)
    try:
        OpenMaya.MGlobal.executeCommand(command)
    except Exception as e:
        sys.stderr.write(str(e) + "\n")

# Create an instance of the command.
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(WoodTexGenCmd())

# Syntax creator 
def syntaxCreator(): 
    syntax = OpenMaya.MSyntax()
    # Color parms
    syntax.addFlag('c', 'woodType', OpenMaya.MSyntax.kUnsigned)
    # Texture pattern parms
    syntax.addFlag('s', 'timeSeed', OpenMaya.MSyntax.kUnsigned)
    # Radius parms
    syntax.addFlag('m', 'radiusmin', OpenMaya.MSyntax.kDouble)
    syntax.addFlag('x', 'radiusmax', OpenMaya.MSyntax.kDouble)
    # Knots parms
    syntax.addFlag('e', 'edgetightness', OpenMaya.MSyntax.kDouble)
    syntax.addFlag('k', 'knotdistortion', OpenMaya.MSyntax.kDouble)
    syntax.addFlag('l', 'liveKnots', OpenMaya.MSyntax.kDouble)
    syntax.addFlag('t', 'thickness', OpenMaya.MSyntax.kDouble)

    return syntax 

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(WoodTexGenCmd.kPluginCmdName, cmdCreator, syntaxCreator)
        createMenu(mplugin.loadPath())
    except Exception as e:
        sys.stderr.write(str(e) + "\n")

# Uninitialize the plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(WoodTexGenCmd.kPluginCmdName)
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
