import maya.OpenMaya as OpenMaya
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import math

def create_vertex_and_fragment_shader():
    # Get the active view and render target
    view = OpenMayaUI.M3dView.active3dView()
    render_target = view.getRenderTarget()

    # Create a shader manager and generator
    shader_manager = OpenMayaRender.MHWRender.MShaderManager.getInstance()
    shader_generator = shader_manager.getShaderGenerator()

    # Create a vertex shader source string
    vertex_shader_source = """
        uniform float time;
        uniform float amplitude;
        in vec3 position;
        in vec3 normal;
        out vec3 worldPosition;
        out vec3 worldNormal;
        void main()
        {
            vec4 worldPos = gl_ModelViewMatrix * vec4(position, 1.0);
            vec4 worldNormal4 = gl_NormalMatrix * vec4(normal, 1.0);
            worldPosition = worldPos.xyz ;
            worldNormal = normalize(worldNormal4.xyz);
            gl_Position = gl_ModelViewProjectionMatrix * vec4(worldPosition, 1.0);
        }
    """

    # Create a fragment shader source string
    fragment_shader_source = """
        in vec3 worldPosition;
        in vec3 worldNormal;
        out vec4 fragColor;
        void main()
        {
            fragColor = vec4(1,0.5,0.5,1.0);
        }
    """

    # Create a vertex shader
    vertex_shader = shader_generator.generateShader(
        vertex_shader_source,
        "vertex",
        "",
        "",
        "",
        render_target
    )

    # Create a fragment shader
    fragment_shader = shader_generator.generateShader(
        fragment_shader_source,
        "",
        "fragment",
        "",
        "",
        render_target
    )

    # Set shader parameters
    time = cmds.currentTime(q=True)
    amplitude = 0.1
    time_uniform = vertex_shader.getUniformParameter("time")
    amplitude_uniform = vertex_shader.getUniformParameter("amplitude")
    time_uniform.setFloat(time)
    amplitude_uniform.setFloat(amplitude)

    # Set the shader on the selected object(s)
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)
    for i in range(selection.length()):
        dag_path = OpenMaya.MDagPath()
        selection.getDagPath(i, dag_path)
        render_item = OpenMayaRender.MRenderItem(
            "custom_vertex_and_fragment_shader",
            OpenMayaRender.MGeometry.kPoints,
            OpenMayaRender.MGeometry.kAll,
            OpenMayaRender.MGeometry.kOpaque,
            dag_path
        )
        render_item.setShader(vertex_shader)
        render_item.setShader(fragment_shader)
        render_target.addItem(render_item)
