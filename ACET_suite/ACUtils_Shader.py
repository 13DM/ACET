#bl_info = {
#    "name": "ACUtils",
#    "author": "Dad",
#    "version": (1, 0, 0),
#    "blender": (3, 4, 0),
#    "location": "View3D > Sidebar > Tool",
#    "description": "Load persistence from ini and handle transparency of objects.",
#    "warning": "",
#    "doc_url": "",
#    "category": "3D View",
#}

import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, FileSelectParams
from .ACET_File_Ops import run_fbx_converter, run_kn5_converter

def clear_principled_bsdf_inputs(node):
    if node.type == 'BSDF_PRINCIPLED':
        for input in node.inputs:
            if input.type == 'RGBA':
                input.default_value = (0.0, 0.0, 0.0, 1.0)
            elif input.type == 'VALUE':
                input.default_value = 0.0
            elif input.type == 'NORMAL':
                input.default_value = (0.0, 0.0, 1.0)
            elif input.type == 'VECTOR':
                input.default_value = (0.0, 0.0, 0.0)

def configure_ac_shader():
    # Handle the texture conversion and node connections
    for material in bpy.data.materials:
        if material.use_nodes:
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            
            # On configuration create all the appropriate shader nodes
            # Set all nodes to none prior to trying to see if they exist
            normal_map_node = None
            separate_color_node = None
            math1_node = None
            math2_node = None
            mapping_node = None
            tc_node = None
            detail_mult_node = None
            detail_mix_node = None
            alpha_mix_node = None
            pbr_mapping_node = None
            pbr_tc_node = None
            pbr_mult_node = None
            ksmaterial_node = None
            detail_normal_mix_node = None
            
            img_tex_1_node = None
            img_tex_2_node = None
            img_tex_3_node = None
            img_tex_4_node = None
            img_tex_5_node = None
            img_tex_6_node = None
            img_tex_7_node = None
            img_tex_8_node = None
            
            principled_bsdf_node = None
            mat_output_node = None
                            
            
            # If nodes exist set them appropriately
            for node in nodes:
                if node.name == "Normal Map 1":
                    normal_map_node = node
                if node.name == "TxtMap Separate Color":
                    separate_color_node = node
                if node.name == "TxtMap Math 1":
                    math1_node = node
                if node.name == "TxtMap Math 2":
                    math2_node = node
                if node.name == "Detail Mapping":
                    mapping_node = node
                if node.name == "Detail Texture Coordinate":
                    tc_node = node
                if node.name == "Detail Multiplier":
                    detail_mult_node = node
                if node.name == "Detail Mix":
                    detail_mix_node = node
                if node.name == "Blend Alpha Mix":
                    alpha_mix_node = node
                if node.name == "PBRMapping":
                    pbr_mapping_node = node
                if node.name == "PBRTexture Coordinate":
                    pbr_tc_node = node
                if node.name == "PBRMultiplier":
                    pbr_mult_node = node
                if node.name == "ksMaterial Details":
                    ksmaterial_node = node
                if node.name == "Detail Normal Mix":
                    detail_normal_mix_node = node
                if node.name == "Image Texture":
                    img_tex_1_node = node
                if node.name == "Image Texture.001":
                    img_tex_2_node = node
                if node.name == "Image Texture.002":
                    img_tex_3_node = node
                if node.name == "Image Texture.003":
                    img_tex_4_node = node
                if node.name == "Image Texture.004":
                    img_tex_5_node = node
                if node.name == "Image Texture.005":
                    img_tex_6_node = node
                if node.name == "Image Texture.006":
                    img_tex_7_node = node
                if node.name == "Image Texture.007":
                    img_tex_8_node = node
                if node.type == 'BSDF_PRINCIPLED' and node.name == 'Principled BSDF':
                    principled_bsdf_node = node
                if node.name == "Material Output":
                    mat_output_node = node
            
            # Create Nodes if not exist
            if not normal_map_node:
                # Add a Normal Map node
                normal_map_node = nodes.new(type='ShaderNodeNormalMap')
                normal_map_node.name = "Normal Map 1"
                # Position the new node
                normal_map_node.location = node.location
                normal_map_node.location.x = 10
                normal_map_node.location.y = -423
            
            if separate_color_node is None:
                # Add a Separate Color node
                separate_color_node = nodes.new(type='ShaderNodeSeparateColor')
                separate_color_node.name = "TxtMap Separate Color"
                
                # Set Location
                separate_color_node.location = node.location
                separate_color_node.location.x = -200
                separate_color_node.location.y = -610
                
            if math1_node is None:
                # Add a first Math node
                math1_node = nodes.new(type='ShaderNodeMath')
                math1_node.name = "TxtMap Math 1"
                
                # Set default values
                math1_node.operation = 'MULTIPLY'
                math1_node.inputs[1].default_value = -1
                
                # Set Location
                math1_node.location = node.location
                math1_node.location.y = -610
                math1_node.location.x = 10
                
            if math2_node is None:
                # Add a second Math node
                math2_node = nodes.new(type='ShaderNodeMath')
                math2_node.name = "TxtMap Math 2"
                
                # Set default values
                math2_node.operation = 'MULTIPLY'
                math2_node.inputs[1].default_value = 1
                
                # Set Location
                math2_node.location = node.location
                math2_node.location.y = -610
                math2_node.location.x = 190
            
            if not mapping_node:
                # Add node
                mapping_node = nodes.new(type='ShaderNodeMapping')
                mapping_node.name = "Detail Mapping"
            
                # Position the new node
                mapping_node.location = node.location
                mapping_node.location.x = -1120
                mapping_node.location.y = 74
                
            if not tc_node:
                # Add node
                tc_node = nodes.new(type='ShaderNodeTexCoord')
                tc_node.name = "Detail Texture Coordinate"
            
                # Position the new node
                tc_node.location = node.location
                tc_node.location.x = -1300
                tc_node.location.y = 74    
                
            if not detail_mult_node:
                # Add nodw
                detail_mult_node = nodes.new(type='ShaderNodeValue')
                detail_mult_node.name = "Detail Multiplier"
            
                # Position the new node
                detail_mult_node.location = node.location
                detail_mult_node.location.x = -1310
                detail_mult_node.location.y = -196
                
                # Set Default Value
                detail_mult_node.outputs[0].default_value = 0.5   
                
            if not detail_mix_node:
                # Add a Normal Map node
                detail_mix_node = nodes.new(type='ShaderNodeMix')
                detail_mix_node.name = "Detail Mix"
            
                # Position the new node for clarity (optional)
                detail_mix_node.location = node.location
                detail_mix_node.location.x = 10
                detail_mix_node.location.y = 570
                
                # Set Default Value
                detail_mix_node.data_type = 'RGBA'
                detail_mix_node.blend_type = 'MIX'
                detail_mix_node.clamp_factor = 0
                detail_mix_node.clamp_result = 0
                detail_mix_node.factor_mode = 'NON_UNIFORM'       
            
            if not alpha_mix_node:
                # Add node
                alpha_mix_node = nodes.new(type='ShaderNodeMix')
                alpha_mix_node.name = "Blend Alpha Mix"
            
                # Position the new node
                alpha_mix_node.location = node.location
                alpha_mix_node.location.x = -175
                alpha_mix_node.location.y = 570
                
                #
                alpha_mix_node.data_type = 'FLOAT'
            
            if not pbr_mapping_node:
                # Add a Normal Map node
                pbr_mapping_node = nodes.new(type='ShaderNodeMapping')
                pbr_mapping_node.name = "PBRMapping"
            
                # Position the new node for clarity (optional)
                pbr_mapping_node.location = node.location
                pbr_mapping_node.location.x = -1120
                pbr_mapping_node.location.y = -300
                
            if not pbr_tc_node:
                # Add a Normal Map node
                pbr_tc_node = nodes.new(type='ShaderNodeTexCoord')
                pbr_tc_node.name = "PBRTexture Coordinate"
            
                # Position the new node for clarity (optional)
                pbr_tc_node.location = node.location
                pbr_tc_node.location.x = -1300
                pbr_tc_node.location.y = -300    
                
            if not pbr_mult_node:
                # Add a Normal Map node
                pbr_mult_node = nodes.new(type='ShaderNodeValue')
                pbr_mult_node.name = "PBRMultiplier"
            
                # Position the new node for clarity (optional)
                pbr_mult_node.location = node.location
                pbr_mult_node.location.x = -1310
                pbr_mult_node.location.y = -570
                
                # Set Default Value
                pbr_mult_node.outputs[0].default_value = 1
                    
            # Add the ksMaterial detail node to each material if not found
            if not ksmaterial_node:
            
                # Create a new custom node group
                node_group = bpy.data.node_groups.new(type='ShaderNodeTree', name='ksMaterial_Details')
                
                # Create input sockets for checkboxes
                input_names = ["Is Base Color", "Is Normal", "Is Texture Map", "Is Detail", "Is PBR", "Is Transparent"]
                for i, input_name in enumerate(input_names):
                    node_group.inputs.new('NodeSocketBool', input_name)
                
                # Create input sockets for float properties
                node_group.inputs.new('NodeSocketFloat', "Detail Mult")
                node_group.inputs.new('NodeSocketFloat', "PBR Mult")
                
                # Get the active material (change this to match your requirements)
                material = material
                
                # Create a shader node using the custom node group
                custom_shader_node = material.node_tree.nodes.new('ShaderNodeGroup')
                custom_shader_node.node_tree = node_group  # Set the custom node group
                custom_shader_node.name = "ksMaterial Details"
                
                # Position the node in the node editor (optional)
                custom_shader_node.location = (-1300, 500)
                
                custom_shader_node.inputs[0].default_value = True
                
            if not detail_normal_mix_node:
                # Add a Normal Map node
                detail_normal_mix_node = nodes.new(type='ShaderNodeMix')
                detail_normal_mix_node.name = "Detail Normal Mix"
            
                # Position the new node for clarity (optional)
                detail_normal_mix_node.location = node.location
                detail_normal_mix_node.location.x = 300
                detail_normal_mix_node.location.y = -130
                
                # Set Default Value
                detail_normal_mix_node.data_type = 'RGBA'
                detail_normal_mix_node.blend_type = 'MIX'
                detail_normal_mix_node.clamp_factor = 0
                detail_normal_mix_node.clamp_result = 0
                detail_normal_mix_node.factor_mode = 'NON_UNIFORM'  
    
            if not img_tex_1_node:
                img_tex_1_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_1_node.name = 'Image Texture'
                img_tex_1_node.location.x = -300
                img_tex_1_node.location.y = 300
                img_tex_1_node.width = 240
    
            if not img_tex_2_node:
                img_tex_2_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_2_node.name = 'Image Texture.001'
                img_tex_2_node.location.x = -300
                img_tex_2_node.location.y = 0
                img_tex_2_node.width = 240
    
            if not img_tex_3_node:
                img_tex_3_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_3_node.name = 'Image Texture.002'
                img_tex_3_node.location.x = -300
                img_tex_3_node.location.y = -300
                img_tex_3_node.width = 240
    
            if not img_tex_4_node:
                img_tex_4_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_4_node.name = 'Image Texture.003'
                img_tex_4_node.location.x = -600
                img_tex_4_node.location.y = 300
                img_tex_4_node.width = 240
    
            if not img_tex_5_node:
                img_tex_5_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_5_node.name = 'Image Texture.004'
                img_tex_5_node.location.x = -600
                img_tex_5_node.location.y = 0
                img_tex_5_node.width = 240
    
            if not img_tex_6_node:
                img_tex_6_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_6_node.name = 'Image Texture.005'
                img_tex_6_node.location.x = -600
                img_tex_6_node.location.y = -300
                img_tex_6_node.width = 240
    
            if not img_tex_7_node:
                img_tex_7_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_7_node.name = 'Image Texture.006'
                img_tex_7_node.location.x = -900
                img_tex_7_node.location.y = 0
                img_tex_7_node.width = 240
    
            if not img_tex_8_node:
                img_tex_8_node = nodes.new(type='ShaderNodeTexImage')
                img_tex_8_node.name = 'Image Texture.007'
                img_tex_8_node.location.x = -900
                img_tex_8_node.location.y = -300
                img_tex_8_node.width = 240
            
            img_tex_1_node.location.x = -300
            img_tex_1_node.location.y = 300
            img_tex_1_node.width = 240
   
            img_tex_2_node.location.x = -300
            img_tex_2_node.location.y = 0
            img_tex_2_node.width = 240
   
            img_tex_3_node.location.x = -300
            img_tex_3_node.location.y = -300
            img_tex_3_node.width = 240
   
            img_tex_4_node.location.x = -600
            img_tex_4_node.location.y = 300
            img_tex_4_node.width = 240
   
            img_tex_5_node.location.x = -600
            img_tex_5_node.location.y = 0
            img_tex_5_node.width = 240
   
            img_tex_6_node.location.x = -600
            img_tex_6_node.location.y = -300
            img_tex_6_node.width = 240
   
            img_tex_7_node.location.x = -900
            img_tex_7_node.location.y = 0
            img_tex_7_node.width = 240
   
            img_tex_8_node.location.x = -900
            img_tex_8_node.location.y = -300
            img_tex_8_node.width = 240
            
            #clear_principled_bsdf_inputs(principled_bsdf_node)
            links.new(principled_bsdf_node.outputs[0], mat_output_node.inputs[0])


