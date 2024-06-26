bl_info = {
    "name": "ACET Suite",
    "author": "Dad",
    "version": (1, 0, 2),
    "blender": (3, 4, 0),
    "location": "View3D > Sidebar > ACET/Tools",
    "description": "The Assetto Corsa Encryption Tools suite with the main logic, and added utils for loading persistence in older blender versions.",
    "warning": "",
    "doc_url": "https://github.com/13DM/ACET",
    "category": "3D View",
}

import bpy
from . import Assetto_Corsa_Encryption_Tools
from . import ACUtils_Shader

def register():
    Assetto_Corsa_Encryption_Tools.register()
    ACUtils_Shader.register()

def unregister():
    Assetto_Corsa_Encryption_Tools.unregister()
    ACUtils_Shader.unregister()
    
if __name__ == "__main__":
    register()
