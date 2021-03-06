# From katana plugins/Src/Resources/Examples/UIPlugins/CustomLayeredMenuExample.py
# Modified for use with Laika Shading Library.

"""
Alt+P shading node menu.
Generates a sorted and searchable list of shading nodes in the Node Graph.
"""

from Katana import UI4, NodegraphAPI, LayeredMenuAPI, RenderingAPI, DrawingModule
from RenderingAPI import RenderPlugins


# A list of shading nodes that exist, but that are legacy'd or we otherwise want to hide.
excludeList = [
    'osl/material/v2_PxrSurfaceAdapter',
    'ris/displace/SetP'
]

# A list of shading nodes that should not typically be used.
# Flag them with a yellow color in the displayed list.
yellowList = []

# The list of shading nodes that are preferred replacements for existing shading nodes.
# Typically, these replace those in the yellow list.
blueList = []

# Color dict.
# Sets the node color per shader category.
    # 'integrator'   :[ 0.00, 0.00, 0.00 ],
    # 'lightfilter'  :[ 0.00, 0.00, 0.00 ],
colorDict = {
    'bxdf'         :[ 0.2380, 0.3196, 0.4420 ],
    'convert'      :[ 0.3900, 0.2910, 0.2100 ],
    'data'         :[ 0.2139, 0.3773, 0.4061 ],
    'displace'     :[ 0.2482, 0.2380, 0.4420 ],
    'displayfilter':[ 0.3000, 0.3900, 0.2100 ],
    'manifold'     :[ 0.3968, 0.2232, 0.2232 ],
    'material'     :[ 0.3918, 0.2324, 0.4316 ],
    'parameter'    :[ 0.2821, 0.2170, 0.4030 ],
    'pattern'      :[ 0.2100, 0.3900, 0.3360 ],
    'samplefilter' :[ 0.3900, 0.2100, 0.3180 ],
    'string'       :[ 0.3810, 0.3900, 0.2100 ],
    'texture'      :[ 0.2100, 0.3900, 0.2280 ],
    'utility'      :[ 0.3900, 0.3450, 0.2100 ],
    'vector'       :[ 0.4030, 0.2170, 0.3286 ]
    }


def IkaPopulateCallback( layeredMenu ):
    """
    Callback for the layered menu, which adds entries to the given
    C{layeredMenu} based on the available shading nodes.

    @type layeredMenu: L{LayeredMenuAPI.LayeredMenu}
    @param layeredMenu: The layered menu to add entries to.
    """
    # Obtain a list of names of available PRMan shaders from the PRMan renderer info plug-in.
    rendererInfoPlugin = RenderPlugins.GetInfoPlugin( 'prman' )
    shaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
    shaderNames = rendererInfoPlugin.getRendererObjectNames( shaderType )

    # Iterate over the names of shaders and add a menu entry for each of them to the given layered menu.
    # Note: Can set text to whatever I want the user to see when selecting a shading node.
    for shaderName in shaderNames:
        if( shaderName in excludeList ): continue

        if( shaderName.lower().find( 'lightfilter' ) != -1 ): continue
        if( shaderName.startswith( 'Pxr' ) and shaderName.endswith( 'Light' )): continue

        if( shaderName in yellowList ):
            layeredMenu.addEntry( shaderName, text=shaderName, color=(0.7, 0.7, 0.1) )

        elif( shaderName in blueList ):
            layeredMenu.addEntry( shaderName, text=shaderName, color=(0.4, 0.4, 1.0) )

        elif( shaderName.startswith( 'osl' )):
            layeredMenu.addEntry( shaderName, text=shaderName, color=(0.3, 0.77, 0.57) )

        elif( shaderName.startswith( 'ris' )):
            layeredMenu.addEntry( shaderName, text=shaderName, color=(0.3, 0.65, 0.73) )

        else:
            layeredMenu.addEntry( shaderName, text=shaderName, color=(0.7, 0.3, 0.3) )


def ActionCallback( value ):
    """
    Callback for the layered menu, which creates a PrmanShadingNode node and
    sets its B{nodeType} parameter to the given C{value}, which is the name of
    a PRMan shader as set for the menu entry in L{IkaPopulateCallback()}.

    @type value: C{str}
    @rtype: C{object}
    @param value: An arbitrary object that the menu entry that was chosen
        represents. In our case here, this is the name of a PRMan shader as
        passed to the L{LayeredMenuAPI.LayeredMenu.addEntry()} function in
        L{IkaPopulateCallback()}.
    @return: An arbitrary object. In our case here, we return the created
        PrmanShadingNode node, which is then placed in the B{Node Graph} tab
        because it is a L{NodegraphAPI.Node} instance.
    """

    # Remove ris/ or osl/ prefix from the node name.
    if( value.find( 'ris/' ) == 0 or value.find( 'osl/' ) == 0 ):
        name = value[ 4: ]
    else:
        name = value

    # Create a node containing the chosen type.
    if( name.find( 'integrator' ) == 0 ):
        node = NodegraphAPI.CreateNode( 'PrmanIntegratorSettings', NodegraphAPI.GetRootNode() )

    else:
        node = NodegraphAPI.CreateNode( 'PrmanShadingNode', NodegraphAPI.GetRootNode() )
        node.getParameter( 'nodeType' ).setValue( value, 0 )

    # Set the node's name.
    node.setName( name )
    node.getParameter( 'name' ).setValue( node.getName(), 0 )

    # Set the node's color based on its shader category.
    for category in colorDict:
        if( category in name ):
            color = colorDict[ category ]
            DrawingModule.SetCustomNodeColor( node, color[0], color[1], color[2] )
            break

    # Update the Node Graph.
    for tab in UI4.App.Tabs.GetTabsByType( 'Node Graph' ):
        tab.update()

    return node


# Laika Shading Nodes
ikaLayeredMenu = LayeredMenuAPI.LayeredMenu( IkaPopulateCallback, ActionCallback, 'Alt+P',
                                                alwaysPopulate = False,
                                                onlyMatchWordStart = False
                                                )
LayeredMenuAPI.RegisterLayeredMenu( ikaLayeredMenu, 'Shading Nodes' )