#ini related parts of the code

def main_ini_processer(ini_filepath):
    #DEBUG - ini_filepath = "D:/SteamLibrary/steamapps/common/assettocorsa/content/cars/kyu_nissan_s15_msports_kyuspec/kyu_s15_msports_kyu.fbx.ini"
    configure_ac_shader()
    material_data = custom_ini_parser(ini_filepath)
    apply_material_settings_from_ini(material_data, ini_filepath)
    
            
def custom_ini_parser(filepath):
    material_data = {}
    current_section = None
    
    with open(filepath, 'r', errors='ignore') as file:
        for line in file:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]  # Extract section name
                material_data[current_section] = {'textures': {}, 'vars': {}}
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                if key == 'NAME':
                    material_data[current_section]['name'] = value
                elif key.startswith('VAR_') and key.endswith('_NAME'):
                    var_index = key.split('_')[1]
                    material_data[current_section]['vars'][var_index] = {'name': value}
                elif key.startswith('VAR_') and key.endswith('_FLOAT1'):
                    var_index = key.split('_')[1]
                    material_data[current_section]['vars'][var_index]['float1'] = value
                elif key.startswith('RES_') and key.endswith('_TEXTURE'):
                    res_index = key.split('_')[1]
                    material_data[current_section]['textures'][res_index] = value
                else:
                    material_data[current_section][key] = value

    return material_data
    
