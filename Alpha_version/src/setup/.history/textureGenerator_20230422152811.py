import sys
import os
import OpenGL.GL.shaders
import numpy as np
import math
import pyrr
import openmesh as om
from PIL import Image #, ImageDraw, ImageOps
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import imageio
import json

import glfw

def load_texture(i, path, nearest=False, repeat_x_edge=False):
    gltex = [GL_TEXTURE0, GL_TEXTURE1, GL_TEXTURE2, GL_TEXTURE3, GL_TEXTURE4, GL_TEXTURE5, GL_TEXTURE6, GL_TEXTURE7]
    image = Image.open(path)
    width = int(image.size[0])
    height = int(image.size[1])
    number_of_channels=3
    tex = np.array(image.getdata()).reshape(width, height, number_of_channels)
    tex = np.array(list(tex), np.uint8)
    glActiveTexture(gltex[i])
    tex_handle = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_handle)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, tex)

    if nearest:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    else:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    if repeat_x_edge:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    else:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

def main():
    
    print(OpenGL.__file__)
    #parm_path = r'C:\Users\54040\Desktop\660\authoringTool\Wood_Knot_Editor\Alpha_version\src\setup\parameters.json'
    parm_path = r'D:\Upenn\Spring2023\CIS660\Wood_Knot_Editor\Alpha_version\src\setup\parameters.json'
    p_file = open(parm_path)
    data = json.load(p_file)
    edgetightness = data['edgetightness']
    knotdistortion = data['knotdistortion']
    liveknots = data['liveknots']
    deadKnots = data['deadKnots']
    thickness = data['thickness']
    # custom_time = data['time']
    # custom_rmin = data['rmin']
    # custom_rmax = data['rmax']
    custom_colormap = data['colorMap']

    # print("----------------------------------------------------")
    # print(custom_time, custom_rmin, custom_rmax, custom_colormap)

    ### WINDOW SETUP ###########################################################

    if not glfw.init():
        return
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    width = height = 600
    window = glfw.create_window(width, height, "Procedural Knots", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    ### LOAD INPUT 3D MODEL ####################################################

    #parent_path = r'C:\Users\54040\Desktop\660\authoringTool\Wood_Knot_Editor\Alpha_version\src'
    parent_path = r'D:\Upenn\Spring2023\CIS660\Wood_Knot_Editor\Alpha_version\src'
    #mesh = om.read_trimesh(parent_path+'\\3d_model\\cube.obj', vertex_normal=True)
    mesh = om.read_trimesh(parent_path + '\\3d_model\\plank.obj', vertex_normal=True)

    #Vertices with normals
    point_array = mesh.points()
    normal_array = mesh.vertex_normals()
    vertex_array = np.concatenate((point_array, normal_array), axis=1) # [x,y,z] + [nx,ny,nz] --> [x,y,z,nx,ny,nz]
    verts = np.array(vertex_array.flatten(), dtype=np.float32)

    #Face indices
    face_array = mesh.face_vertex_indices()
    indices = np.array(face_array.flatten(), dtype = np.uint32)

    # Buffer vertices and indices
    #store vertices
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, 4*len(verts), verts, GL_DYNAMIC_DRAW)

    #store indices
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4*len(indices), indices, GL_DYNAMIC_DRAW)

    # Vertex attribute pointers
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0)) #position
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12)) #normal
    glEnableVertexAttribArray(1)

    ### LOAD VERTEX AND FRAGEMENT SHADERS FROM EXTERNAL FILES ##################

    #VERTEX_SHADER = open("main.vert",'r').read()
    VERTEX_SHADER = open(parent_path+'\\setup\\main.vert','r').read()

    FRAGMENT_SHADER = open(parent_path+'\\setup\\main.frag','r').read()

    # Compile The Program and shaders

    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))

    #Customize: Create a framebuffer and bind it
    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    #Customize: Create a texture to store the output
    output_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, output_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    #Customize: Attach the texture to the framebuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output_texture, 0)
    #Customize: Check if the framebuffer is complete
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print("Error: Framebuffer is not complete!")
        glfw.terminate()
        exit()


    ### LOAD TEXTURE MAPS ######################################################

    glEnable(GL_TEXTURE_2D)
    # print("customColorMap:")
    # print(custom_colormap)
    # Wood colors etc.
    if (custom_colormap == 1):
        print("color1")
        load_texture(0, parent_path + '\\wood_color_maps\\wood_bar_color.bmp')
    elif (custom_colormap == 2):
        print("color2")
        load_texture(0, parent_path+'\\wood_color_maps\\color1.bmp')
    elif (custom_colormap == 3):
        print("color3")
        load_texture(0, parent_path+'\\wood_color_maps\\color2.bmp')
    elif (custom_colormap == 4):
        print("color4")
        load_texture(0, parent_path+'\\wood_color_maps\\color3.bmp')
    elif (custom_colormap == 5):
        print("color5")
        load_texture(0, parent_path+'\\wood_color_maps\\color4.bmp')
    #load_texture(0, parent_path+'\\wood_color_maps\\wood_bar_color.bmp')
    #load_texture(0, parent_path+'\\wood_color_maps\\color4.bmp')
    load_texture(1, parent_path+'\\wood_color_maps\\wood_bar_specular.bmp')
    load_texture(2, parent_path+'\\wood_color_maps\\wood_bar_normal.bmp')

    # Internal tree log skeleton geometry
    load_texture(3, parent_path+'\\tree_geo_maps\\pith_and_radius_map.bmp',repeat_x_edge=True)
    load_texture(4, parent_path+'\\tree_geo_maps\\knot_height_map.bmp')
    load_texture(5, parent_path+'\\tree_geo_maps\\knot_orientation_map.bmp')
    load_texture(6, parent_path+'\\tree_geo_maps\\knot_state_map.bmp',nearest=True)

    glUseProgram(shader)

    texLocCol = glGetUniformLocation(shader,'ColorMap')
    glUniform1i(texLocCol, 0)
    texLocSpec = glGetUniformLocation(shader,'SpecularMap')
    glUniform1i(texLocSpec, 1)
    texLocNorm = glGetUniformLocation(shader,'NormalMap')
    glUniform1i(texLocNorm, 2)
    texLocNorm = glGetUniformLocation(shader,'PithRadiusMap')
    glUniform1i(texLocNorm, 3)
    texLocNorm = glGetUniformLocation(shader,'KnotHeightMap')
    glUniform1i(texLocNorm, 4)
    texLocNorm = glGetUniformLocation(shader,'KnotOrientMap')
    glUniform1i(texLocNorm, 5)
    texLocNorm = glGetUniformLocation(shader,'KnotStateMap')
    glUniform1i(texLocNorm, 6)

    ### SET SHADER PARAMETERS ##################################################

    # Set tree log properties
    f = open(parent_path+'//tree_geo_maps//map_params.json')
    rmin, rmax, hmax, knum = json.load(f)
    # rmin = custom_rmin
    # rmax = custom_rmax
    f.close()
    print(rmin, rmax, hmax, knum)

    rminLoc = glGetUniformLocation(shader, "rmin")
    glUniform1f(rminLoc, rmin)
    rmaxLoc = glGetUniformLocation(shader, "rmax")
    glUniform1f(rmaxLoc, rmax)
    hmaxLoc = glGetUniformLocation(shader, "hmax")
    glUniform1f(hmaxLoc, hmax)
    knumLoc = glGetUniformLocation(shader, "N")
    glUniform1i(knumLoc, knum)

    #customize parameters

    k_b = edgetightness
    k_s = knotdistortion
    #knotColor = np.array([0.20,0.20,0.15])
    dead_color_factor = deadKnots
    dead_outline_factor = 1.0
    dead_outline_thickness = thickness
    k_sLoc = glGetUniformLocation(shader, "k_s")
    glUniform1f(k_sLoc, k_s)

    k_bLoc = glGetUniformLocation(shader, "k_b")
    glUniform1f(k_bLoc, k_b)

    knotColorLoc = glGetUniformLocation(shader, "knotColor")
    glUniform3f(knotColorLoc, liveknots, liveknots, liveknots)

    dead_color_factorLoc = glGetUniformLocation(shader, "dead_color_factor_default")
    glUniform1f(dead_color_factorLoc, dead_color_factor)

    dead_outline_factorLoc = glGetUniformLocation(shader, "dead_outline_factor_default")
    glUniform1f(dead_outline_factorLoc, dead_outline_factor)

    dead_outline_thicknessLoc = glGetUniformLocation(shader, "dead_outline_thickness_default")
    glUniform1f(dead_outline_thicknessLoc, dead_outline_thickness)

    # Model matrix
    mrot = 0.0
    model = np.array(pyrr.Matrix44.from_z_rotation(mrot));
    modelLoc = glGetUniformLocation(shader, "model")
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, model)

    # View matrix
    rot_x = pyrr.Matrix44.from_x_rotation(-4.71)
    rot_z = pyrr.Matrix44.from_z_rotation(0.0)
    view = np.array(rot_x*rot_z);
    viewLoc = glGetUniformLocation(shader, "view")
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, view)

    # View position
    view_pos_vec = np.array([0.0, 0, 3.0, 0.0],dtype=np.float32)
    view_pos_vec = view*view_pos_vec;
    viewPosLoc = glGetUniformLocation(shader, "viewPos")
    glUniform3f(viewPosLoc, -1.5, 2.0, -1.0);

    # Light position
    lrot = 5.2
    light_pos_vec = np.array(np.array([math.cos(lrot), math.sin(lrot), 1.2]), dtype = np.float32)
    lightPosLoc = glGetUniformLocation(shader, "lightPos")
    glUniform3f(lightPosLoc, light_pos_vec[0], light_pos_vec[1], light_pos_vec[2])

    ### DRAW ###################################################################

    glClearColor(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # while not glfw.window_should_close(window):

    #glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Pass time variable to fragment shader (for animation)
    timeLoc = glGetUniformLocation(shader, "time")
    #glUniform1f(timeLoc, glfw.get_time())
    glUniform1f(timeLoc, 590.0)
    #glUniform1f(timeLoc, custom_time)


    # Draw mesh
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT,  None)

    # Swap buffers
    glfw.swap_buffers(window)

    #Customize: Read the pixels from the framebuffer into a NumPy array
    pixels = glReadPixels(0, 0, height, width, GL_RGBA, GL_UNSIGNED_BYTE)
    image_data = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, 4)
    imageio.imwrite(parent_path+'//setup//output.png', np.flipud(image_data))
    glDeleteTextures(1, [output_texture])
    glDeleteFramebuffers(1, [framebuffer])
    glDeleteProgram(shader)
    glfw.terminate()

if __name__ == "__main__":
    main()