def apply_material_settings_from_ini(material_data, ini_filepath):
    # Similar implementation as before, but using the custom parsed data
    print(f"{material_data}")
    
    tex_names = []
    
    ini_path, ini_file = os.path.split(ini_filepath)
    texture_directory = os.path.join(ini_path, "texture")
    
    Error_result = ''

    for key, value in material_data.items():
        if key.startswith('MATERIAL_'):
            print(f"Material: {value.get('name')}")
            print(f"--Material Shader: {value.get('SHADER')}")
            print(f"--Material Texture Count: {value.get('RESCOUNT')}")
            
            # Set Variables for shader things
            _currentMatName = str(value.get('name'))
            _currentMat = None
            _currentDetailMult = None
            _currentDetailNMMult = None
            _useDetail = False
            _currentDetailNormalBlend = None
            
            if tex_names is not None:
                tex_names.clear()
            
            # Get the material we are working with through the ini file and see if it exists in the file
            if bpy.data.materials.get(_currentMatName):
                _currentMat = bpy.data.materials.get(_currentMatName)
            else:
                _currentMat = None
                
            # If material is not found, skip this iteration
            if _currentMat is None:
                continue
            
            _currentShader = value.get('SHADER')
            # Fix Alpha Blend Value as boolean
            _currentAlphaBlend = False
            if int(value.get('ALPHABLEND')) > 0:
                _currentAlphaBlend = True
            else:
                _currentAlphaBlend = False
                
            print(f"--Material Alpha Blend: {_currentAlphaBlend}")
            # Fix Alpha Test Value as boolean
            _currentAlphaTest = False
            if value.get('APLHATEST') == None:
                if int(value.get('ALPHATEST')) > 0:
                    _currentAlphaTest = True
                else:
                    _currentAlphaTest = False
            else:
                if int(value.get('APLHATEST')) > 0:
                    _currentAlphaTest = True
                else:
                    _currentAlphaTest = False
            
            print(f"--Material Alpha Test: {_currentAlphaTest}")
            
            # Get the total number of images for the material
            _currentTextureCount = value.get('RESCOUNT')
            
            vars = value.get('vars')
            vv1_prev = None  # Initialize vv1_prev here
            if vars:
                for var_key, var_value in vars.items():
                    for var_key1, var_value1 in var_value.items():
                        if vv1_prev is None:
                            # Store the ambient value for the next iteration
                            vv1_prev = var_value.get('name')
                        else:
                            if vv1_prev is not None:
                                if vv1_prev == "normalUVMultiplier":
                                    _currentDetailNMMult = float(var_value1)
                                if vv1_prev == "detailUVMultiplier":
                                    _currentDetailMult = float(var_value1)
                                if vv1_prev == "useDetail":
                                    if float(var_value1) > 0:
                                        _useDetail = True
                                if vv1_prev == "detailNormalBlend":
                                    _currentDetailNormalBlend = float(var_value1)
                                
                                # Print the ambient value from the previous iteration
                                print(f"----{vv1_prev}: {var_value1}")
                                vv1_prev = None  # Reset ambient_value
                            #print(f"----Vars {var_key1}: {var_value1}")
            textures = value.get('textures')
            if textures:
                slot = 0
                for tex_key, tex_value in textures.items():
                    if slot > 0:
                        print(f"----Texture Image.00{slot}: {tex_value}")
                    else:
                        print(f"----Texture Image: {tex_value}")
                    tex_names.append(tex_value)
                    print(f"Tex name = {tex_names[slot]}")
                    slot += 1
                    
            print(f"")
            
            nodes = _currentMat.node_tree.nodes
            links = _currentMat.node_tree.links
            
            print(f"Use Detail: {_useDetail}")
            print(f"Detail Multiplier: {_currentDetailMult}")
            print(f"Normal Multiplier: {_currentDetailNMMult}")
            print(f"Normal Blend: {_currentDetailNormalBlend}")
            
            normal_map_node = None
            separate_color_node = None
            math1_node = None
            math2_node = None
            mapping_node = None
            tc_node = None
            detail_mult_node = None
            detail_mix_node = None
            alpha_mix_node = None
            pbr_mapping_node = None
            pbr_tc_node = None
            pbr_mult_node = None
            ksmaterial_node = None
            detail_normal_mix_node = None
            
            img_tex_1_node = None
            img_tex_2_node = None
            img_tex_3_node = None
            img_tex_4_node = None
            img_tex_5_node = None
            img_tex_6_node = None
            img_tex_7_node = None
            img_tex_8_node = None
            
            principled_bsdf_node = None
            
            # If nodes exist set them appropriately
            for node in nodes:
                if node.name == "Normal Map 1":
                    normal_map_node = node  
                    print(f"Normal: {node}")
                if node.name == "TxtMap Separate Color":
                    separate_color_node = node
                    print(f"Sep Color: {node}")
                if node.name == "TxtMap Math 1":
                    math1_node = node
                    print(f"math1: {node}")
                if node.name == "TxtMap Math 2":
                    math2_node = node
                    print(f"Math2: {node}")
                if node.name == "Detail Mapping":
                    mapping_node = node
                    print(f"Detail Mapping: {node}")
                if node.name == "Detail Texture Coordinate":
                    tc_node = node
                    print(f"TC: {node}")
                if node.name == "Detail Multiplier":
                    detail_mult_node = node
                    print(f"Detail Mult: {node}")
                if node.name == "Detail Mix":
                    detail_mix_node = node
                    print(f"Detail Mix: {node}")
                if node.name == "Blend Alpha Mix":
                    alpha_mix_node = node
                    print(f"Alpha Mix: {node}")
                if node.name == "PBRMapping":
                    pbr_mapping_node = node
                    print(f"PBR Map: {node}")
                if node.name == "PBRTexture Coordinate":
                    pbr_tc_node = node
                    print(f"PBR TC: {node}")
                if node.name == "PBRMultiplier":
                    pbr_mult_node = node
                    print(f"PBR Mult: {node}")
                if node.name == "ksMaterial Details":
                    ksmaterial_node = node
                    print(f"ksMat: {node}")
                if node.name == "Detail Normal Mix":
                    detail_normal_mix_node = node
                    print(f"Detail Normal Mix: {node}")
                if node.name == "Principled BSDF":
                    principled_bsdf_node = node
                    print(f"PBSDF: {node}")
                if node.name == "Image Texture":
                    img_tex_1_node = node
                    print(f"Image Texture: {node}")
                if node.name == "Image Texture.001":
                    img_tex_2_node = node
                    print(f"Image Texture.001: {node}")
                if node.name == "Image Texture.002":
                    img_tex_3_node = node
                    print(f"Image Texture.002: {node}")
                if node.name == "Image Texture.003":
                    img_tex_4_node = node
                    print(f"Image Texture.003: {node}")
                if node.name == "Image Texture.004":
                    img_tex_5_node = node
                    print(f"Image Texture.004: {node}")
                if node.name == "Image Texture.005":
                    img_tex_6_node = node
                    print(f"Image Texture.005: {node}")
                if node.name == "Image Texture.006":
                    img_tex_7_node = node
                    print(f"Image Texture.006: {node}")
                if node.name == "Image Texture.007":
                    img_tex_8_node = node
                    print(f"Image Texture.007: {node}")
                #if node.name == "Image Texture.008":
                #    img_tex_9_node = node
                #    print(f"Image Texture.008: {node}")
                #if node.name == "Image Texture.009":
                #    img_tex_10_node = node
                
            #apply the shader socket connections
            if _currentAlphaBlend == True:
                _currentMat.blend_method = "BLEND"
                _currentMat.show_transparent_back = 0
                if _useDetail == True:
                    links.new(alpha_mix_node.outputs[0], principled_bsdf_node.inputs['Alpha'])
                else:
                    links.new(img_tex_1_node.outputs['Alpha'], principled_bsdf_node.inputs['Alpha'])
            if _currentAlphaTest == True:
                _currentMat.blend_method = "HASHED"
                _currentMat.show_transparent_back = 0
                if _useDetail == True:
                    links.new(alpha_mix_node.outputs[0], principled_bsdf_node.inputs['Alpha'])
                else:
                    links.new(img_tex_1_node.outputs['Alpha'], principled_bsdf_node.inputs['Alpha'])
            
            if int(_currentTextureCount) == 1:
                links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                    
                
            if int(_currentTextureCount) == 2:
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                
                if img_tex_2_node:
                    # Check if the image datablock exists
                    if img_tex_2_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[1], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image = img
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_2_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_2_node.image.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image.name = tex_names[1]
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_2_node.name} with path of: {os.path.join(texture_directory, tex_names[1])} \n')
                
                if _currentShader not in ("ksGrass", "ksPostFOG_MS"):
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                
                if _currentShader != "ksPerPixelNM_UVMult":
                    print(f"WARN: Shader type: {_currentShader} utilizes multipliers which are not configured for the base color or normal texture.")
                
                
            if int(_currentTextureCount) == 3:
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                
                if img_tex_2_node:
                    # Check if the image datablock exists
                    if img_tex_2_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[1], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image = img
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_2_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_2_node.image.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image.name = tex_names[1]
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_2_node.name} with path of: {os.path.join(texture_directory, tex_names[1])} \n')
                
                if img_tex_3_node:
                    # Check if the image datablock exists
                    if img_tex_3_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[2], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image = img
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_3_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_3_node.image.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image.name = tex_names[2]
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_3_node.name} with path of: {os.path.join(texture_directory, tex_names[2])} \n')
                
            
                if _currentShader == "ksPerPixelAT_NM_emissive":
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(img_tex_2_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                    
                    links.new(img_tex_3_node.outputs['Color'], principled_bsdf_node.inputs['Emission'])
                
                if _currentShader == "ksPerPixel_dual_layer":
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                
                    print(f"WARN: Shader type: {_currentShader} utilizes layers and mask which are not configured for the shader. Mapping original color only.")
                if _currentShader == "ksPerPixelAT_NM_emissive":
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                
                    print(f"WARN: Shader type: {_currentShader} utilizes multipliers which are not configured for the base color or normal texture.")
                
                
            if int(_currentTextureCount) == 4:
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                
                if img_tex_2_node:
                    # Check if the image datablock exists
                    if img_tex_2_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[1], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image = img
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_2_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_2_node.image.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image.name = tex_names[1]
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_2_node.name} with path of: {os.path.join(texture_directory, tex_names[1])} \n')
                
                if img_tex_3_node:
                    # Check if the image datablock exists
                    if img_tex_3_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[2], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image = img
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_3_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_3_node.image.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image.name = tex_names[2]
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_3_node.name} with path of: {os.path.join(texture_directory, tex_names[2])} \n')
                
                if img_tex_4_node:
                    # Check if the image datablock exists
                    if img_tex_4_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[3], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image = img
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_4_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_4_node.image.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image.name = tex_names[3]
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_4_node.name} with path of: {os.path.join(texture_directory, tex_names[3])} \n')
                
                # IsDetail true map the base colors to the mix nodes
                if _useDetail == True:
                    # Base Color
                    links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                    links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                    
                    links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                    links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                    
                    alpha_mix_node.inputs[0].default_value = 0.95
                    
                    links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                    links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                    
                    # Normal
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                    
                    # Texture Map
                    links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                    
                    links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                    links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                    links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                    
                    links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                    links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                    
                    img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                    
                    # Detail 
                    links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                    links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                    links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                    
                    if _currentDetailMult is None:
                        detail_mult_node.outputs[0].default_value = 1.0
                    else:
                        detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                else:
                    # Base Color
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    # Normal
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                    
                    # Texture Map
                    links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                    
                    links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                    links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                    links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                    
                    links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                    links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                    
                    img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                    
                    # Detail 
                    links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                    links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                    links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                    
                    if _currentDetailMult is None:
                        detail_mult_node.outputs[0].default_value = 1.0
                    else:
                        detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                
            if int(_currentTextureCount) == 5:
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                
                if img_tex_2_node:
                    # Check if the image datablock exists
                    if img_tex_2_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[1], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image = img
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_2_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_2_node.image.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image.name = tex_names[1]
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_2_node.name} with path of: {os.path.join(texture_directory, tex_names[1])} \n')
                
                if img_tex_3_node:
                    # Check if the image datablock exists
                    if img_tex_3_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[2], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image = img
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_3_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_3_node.image.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image.name = tex_names[2]
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_3_node.name} with path of: {os.path.join(texture_directory, tex_names[2])} \n')
                
                if img_tex_4_node:
                    # Check if the image datablock exists
                    if img_tex_4_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[3], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image = img
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_4_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_4_node.image.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image.name = tex_names[3]
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_4_node.name} with path of: {os.path.join(texture_directory, tex_names[3])} \n')
                
                if img_tex_5_node:
                    # Check if the image datablock exists
                    if img_tex_5_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[4], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[4])
                        img_tex_5_node.image = img
                        img_tex_5_node.image.reload()
                        img_tex_5_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_5_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_5_node.image.filepath = os.path.join(texture_directory, tex_names[4])
                        img_tex_5_node.image.name = tex_names[4]
                        img_tex_5_node.image.reload()
                        img_tex_5_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_5_node.name} with path of: {os.path.join(texture_directory, tex_names[4])} \n')
            
                # IsDetail true map the base colors to the mix nodes
                if _useDetail == True:
                    if _currentShader in ("ksDiscBrake", "ksTyres"):
                        links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                        links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                        links.new(img_tex_2_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                    elif _currentShader == "ksPerPixelMultiMap_emissive":
                        # Base Color
                        links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                        links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                        
                        links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                        links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                        
                        alpha_mix_node.inputs[0].default_value = 0.95
                        
                        links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                        
                        # Normal
                        links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                        
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Texture Map
                        links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                        
                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                        
                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                        
                        img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Detail 
                        links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                        
                        detail_mult_node.outputs[0].default_value = float(_currentDetailMult)   
                        
                        # Emission
                        links.new(img_tex_5_node.outputs['Color'], principled_bsdf_node.inputs['Emission'])
                        
                    elif _currentShader == "ksPerPixelMultiMap_AT_emissive":
                        # Base Color
                        links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                        links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                        
                        links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                        links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                        
                        alpha_mix_node.inputs[0].default_value = 0.95
                        
                        links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                        
                        # Normal
                        links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                        
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Texture Map
                        links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                        
                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                        
                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                        
                        img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Detail 
                        links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                        
                        # Emission
                        links.new(img_tex_5_node.outputs['Color'], principled_bsdf_node.inputs['Emission'])
                        
                        detail_mult_node.outputs[0].default_value = float(_currentDetailMult)    
                        
                    elif _currentShader in ("ksPerPixelMultiMap_NMDetail", "ksSkinnedMesh_NMDetaill"):
                        # Base Color
                        links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                        links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                        
                        links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                        links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                        
                        alpha_mix_node.inputs[0].default_value = 0.95
                        
                        links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                        
                        # Normal
                        links.new(img_tex_2_node.outputs['Color'], detail_normal_mix_node.inputs[6])
                        links.new(img_tex_5_node.outputs['Color'], detail_normal_mix_node.inputs[7])
                        
                        links.new(detail_normal_mix_node.outputs[2], normal_map_node.inputs['Color'])
                        
                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                        
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                        img_tex_5_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Texture Map
                        links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                        
                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                        
                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                        
                        img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Detail 
                        links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                        
                        if _currentDetailMult is None:
                            detail_mult_node.outputs[0].default_value = 1.0
                        else:
                            detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                        
                        links.new(pbr_mapping_node.outputs['Vector'], img_tex_5_node.inputs['Vector'])
                        links.new(pbr_tc_node.outputs['UV'], pbr_mapping_node.inputs['Vector'])
                        links.new(pbr_mult_node.outputs['Value'], pbr_mapping_node.inputs['Scale'])
                        
                        detail_normal_mix_node.inputs[0].default_value = float(_currentDetailNormalBlend)
                        
                        pbr_mult_node.outputs[0].default_value = float(_currentDetailMult)
                        
                        
                    elif _currentShader == "smSticker":
                        # Base Color
                        links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                        links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                        
                        links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                        links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                        
                        alpha_mix_node.inputs[0].default_value = 0.95
                        
                        links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                        
                        # Normal
                        links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                        
                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                        
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Texture Map
                        links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                        
                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                        
                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                        
                        img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Detail 
                        links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                        
                        if _currentDetailMult is None:
                            detail_mult_node.outputs[0].default_value = 1.0
                        else:
                            detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                        
                        links.new(pbr_mapping_node.outputs['Vector'], img_tex_2_node.inputs['Vector'])
                        links.new(pbr_tc_node.outputs['UV'], pbr_mapping_node.inputs['Vector'])
                        links.new(pbr_mult_node.outputs['Value'], pbr_mapping_node.inputs['Scale'])
                        
                        pbr_mult_node.outputs[0].default_value = float(_currentDetailNMMult)
                        
                        
                    elif _currentShader == "ksPerPixelMultiMap_AT_NMDetail":
                        # Base Color
                        links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                        links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                        
                        links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                        links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                        
                        alpha_mix_node.inputs[0].default_value = 0.95
                        
                        links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                        
                        # Normal
                        links.new(img_tex_2_node.outputs['Color'], detail_normal_mix_node.inputs[6])
                        links.new(img_tex_5_node.outputs['Color'], detail_normal_mix_node.inputs[7])
                        
                        links.new(detail_normal_mix_node.outputs[2], normal_map_node.inputs['Color'])
                        
                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                        
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                        img_tex_5_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Texture Map
                        links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                        
                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                        
                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                        
                        img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Detail 
                        links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                        
                        if _currentDetailMult is None:
                            detail_mult_node.outputs[0].default_value = 1.0
                        else:
                            detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                        
                        links.new(pbr_mapping_node.outputs['Vector'], img_tex_5_node.inputs['Vector'])
                        links.new(pbr_tc_node.outputs['UV'], pbr_mapping_node.inputs['Vector'])
                        links.new(pbr_mult_node.outputs['Value'], pbr_mapping_node.inputs['Scale'])
                        
                        detail_normal_mix_node.inputs[0].default_value = float(_currentDetailNormalBlend)
                        
                        pbr_mult_node.outputs[0].default_value = float(_currentDetailNMMult)
                        
                        
                    elif _currentShader == "ksPerPixelMultiMap_damage":
                        # Base Color
                        links.new(img_tex_1_node.outputs['Color'], detail_mix_node.inputs[6])
                        links.new(img_tex_1_node.outputs['Alpha'], alpha_mix_node.inputs[2])
                        
                        links.new(img_tex_4_node.outputs['Color'], detail_mix_node.inputs[7])
                        links.new(img_tex_4_node.outputs['Alpha'], alpha_mix_node.inputs[3])
                        
                        alpha_mix_node.inputs[0].default_value = 0.95
                        
                        links.new(alpha_mix_node.outputs[0], detail_mix_node.inputs[0])
                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                        
                        # Normal
                        links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                        
                        img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Texture Map
                        links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                        
                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                        
                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                        
                        img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                        
                        # Detail 
                        links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                        
                        if _currentDetailMult is None:
                            detail_mult_node.outputs[0].default_value = 1.0
                        else:
                            detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                else:
                    # Base Color
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    # Normal
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                    
                    # Texture Map
                    links.new(img_tex_3_node.outputs['Color'], separate_color_node.inputs['Color'])
                    
                    links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                    links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                    links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                    
                    links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                    links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                    
                    img_tex_3_node.image.colorspace_settings.name = 'Non-Color'
                    
                    # Detail 
                    links.new(mapping_node.outputs['Vector'], img_tex_4_node.inputs['Vector'])
                    links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                    links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                    
                    if _currentDetailMult is None:
                        detail_mult_node.outputs[0].default_value = 1.0
                    else:
                        detail_mult_node.outputs[0].default_value = float(_currentDetailMult)
                
                
            #if int(_currentTextureCount) > 5:
            if int(_currentTextureCount) == 6:
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                
                if img_tex_2_node:
                    # Check if the image datablock exists
                    if img_tex_2_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[1], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image = img
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_2_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_2_node.image.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image.name = tex_names[1]
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_2_node.name} with path of: {os.path.join(texture_directory, tex_names[1])} \n')
                
                if img_tex_3_node:
                    # Check if the image datablock exists
                    if img_tex_3_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[2], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image = img
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_3_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_3_node.image.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image.name = tex_names[2]
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_3_node.name} with path of: {os.path.join(texture_directory, tex_names[2])} \n')
                
                if img_tex_4_node:
                    # Check if the image datablock exists
                    if img_tex_4_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[3], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image = img
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_4_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_4_node.image.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image.name = tex_names[3]
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_4_node.name} with path of: {os.path.join(texture_directory, tex_names[3])} \n')
                
                if img_tex_5_node:
                    # Check if the image datablock exists
                    if img_tex_5_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[4], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[4])
                        img_tex_5_node.image = img
                        img_tex_5_node.image.reload()
                        img_tex_5_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_5_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_5_node.image.filepath = os.path.join(texture_directory, tex_names[4])
                        img_tex_5_node.image.name = tex_names[4]
                        img_tex_5_node.image.reload()
                        img_tex_5_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_5_node.name} with path of: {os.path.join(texture_directory, tex_names[4])} \n')
                
                if img_tex_6_node:
                    # Check if the image datablock exists
                    if img_tex_6_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[5], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[5])
                        img_tex_6_node.image = img
                        img_tex_6_node.image.reload()
                        img_tex_6_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_6_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_6_node.image.filepath = os.path.join(texture_directory, tex_names[5])
                        img_tex_6_node.image.name = tex_names[5]
                        img_tex_6_node.image.reload()
                        img_tex_6_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_6_node.name} with path of: {os.path.join(texture_directory, tex_names[5])} \n')
                
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")

            if int(_currentTextureCount) == 7:
                if img_tex_1_node:
                    # Check if the image datablock exists
                    if img_tex_1_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[0], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image = img
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_1_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_1_node.image.filepath = os.path.join(texture_directory, tex_names[0])
                        img_tex_1_node.image.name = tex_names[0]
                        img_tex_1_node.image.reload()
                        img_tex_1_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_1_node.name} with path of: {os.path.join(texture_directory, tex_names[0])} \n')
                
                if img_tex_2_node:
                    # Check if the image datablock exists
                    if img_tex_2_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[1], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image = img
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_2_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_2_node.image.filepath = os.path.join(texture_directory, tex_names[1])
                        img_tex_2_node.image.name = tex_names[1]
                        img_tex_2_node.image.reload()
                        img_tex_2_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_2_node.name} with path of: {os.path.join(texture_directory, tex_names[1])} \n')
                
                if img_tex_3_node:
                    # Check if the image datablock exists
                    if img_tex_3_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[2], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image = img
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_3_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_3_node.image.filepath = os.path.join(texture_directory, tex_names[2])
                        img_tex_3_node.image.name = tex_names[2]
                        img_tex_3_node.image.reload()
                        img_tex_3_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_3_node.name} with path of: {os.path.join(texture_directory, tex_names[2])} \n')
                
                if img_tex_4_node:
                    # Check if the image datablock exists
                    if img_tex_4_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[3], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image = img
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_4_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_4_node.image.filepath = os.path.join(texture_directory, tex_names[3])
                        img_tex_4_node.image.name = tex_names[3]
                        img_tex_4_node.image.reload()
                        img_tex_4_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_4_node.name} with path of: {os.path.join(texture_directory, tex_names[3])} \n')
                
                if img_tex_5_node:
                    # Check if the image datablock exists
                    if img_tex_5_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[4], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[4])
                        img_tex_5_node.image = img
                        img_tex_5_node.image.reload()
                        img_tex_5_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_5_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_5_node.image.filepath = os.path.join(texture_directory, tex_names[4])
                        img_tex_5_node.image.name = tex_names[4]
                        img_tex_5_node.image.reload()
                        img_tex_5_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_5_node.name} with path of: {os.path.join(texture_directory, tex_names[4])} \n')
                
                if img_tex_6_node:
                    # Check if the image datablock exists
                    if img_tex_6_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[5], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[5])
                        img_tex_6_node.image = img
                        img_tex_6_node.image.reload()
                        img_tex_6_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_6_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_6_node.image.filepath = os.path.join(texture_directory, tex_names[5])
                        img_tex_6_node.image.name = tex_names[5]
                        img_tex_6_node.image.reload()
                        img_tex_6_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_6_node.name} with path of: {os.path.join(texture_directory, tex_names[5])} \n')
                
                if img_tex_7_node:
                    # Check if the image datablock exists
                    if img_tex_7_node.image is None:
                        # Create a new image datablock and set it to the node
                        img = bpy.data.images.new(name=tex_names[6], width=1, height=1)
                        img.filepath = os.path.join(texture_directory, tex_names[6])
                        img_tex_7_node.image = img
                        img_tex_7_node.image.reload()
                        img_tex_7_node.image.alpha_mode = 'CHANNEL_PACKED'
                        img_tex_7_node.image.source = 'FILE'
                    else:
                        # Set the image filepath and name
                        img_tex_7_node.image.filepath = os.path.join(texture_directory, tex_names[6])
                        img_tex_7_node.image.name = tex_names[6]
                        img_tex_7_node.image.reload()
                        img_tex_7_node.image.alpha_mode = 'CHANNEL_PACKED'
                else:
                    Error_result += (f'Material: {_currentMatName} missing image on {img_tex_7_node.name} with path of: {os.path.join(texture_directory, tex_names[6])} \n')
                
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
            if int(_currentTextureCount) == 8:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
            if int(_currentTextureCount) == 9:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
            if int(_currentTextureCount) == 10:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
    
    print(f'Missing texture report: \n {Error_result} \n')

def toggle_show_backface(selected_objects):
    for obj in selected_objects:
        if obj.type != 'MESH':
            continue
        
        # Iterate through all material slots of the object
        for slot in obj.material_slots:
            if slot.material:
                material = slot.material
                
                # Toggle the show_backface property
                if material.show_transparent_back == 1:
                    material.show_transparent_back = 0
                    print(f"Turned off 'Show Backface' for material '{material.name}'")
                else:
                    material.show_transparent_back = 1
                    print(f"Turned on 'Show Backface' for material '{material.name}'")

class OBJECT_OT_acutil_read_ini(Operator, ImportHelper):
    bl_idname = "acutil.read_ini"
    bl_label = "Read INI"
    bl_description = "This will open a dialog to select an ini file from a converted kn5. It wil then apply the correct shader values based off the material details in the ini"
    
    filename_ext = ".ini"

    def execute(self, context):
        # Get the filepath from the operator
        ini_filepath = self.filepath
        # Process the selected INI file
        main_ini_processer(ini_filepath)
        self.report({'INFO'}, 'ACET: INI file processed and persistence applied')
        
        return {'FINISHED'}

class OBJECT_OT_acutil_backface(bpy.types.Operator):
    bl_idname = "acutil.backface"
    bl_label = "Set Backface"
    bl_description = "This will flip the backface of the selected materials."

    def execute(self, context):
        # Get selected objects
        selected_objects = bpy.context.selected_objects
        
        # Call the function
        toggle_show_backface(selected_objects)
        return {'FINISHED'}
        
# Functionality for physical file operations such as KN5 conversion and FBX conversion

class OBJECT_OT_RunFbxConverter(bpy.types.Operator):
    """Run FbxConverter"""
    bl_idname = "object.run_fbx_converter"
    bl_label = "Run Fbx Converter"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        result = run_fbx_converter(self.filepath)
        if 'INFO' in result:
            self.report({'INFO'}, result['INFO'])
        else:
            self.report({'ERROR'}, result['ERROR'])
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OBJECT_OT_RunKn5Converter(bpy.types.Operator):
    """Run KN5 Converter"""
    bl_idname = "object.run_kn5_converter"
    bl_label = "Run KN5 Converter"

    output_type: bpy.props.StringProperty(name="Output Type", description="Output type for KN5 Converter", default="fbx")
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        result = run_kn5_converter(self.filepath, self.output_type)
        if 'INFO' in result:
            self.report({'INFO'}, result['INFO'])
        else:
            self.report({'ERROR'}, result['ERROR'])
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Define the panel for the custom tab
class OBJECT_PT_ac_shader(bpy.types.Panel):
    bl_label = "AC Utilities"
    bl_idname = "OBJECT_PT_ac_shader"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'  # Specify the tab's name here
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Text block that says "Standard Conversion"
        row = layout.row()
        row.label(text="KN5 Conversion", icon='NONE')
        
        # KN5 Converter buttons
        layout.operator("object.run_kn5_converter", text="Convert to FBX").output_type = "fbx"
        layout.operator("object.run_kn5_converter", text="Convert to OBJ").output_type = "obj"
        
        # Text block that says "Standard Conversion"
        row = layout.row()
        row.label(text="FBX Conversion", icon='NONE')
        
        layout.operator("object.run_fbx_converter", text="Convert to FBX to Binary")
        
        
        layout.operator("acutil.read_ini", text="Load Persistence")
        layout.operator("acutil.backface", text="Set Transparency")
        
        
# Register the operators and panel
def register():
    bpy.utils.register_class(OBJECT_OT_acutil_read_ini)
    bpy.utils.register_class(OBJECT_OT_acutil_backface)
    bpy.utils.register_class(OBJECT_PT_ac_shader)
    bpy.utils.register_class(OBJECT_OT_RunKn5Converter)
    bpy.utils.register_class(OBJECT_OT_RunFbxConverter)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_acutil_read_ini)
    bpy.utils.unregister_class(OBJECT_OT_acutil_backface)
    bpy.utils.unregister_class(OBJECT_PT_ac_shader)
    bpy.utils.unregister_class(OBJECT_OT_RunKn5Converter)
    bpy.utils.unregister_class(OBJECT_OT_RunFbxConverter)
    
if __name__ == "__main__":
    register()