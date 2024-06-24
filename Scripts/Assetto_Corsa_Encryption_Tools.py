bl_info = {
    "name": "Assetto Corsa Encryption Tools",
    "author": "Dad",
    "version": (2, 2, 1),
    "blender": (3, 4, 0),
    "location": "View3D > Sidebar > ACET",
    "description": "Toolset for use with NR imports for Encrypted files from AC. End to end tool for unencrypting cars.",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
import os
import re
import math
import mathutils
import shutil
from collections import Counter, defaultdict
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, FileSelectParams
from bpy.props import StringProperty

# TODO / CHANGE LOG
"""
2.2.1
• A few bug fixes
• Added a few functions to correct dummy parenting issues and a function to drop the numbering suffix due to how KN5 have a dummy for each mesh.
2.2.0
• Added functionality for updating origins for objects and their parents. Two features were added to handle this. 
• Updated the aligning logic for aligning the NR model and KN5. This should hopefully be more consistent with the alignment functionality. 
• Fixed a bug with the FBX importer, if an object is no longer in the Scene Collection, it will ignore the removal function and continue as expected.
2.1.1
• Added in Wheel Straightening. This uses similar functionality to the model alignment but uses some other math. This will realign wheels on their parent. 
+
2.1.0
• Adding in extra functionality for start to finish. Can now Read INI file and apply blender shader details to the model. This will also rename the original textures from the rip to the original kn5 texture names and place them in a folder called textures. 
• Additional shader buttons were added to adjust visual representation in blender.
2.0.0
• Complete reweite of the code base. Changed direction from a helper tool to an end to end tool. This can handle the importation of the NR files to the end of exporting out a ready made fbx for kseditor.

1.03
• [FIXED] - Add in detail node to export out what textures belong to what material/object - Currently the framework for the node is present. Need to impliment the export functionality
• [Added later] - Setup dummy based off object location, need to look at ACT for this
• [FIXED] - Fix normal map node creation between PBR and standard normal mapping. (Currently creating new nodes breaking remapping PBR)

1.0.2
•[FIXED] - Need to fix the detail mapping, flip a and b nodes, and set the detail image alpha instead of the diffuse alpha for factor_mode
•[FIXED] - Need to redo the conversion, with switching the alpha stuff, the image is missing when converting to png. If converted to dds it still does not show correctly. Other option would be to set alpha type to channel packed, but unsure if this works with transparency. Works with solid images.
- Setting images to Channel Packed testing
•[No Fix] - refer to above, this handles the transparency - Change transparency to now reflect the transparent image, this should be done with the _alpha image. Need to figure out how to add a new image texture with a basic image then set the image to the transparent timage.

1.0.0 - 1.0.1
• Initial release and bug fixes
"""
nr_imported = False
nr_converted = False

# Function to create an empty
def create_empty(name, location=(0, 0, 0), empty_display_size=0.5):
    bpy.ops.object.empty_add(location=location)
    empty = bpy.context.object
    empty.name = name
    empty.empty_display_size = empty_display_size
    return empty

# Function to delete the NR/KN5 alignment empties.
def delete_alignment_empties():
    empty_names = ['NR_Alignment_F', 'NR_Alignment_R', 'KN5_Alignment_F', 'KN5_Alignment_R']
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    for empty_name in empty_names:
        if empty_name in bpy.data.objects:
            empty = bpy.data.objects[empty_name]
            empty.select_set(True)  # Select the empty
    bpy.ops.object.delete()  # Delete selected objects

# Function to add a damped track constraint
def add_damped_track_constraint(source, target, track_axis='TRACK_Y', influence=1.0):
    constraint = source.constraints.new(type='DAMPED_TRACK')
    constraint.target = target
    constraint.track_axis = track_axis
    constraint.influence = influence

# Function to add a locked track constraint
def add_locked_track_constraint(source, target, track_axis, lock_axis, influence=1.0):
    constraint = source.constraints.new(type='LOCKED_TRACK')
    constraint.target = target
    constraint.track_axis = track_axis
    constraint.lock_axis = lock_axis
    constraint.influence = influence

# Function to setup and configure the alignment empties for rotating the NR imported model.
def setup_alignment_empties_and_constraints():
    # Create empties
    nr_alignment_f = create_empty('NR_Alignment_F')
    nr_alignment_r = create_empty('NR_Alignment_R')
    kn5_alignment_f = create_empty('KN5_Alignment_F')
    kn5_alignment_r = create_empty('KN5_Alignment_R')

    # Add Damped Track constraints
    add_locked_track_constraint(nr_alignment_r, nr_alignment_f, 'TRACK_Y', 'LOCK_X')
    add_locked_track_constraint(kn5_alignment_r, kn5_alignment_f, 'TRACK_Y', 'LOCK_Z')

# Function to actually align the NR model to the imported KN5 model
def nr_align_and_parent():
    nr_alignment_r = bpy.data.objects['NR_Alignment_R']
    
    apply_constraint_to_object("NR_Alignment_R", "Locked Track")
    #apply_constraint_to_object("NR_Alignment_R", "Damped Track")
    apply_constraint_to_object("KN5_Alignment_R", "Locked Track")
    #apply_constraint_to_object("KN5_Alignment_R", "Damped Track")
    
    
    # Parent objects not in 'KN5' collection to 'NR_Alignment_R'
    bpy.ops.object.select_all(action='DESELECT')
    kn5_collection = bpy.data.collections.get("KN5")
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and (not kn5_collection or obj.name not in kn5_collection.objects):
            #obj.select_set(True)
            obj.parent = nr_alignment_r
            obj.matrix_parent_inverse = nr_alignment_r.matrix_world.inverted()
    nr_alignment_r.select_set(True)
    bpy.context.view_layer.objects.active = nr_alignment_r
    #bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    # Align NR alignment empties to match KN5 alignment empties in location and rotation
    bpy.data.objects['NR_Alignment_F'].location = bpy.data.objects['KN5_Alignment_F'].location
    bpy.data.objects['NR_Alignment_F'].rotation_euler = bpy.data.objects['KN5_Alignment_F'].rotation_euler
    bpy.data.objects['NR_Alignment_R'].location = bpy.data.objects['KN5_Alignment_R'].location
    bpy.data.objects['NR_Alignment_R'].rotation_euler = bpy.data.objects['KN5_Alignment_R'].rotation_euler
    
    # Before aligning, rotate NR_Alignment_R around the Y axis by 180 degrees
    #nr_alignment_r.rotation_euler[1] += math.radians(180)

    # Apply visual transform and clear parent
    bpy.ops.object.select_all(action='DESELECT')
    nr_alignment_r.select_set(True)
    bpy.context.view_layer.objects.active = nr_alignment_r
    
    for child in nr_alignment_r.children:
        child.select_set(True)
        bpy.context.view_layer.objects.active = child
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
    delete_alignment_empties()

# ---------------------------------------------------------

# FBX importer class to bring in the KN5 encrypted original model
class OpenFBXFilebrowser(Operator, ImportHelper):
    bl_idname = "import_scene.fbx_to_kn5"
    bl_label = "Import FBX Data"
    filename_ext = ".fbx"
    filter_glob: StringProperty(
        default='*.fbx',
        options={'HIDDEN'}
    )

    def execute(self, context):
        # Import the FBX file
        bpy.ops.import_scene.fbx(filepath=self.filepath)
        
        # Ensure the root object's scale is set to 1,1,1
        self.adjust_root_scale()

        # Handle the collection
        collection_name = "KN5"
        target_collection = self.get_or_create_collection(collection_name)

        # Move imported objects to the target collection
        self.move_objects_to_collection(target_collection)

        return {'FINISHED'}

    def adjust_root_scale(self):
        for obj in bpy.context.selected_objects:
            if obj.parent is None:  # Assuming the root object has no parent
                if obj.scale != (1.0, 1.0, 1.0):
                    obj.scale = (1.0, 1.0, 1.0)
                    bpy.context.view_layer.update()

    def get_or_create_collection(self, collection_name):
        if collection_name in bpy.data.collections:
            return bpy.data.collections[collection_name]
        elif "Collection" in bpy.data.collections:
            bpy.data.collections["Collection"].name = collection_name
            return bpy.data.collections[collection_name]
        else:
            new_collection = bpy.data.collections.new(name=collection_name)
            bpy.context.scene.collection.children.link(new_collection)
            return new_collection

    #def move_objects_to_collection(self, target_collection):
    #    for obj in bpy.context.selected_objects:
    #        # Ensure we are only moving the newly imported objects
    #
    #        bpy.context.scene.collection.objects.unlink(obj)
    #        target_collection.objects.link(obj)
    def move_objects_to_collection(self, target_collection):
        for obj in bpy.context.selected_objects:
            if obj.name in bpy.context.scene.collection.objects.keys():
                # Ensure we are only moving the newly imported objects
                bpy.context.scene.collection.objects.unlink(obj)
            target_collection.objects.link(obj)

# NR file operators and handlers
# To open the file browser, run: bpy.ops.import_nr_mesh.nr_log('INVOKE_DEFAULT')

class OpenNRFilebrowser(Operator, ImportHelper):
    bl_idname = "import_nr_mesh.nr_log"
    bl_label = "Import NR Log File"
    filename_ext = ".txt"
    filter_glob: StringProperty(
        default='*.txt',
        options={'HIDDEN'}
    )

    def execute(self, context):
        process_file(self.filepath)
        return {'FINISHED'}

# INI file browser functionality

class OpenINIFilebrowser(Operator, ImportHelper):
    bl_idname = "import_ini_file.shader_reader"
    bl_label = "Import KN5 INI file"
    filename_ext = ".ini"
    filter_glob: StringProperty(
        default='*.ini',
        options={'HIDDEN'}
    )

    def execute(self, context):
        context.window_manager.fileselect_add(self)  # Open file browser
        return {'RUNNING_MODAL'}
        
# references find_associated_files and _import_nr_mesh
# Used to process the log file and get the matrixes and options for importing the mesh
def process_file(filepath):
    matrix_pattern = r"float4x4 ksProjection_base = (\[\[.+?\]\])"
    mesh_info_pattern = r"Mesh\(s\) saved\. File: (.+?\\mesh_(\d+)\.nr)"
    line_to_matrix = {}
    line_to_file = {}
    matrix_counts = Counter()

    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            matrix_match = re.search(matrix_pattern, line)
            if matrix_match:
                matrix = matrix_match.group(1)
                line_to_matrix[i] = matrix
                matrix_counts[matrix] += 1

            file_match = re.search(mesh_info_pattern, line)
            if file_match:
                file_path = file_match.group(1)
                line_to_file[i] = file_path

    if not matrix_counts:
        print("No matrices found.")
        return

    most_common_matrix, _ = matrix_counts.most_common(1)[0]
    file_lines_for_matrix = find_associated_files(line_to_matrix, line_to_file, most_common_matrix)
    if file_lines_for_matrix:
        file_directory = file_lines_for_matrix[0].rsplit('\\', 1)[0]  # Assuming all files are in the same directory
        import_nr_mesh(file_directory, file_lines_for_matrix, most_common_matrix)
    else:
        print("No associated file lines found.")

def find_associated_files(line_to_matrix, line_to_file, matrix):
    associated_files = []
    for matrix_line, matrix_val in line_to_matrix.items():
        if matrix_val == matrix:
            for file_line in line_to_file.keys():
                if abs(file_line - matrix_line) <= 200:
                    associated_files.append(line_to_file[file_line])
    return list(set(associated_files))  # Remove duplicates

def import_nr_mesh(directory, files, matrix):
    file_list = [{"name": file_name.rsplit('\\', 1)[-1]} for file_name in files]  # Extract file names from paths
    bpy.ops.import_mesh.nr(
        filepath="", 
        filter_glob="*.nr", 
        files=file_list, 
        directory=directory, 
        positionLoadTab='MATRIX', 
        exactProjMat=matrix,
        # Add or adjust additional parameters as needed
    )

# -----------------------------------------------------

# Function to create or update an image with new pixel data
def create_or_update_image(name, width, height, pixel_data):
    temp_name = name + "_temp"
    if temp_name not in bpy.data.images:
        new_img = bpy.data.images.new(temp_name, width=width, height=height, alpha=True)
    else:
        new_img = bpy.data.images[temp_name]
        new_img.scale(width, height)  # Ensure the image is the correct size

    new_img.pixels = pixel_data
    return new_img
    
# Create a function to get image details from an Image Texture node
def get_image_details(image_texture_node):
    if image_texture_node and image_texture_node.image:
        image = image_texture_node.image
        image_name = image.name
        image_path = bpy.path.abspath(image.filepath)
        return image_name, image_path
    return None, None
    

def active_object_change_handler(scene):
    if hasattr(bpy.context, "window_manager"):
        # This global variable is used to store the name of the last active object
        global last_active_object_name
        current_active_object = bpy.context.active_object
        current_active_object_name = current_active_object.name if current_active_object else None

        if current_active_object_name != last_active_object_name:
            last_active_object_name = current_active_object_name
            update_detail_multiplier_from_active_object(bpy.context)
            update_pbr_multiplier_from_active_object(bpy.context)

# Initialize the global variable outside of the handler function
last_active_object_name = None

# ------------------------------------------------------------

# Define the operator for the Align parents button
class OBJECT_OT_acet_alignparent(bpy.types.Operator):
    bl_idname = "acet.align_parent"
    bl_label = "Convert Textures"
    bl_description = "Once all Alignment empties have been placed, this will align the NR model to the KN5 model. Be sure to align empties, either manually or using the buttons before starting this operation. The empties will be created during the previous operation. If you do not see them, reload the file from before the previous operation"
    
    def execute(self, context):
        
        # Call the NR importer function to select the acs_log.txt file.
        # This references find_associated_files and _import_nr_mesh
        nr_align_and_parent()
        
        return {'FINISHED'}
        
        
# Define the operator for the Import NR button
class OBJECT_OT_acet_importnr(bpy.types.Operator):
    bl_idname = "acet.importnr"
    bl_label = "Convert Textures"
    bl_description = "This will use NR import to import the correct ripped files based of the log. This needs to be the acs_log.txt file that is created above frame_0"
    
    def execute(self, context):
        
        # Call the NR importer function to select the acs_log.txt file.
        # This references find_associated_files and _import_nr_mesh
        bpy.ops.import_nr_mesh.nr_log('INVOKE_DEFAULT')
        
        print(f"NR imported")
        
        nr_imported = True
        
        return {'FINISHED'}
        
# Define the operator for adjusting the detail value on a shader. This requires the shader setup to be configured. 
class OBJECT_OT_acet_swap_detail_value(bpy.types.Operator):
    bl_idname = "acet.swap_detail_value"
    bl_label = "Swap Detail Value"
    bl_description = "This will swap the value used to blend the diffuse and detail textures if the detail appears too strong. There are three mode and this will cycle them. This has no effect on the exported model when loading into knEditor"
    
    def execute(self, context):
        
        # Define alpha_switch_tolerance value
        alpha_switch_tolerance = 1e-6  # You can adjust this alpha_switch_tolerance based on your precision requirements
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        
                        # If nodes exist set them appropriately
                        alpha_mix_node = None
                        for node in nodes:
                            
                            if node.name == "Blend Alpha Mix":
                                alpha_mix_node = node
                                
                        if alpha_mix_node:
                            # Check if the difference is within the alpha_switch_tolerance
                            if abs(alpha_mix_node.inputs[0].default_value - 0.95) < alpha_switch_tolerance:
                                alpha_mix_node.inputs[0].default_value = 0.4
                            elif abs(alpha_mix_node.inputs[0].default_value - 0.4) < alpha_switch_tolerance:
                                alpha_mix_node.inputs[0].default_value = 0.05
                            elif abs(alpha_mix_node.inputs[0].default_value - 0.05) < alpha_switch_tolerance:
                                alpha_mix_node.inputs[0].default_value = 0.95
                            else:
                                alpha_mix_node.inputs[0].default_value = 0.95

        
        return {'FINISHED'}
        
# Define the operator for adjusting the metallic value on a shader. This requires the shader setup to be configured. 
class OBJECT_OT_acet_swap_metallic_value(bpy.types.Operator):
    bl_idname = "acet.swap_metallic_value"
    bl_label = "Swap Detail Value"
    bl_description = "This will swap the value used for metallic from texture map if the visual appears too strong. There are three mode and this will cycle them. This has no effect on the exported model when loading into knEditor"
    
    def execute(self, context):
        
        # Define alpha_switch_tolerance value
        alpha_switch_tolerance = 1e-6  # You can adjust this alpha_switch_tolerance based on your precision requirements
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        
                        # If nodes exist set them appropriately
                        math2_node = None
                        for node in nodes:
                            
                            if node.name == "TxtMap Math 2":
                                math2_node = node
                                
                        if math2_node:
                            # Check if the difference is within the alpha_switch_tolerance
                            if abs(math2_node.inputs[1].default_value - 1) < alpha_switch_tolerance:
                                math2_node.inputs[1].default_value = 0.5
                            elif abs(math2_node.inputs[1].default_value - 0.5) < alpha_switch_tolerance:
                                math2_node.inputs[1].default_value = -1
                            elif abs(math2_node.inputs[1].default_value + 1) < alpha_switch_tolerance:
                                math2_node.inputs[1].default_value = 1
                            else:
                                math2_node.inputs[1].default_value = - 1

        return {'FINISHED'}

# Define the operator for swapping the detail texture on a shader. This requires the shader setup to be configured. 
class OBJECT_OT_acet_swap_detail_texture(bpy.types.Operator):
    bl_idname = "acet.swap_detail_texture"
    bl_label = "Swap Detail Texture"
    bl_description = " This will swap the blending of the diffuse and detail textures. Use this if the textures appear backwards. This has no effect on the exported model when loading into knEditor"
    
    def execute(self, context):
    
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # If nodes exist set them appropriately
                        detail_mix_node = None
                        detail_tex_node = None
                        img_tex_node = None
                        for node in nodes:
                            
                            if node.name == "Detail Mix":
                                detail_mix_node = node
                            if node.name == "Image Texture":
                                img_tex_node = node
                            if node.name == "Image Texture.003":
                                detail_tex_node = node
                        
                        if detail_tex_node.image:
                            # Check if connections exist
                            img_tex_to_detail_mix = False
                            detail_tex_to_detail_mix = False
                            for link in links:
                                if (link.from_node == img_tex_node and link.from_socket == img_tex_node.outputs['Color'] 
                                    and link.to_node == detail_mix_node and link.to_socket == detail_mix_node.inputs[7]):
                                    img_tex_to_detail_mix = True
                                    
                                elif (link.from_node == detail_tex_node and link.from_socket == detail_tex_node.outputs['Color'] 
                                    and link.to_node == detail_mix_node and link.to_socket == detail_mix_node.inputs[6]):
                                    detail_tex_to_detail_mix = True
                                
                            # Logic
                            print(f"Connection found a: {img_tex_to_detail_mix}")
                            print(f"Connection found b: {detail_tex_to_detail_mix}")
                            if img_tex_to_detail_mix == True and detail_tex_to_detail_mix == True:
                                links.new(img_tex_node.outputs['Color'], detail_mix_node.inputs[6])
                                links.new(detail_tex_node.outputs['Color'], detail_mix_node.inputs[7])
                            else:
                                links.new(img_tex_node.outputs['Color'], detail_mix_node.inputs[7])
                                links.new(detail_tex_node.outputs['Color'], detail_mix_node.inputs[6])
                            bpy.context.view_layer.update()
        return {'FINISHED'}


# Define the operator for the "Convert" button
class OBJECT_OT_acet_convert(bpy.types.Operator):
    bl_idname = "acet.convert"
    bl_label = "Convert Textures"
    bl_description = "This will convert the existing dds files on the selected objects to png files. It will split the transparency channel to a separate image. This will also correct the uv channel to the appropriate channel, as well as configure the shaders in the blend file for use later"
    
    def execute(self, context):
        
        bpy.ops.object.select_all(action='SELECT')
        
        print(f"Objects selected.")
        
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        atex = 0
        etex = 0
        
        print(f"Starting Image name update and uv correction. This will convert DDS files to PNG files should they not exist and set the objects uv map to the correct one.")

        # The target extension
        new_extension = '.png'  # Ensure this starts with a '.'
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                
                eobj += 1
                
                # Access the object's UV maps
                uv_maps = obj.data.uv_layers
        
                # Check if the object has at least three UV maps
                if len(uv_maps) >= 3:
                    # Set the third UV map (index 2) as the active render UV map
                    uv_maps.active_index = 2
        
                    # Collect names of UV maps to be removed, except the active one
                    uv_maps_to_remove = [uv_map.name for uv_map in uv_maps if uv_map != uv_maps.active]
        
                    # Remove the collected UV maps
                    for uv_map_name in uv_maps_to_remove:
                        uv_maps.remove(uv_maps[uv_map_name])
        
                    print(f"Active UV map set to '{uv_maps.active.name}' for object '{obj.name}'.")
                else:
                    print(f"Not enough UV maps in object '{obj.name}'. Needed 3, found {len(uv_maps)}.")
        
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
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
                            material = mat_slot.material
                            
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
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                old_image_path = bpy.path.abspath(node.image.filepath)
                                directory, filename = os.path.split(old_image_path)
                                newdirectory = os.path.join(directory, "Converted")
                                basename, extension = os.path.splitext(filename)
                                
                                etex += 1
                                
                                # Print the index, node name, and image name
                                print(f"Node index: {index}, Node name: '{node.name}', Image name: '{node.image.name}'")
                                
                                print(f"OldImagePath: {old_image_path}")
        
                                # Check if the current image's extension matches the source extension we're converting from
                                if extension.lower() == '.dds':
                                    new_filename_rgb = basename + new_extension
                                    new_filename_alpha = basename + "_alpha" + new_extension
                                    new_image_path_rgb = os.path.join(newdirectory, new_filename_rgb)
                                    new_image_path_a = os.path.join(newdirectory, new_filename_alpha)
        
                                    # If the new PNG file already exists, just update the path
                                    if os.path.isfile(new_image_path_rgb) and os.path.isfile(new_image_path_a):
                                        print(f"PNG already exists at: {newdirectory}. Skipping Conversion.")
                                        
                                        # Update the node to use the existing PNG
                                        #node.image.filepath = new_image_path_rgb
                                        #node.image.reload()  # Refresh the image data
        
                                        # Update the image data block name
                                        #node.image.name = new_filename_rgb
                                        
                                    else:
                                        print(f"Converting: {old_image_path} to PNGs")
        
                                        # Perform the conversion
                                        img = node.image  # Get the current image data block
                                        
                                        # Prepare to create two new images
                                        width, height = img.size[:]
                                        pixels = list(img.pixels)  # Copy original pixel data
                                        
                                        # Prepare pixel data for two new images
                                        rgb_pixels = []
                                        alpha_pixels = []
                                        
                                        # Iterate through the original image pixel data
                                        num_channels = 4  # RGBA
                                        for i in range(0, len(pixels), num_channels):
                                            r, g, b, a = pixels[i:i+num_channels]
                                            
                                            # For the RGB image, ignore the alpha channel
                                            #rgb_pixels.extend([r, g, b, a])  # Normal file but png
                                            rgb_pixels.extend([r, g, b, 1.0])  # Setting alpha to 1.0 for full opacity
                                            
                                            # For the grayscale image, use the alpha value for R, G, and B; set alpha to 1.0
                                            alpha_pixels.extend([a, a, a, 1.0])
                                            
                                        #create the temp image files
                                        create_or_update_image(new_filename_rgb, width, height, rgb_pixels)
                                        create_or_update_image(new_filename_alpha, width, height, alpha_pixels)
        
                                        # Define the output file path with the same base name but with a .png extension
                                        output_file_path = os.path.join(newdirectory, new_filename_rgb)
                                        output_file_path_alpha = os.path.join(newdirectory, new_filename_alpha)
        
                                        # Save the images as a PNG
                                        img_rgb = bpy.data.images[new_filename_rgb + "_temp"]
                                        img_rgb.filepath_raw = output_file_path
                                        img_rgb.file_format = 'PNG'
                                        img_rgb.save()
                                        
                                        img_a = bpy.data.images[new_filename_alpha + "_temp"]
                                        img_a.filepath_raw = output_file_path_alpha
                                        img_a.file_format = 'PNG'
                                        img_a.save()
                                        
                                        bpy.data.images.remove(img_rgb)
                                        bpy.data.images.remove(img_a)
                                        
                                        ###### This is being omitted so we can retain the original dds files. They will still load in blender with the modified shader and image settings.
                                        # Update the node to use the new PNG
                                        #node.image.filepath = output_file_path
                                        #node.image.reload()  # Refresh the image data
        
                                        # Update the image data block name
                                        #node.image.name = new_filename_rgb
                                        
                                        atex += 1
        
                                        print(f"Conversion complete. PNG copies at: {output_file_path} \n")
                            
                            # Set the alpha mode to "Channel packed" this forces each channel to be seperate letting RBG channels to show without considering the alpha.
                            # Must be used with the dds files to allow them to display correctly.
                            if node.type == 'TEX_IMAGE' and node.image:
                                node.image.alpha_mode = 'CHANNEL_PACKED'
                                
        self.report({'INFO'}, 'ACET: Converted ' + str(atex) + ' of ' + str(etex) + ' Images and corrected UV on ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}
        
# The operator for importing the kn5 fbx / operator name recycled from v1 of script
class OBJECT_OT_acet_convertall(bpy.types.Operator):
    bl_idname = "acet.convertall"
    bl_label = "Convert Textures"
    bl_description = "Select fbx created from encrypted KN5. Be sure to select the Collection named Collection first"
    
    def execute(self, context):
        setup_alignment_empties_and_constraints()
        
        #this needs to take the scene as a argument somehow
        check_empty_existence(bpy.context.scene)
        
        self.report({'WARNING'}, 'ACET: Alignment Empties created. Please align the NR Empties to the ripped model and the KN5 empties to the encrypted car.')
        
        # Once the NR File is imported, we will call a separate File Dialog to bring in the FBX converted KN5 original model.
        # This will be used as our referenced for correcting the ripped model.
        bpy.ops.import_scene.fbx_to_kn5('INVOKE_DEFAULT')
        
        self.report({'INFO'}, 'ACET: FBX file imported')
        
        # Setup the alignment empties to align the ripped car to the encrypted model
        
        
        return {'FINISHED'}
        
# The operator for reading the ini persistence files and applying to the NR model
class OBJECT_OT_acet_read_ini(Operator, ImportHelper):
    bl_idname = "acet.read_ini"
    bl_label = "Read INI"
    bl_description = "This will open a dialog to select an ini file from a converted kn5. It wil then apply the correct shader values based off the material details in the ini"
    
    filename_ext = ".ini"

    def execute(self, context):
        # Get the filepath from the operator
        ini_filepath = self.filepath
        # Process the selected INI file
        main_ini_processer(ini_filepath)
        self.report({'INFO'}, 'ACET: INI file processed')
        return {'FINISHED'}
                            
def custom_ini_parser(filepath):
    material_data = {}
    current_section = None
    
    with open(filepath, 'r') as file:
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
    
def apply_material_settings_from_ini(material_data):
    # Similar implementation as before, but using the custom parsed data
    print(f"{material_data}")
    
    tex_names = []

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
            
            
            
            print(f"Use Detail: {_useDetail}")
            print(f"Detail Multiplier: {_currentDetailMult}")
            print(f"Normal Multiplier: {_currentDetailNMMult}")
            print(f"Normal Blend: {_currentDetailNormalBlend}")
            
            # Gather nodes for applying shader values to
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
            principled_bsdf_node = None
            img_tex_node = None
            img_tex_1_node = None
            img_tex_2_node = None
            img_tex_3_node = None
            img_tex_4_node = None
            img_tex_5_node = None
            img_tex_6_node = None
            img_tex_7_node = None
            img_tex_8_node = None
            img_tex_9_node = None
            img_tex_10_node = None
            
            nodes = _currentMat.node_tree.nodes
            links = _currentMat.node_tree.links
            
            print(f"Total Nodes in Material {len(nodes) - 1}")
            
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
                if node.name == "Image Texture.008":
                    img_tex_9_node = node
                    print(f"Image Texture.008: {node}")
                if node.name == "Image Texture.009":
                    img_tex_10_node = node
                
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
                
                rename_images(img_tex_1_node, tex_names[0])
            if int(_currentTextureCount) == 2:
                if _currentShader not in ("ksGrass", "ksPostFOG_MS"):
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                
                    rename_images(img_tex_1_node, tex_names[0])
                    rename_images(img_tex_2_node, tex_names[1])
                if _currentShader != "ksPerPixelNM_UVMult":
                    print(f"WARN: Shader type: {_currentShader} utilizes multipliers which are not configured for the base color or normal texture.")
            if int(_currentTextureCount) == 3:
                if _currentShader == "ksPerPixelAT_NM_emissive":
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(img_tex_2_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                    
                    links.new(img_tex_3_node.outputs['Color'], principled_bsdf_node.inputs['Emission'])
                
                    rename_images(img_tex_1_node, tex_names[0])
                    rename_images(img_tex_2_node, tex_names[1])
                    rename_images(img_tex_3_node, tex_names[2])
                if _currentShader == "ksPerPixel_dual_layer":
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                
                    rename_images(img_tex_1_node, tex_names[0])
                    rename_images(img_tex_2_node, tex_names[1])
                    rename_images(img_tex_3_node, tex_names[2])
                    print(f"WARN: Shader type: {_currentShader} utilizes layers and mask which are not configured for the shader. Mapping original color only.")
                if _currentShader == "ksPerPixelAT_NM_emissive":
                    links.new(img_tex_1_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                    
                    links.new(img_tex_2_node.outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                    
                    img_tex_2_node.image.colorspace_settings.name = 'Non-Color'
                
                    rename_images(img_tex_1_node, tex_names[0])
                    rename_images(img_tex_2_node, tex_names[1])
                    rename_images(img_tex_3_node, tex_names[2])
                    print(f"WARN: Shader type: {_currentShader} utilizes multipliers which are not configured for the base color or normal texture.")
            if int(_currentTextureCount) == 4:
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
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
            if int(_currentTextureCount) == 5:
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
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
                rename_images(img_tex_5_node, tex_names[4])
                
            #if int(_currentTextureCount) > 5:
            if int(_currentTextureCount) == 6:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
                rename_images(img_tex_5_node, tex_names[4])
                rename_images(img_tex_6_node, tex_names[5])
                
            if int(_currentTextureCount) == 7:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
                rename_images(img_tex_5_node, tex_names[4])
                rename_images(img_tex_6_node, tex_names[5])
                rename_images(img_tex_7_node, tex_names[6])
                
            if int(_currentTextureCount) == 8:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
                rename_images(img_tex_5_node, tex_names[4])
                rename_images(img_tex_6_node, tex_names[5])
                rename_images(img_tex_7_node, tex_names[6])
                rename_images(img_tex_8_node, tex_names[7])
                
            if int(_currentTextureCount) == 9:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
                rename_images(img_tex_5_node, tex_names[4])
                rename_images(img_tex_6_node, tex_names[5])
                rename_images(img_tex_7_node, tex_names[6])
                rename_images(img_tex_8_node, tex_names[7])
                rename_images(img_tex_9_node, tex_names[8])
                
            if int(_currentTextureCount) == 10:
                print(f"Currently unsupported amount of textures. Renaming of files will still occur but no shader details will be setup.")
                
                rename_images(img_tex_1_node, tex_names[0])
                rename_images(img_tex_2_node, tex_names[1])
                rename_images(img_tex_3_node, tex_names[2])
                rename_images(img_tex_4_node, tex_names[3])
                rename_images(img_tex_5_node, tex_names[4])
                rename_images(img_tex_6_node, tex_names[5])
                rename_images(img_tex_7_node, tex_names[6])
                rename_images(img_tex_8_node, tex_names[7])
                rename_images(img_tex_9_node, tex_names[8])
                rename_images(img_tex_10_node, tex_names[9])
                
# The operator for renaming image files in the shader graph
def rename_images(node, newname):
    if node is not None and node.image is not None:
        filepath = bpy.path.abspath(node.image.filepath)
        directory, filename = os.path.split(filepath)
        new_directory = os.path.join(directory, "textures")
        parent_directory = os.path.basename(os.path.dirname(directory))
        new_base, new_ext = os.path.splitext(newname)
        
        if parent_directory == "textures":
            print(f"Skipping renaming as the file is already in 'textures' directory: {filepath}")
            return
        
        if newname is not None:
            updated_filepath = os.path.join(new_directory, newname)
            
            # Check if the original filename is the same as the new name
            if filename == newname:
                print("Original filename is the same as the new name. Skipping renaming.")
                return
                
            # Check if the original filename is the same as the new name
            if os.path.exists(updated_filepath):
                print("File already moved. Skipping renaming, and assigning new image.")
                
                # Set the image node file path to the new file path
                node.image.filepath = updated_filepath
                
                # Set the name of the image node to the new file name
                node.image.name = newname
                
                # Reload the image
                node.image.reload()
                return
            
            # Create the directory if it doesn't exist
            os.makedirs(new_directory, exist_ok=True)
            
            print(f"Original filepath: {filepath}.")
            print(f"New filepath: {updated_filepath}.")
            if os.path.exists(filepath):
                # If the new file is a png, we need to convert the dds to png else it will be corrupted
                if new_ext.lower() == '.png':
                    # Perform the conversion
                    img = node.image  # Get the current image data block
                    
                    # Prepare to create new image
                    width, height = img.size[:]
                    pixels = list(img.pixels)  # Copy original pixel data
                    
                    # Prepare pixel data for two new images
                    img_pixels = []
                    
                    # Iterate through the original image pixel data
                    num_channels = 4  # RGBA
                    for i in range(0, len(pixels), num_channels):
                        r, g, b, a = pixels[i:i+num_channels]
                        
                        # For the RGB image, ignore the alpha channel
                        img_pixels.extend([r, g, b, a])  # Normal file but png
                    
                    # Create a new image file
                    new_image = bpy.data.images.new(name=newname, width=width, height=height)
                    new_image.filepath = updated_filepath  # Set the filepath for the new image
                    
                    # Assign pixel data to the new image
                    new_image.pixels = img_pixels
                    new_image.file_format = 'PNG'
                    
                    # Save the image data as a new image on disc with the updated file path
                    new_image.save()
                    
                    # Remove the newly created image from bpy.data.images
                    bpy.data.images.remove(new_image)
                else:    
                    # Copy original file to the new file path
                    shutil.copy(filepath, updated_filepath)
                
                # Set the image node file path to the new file path
                node.image.filepath = updated_filepath
                
                # Set the name of the image node to the new file name
                node.image.name = newname
                
                # Reload the image
                node.image.reload()
            
        else:
            print(f"Name missing for file, renaming will not occur for {node.name}.")
    else:
        print(f"Filepath missing for {node}, renaming will not occur for {node.name}.")
    

def main_ini_processer(ini_filepath):
    #DEBUG - ini_filepath = "D:/SteamLibrary/steamapps/common/assettocorsa/content/cars/kyu_nissan_s15_msports_kyuspec/kyu_s15_msports_kyu.fbx.ini"
    material_data = custom_ini_parser(ini_filepath)
    apply_material_settings_from_ini(material_data)
    
    

# Define the operator to move the empty to the 3D cursor
class OBJECT_OT_MoveEmptyToCursor(bpy.types.Operator):
    bl_idname = "object.move_empty_to_cursor"
    bl_label = "Move Empty to Cursor"
    bl_description = "This will align the corresponding Empty to the selected vertices. Be sure to align the empties based off their location"

    empty_name: bpy.props.StringProperty()  # Name of the empty to move

    def execute(self, context):
        # Get the empty object
        empty = bpy.data.objects.get(self.empty_name)
        if empty:
            # Set 3D cursor location to selected vertices' median point
            bpy.ops.view3d.snap_cursor_to_selected()
            # Move empty to 3D cursor location
            empty.location = context.scene.cursor.location
            # Return 3D cursor to world origin
            bpy.ops.view3d.snap_cursor_to_center()
        return {'FINISHED'}
        
# The operator for renaming a duplicate object from empty name. This is important due to how AC works with objects. Where in blender/3ds max you might just have a mesh
# AC takes that mesh and creates a Dummy/Empty of the same name. This is an issue when working with the model because it causes 2x the objects on the model.
class OBJECT_OT_RenameDuplicateObject(bpy.types.Operator):
    bl_idname = "object.renameduplicateobject"
    bl_label = "Rename Duplicated Object"
    bl_description = "This will rename a mesh object which would normally have a empty with the same name. Due to how KN5s work, if a mesh is selected with .001 in the name and a parent of the same name it will unparent the mesh, delete the parent, and rename the mesh to the original name"
                    
    def execute(self, context):
        def reparent_preserve_transform():
            selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        
            for obj in selected_objects:
                parent = obj.parent
                grandparent = parent.parent if parent else None
                
                # Check if the object's name ends with a suffix in the format ".00X"
                if parent and obj.name.endswith(tuple(".00{}".format(i) for i in range(10))):
                    expected_parent_name = obj.name.rsplit('.', 1)[0]
                    if parent.name == expected_parent_name:
                        # Store the object's current world matrix
                        world_matrix = obj.matrix_world.copy()
        
                        # Clear parent but keep the object's transform
                        bpy.ops.object.select_all(action='DESELECT')  # Ensure only the target object is selected
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
                        # Reparent to grandparent if available, and apply the stored world matrix
                        if grandparent:
                            obj.parent = grandparent
                            obj.matrix_world = world_matrix
                        
                        # Rename the object if no naming conflict is anticipated
                        if not bpy.data.objects.get(expected_parent_name):
                            obj.name = expected_parent_name
        
                        # Check if the parent can be deleted (has no other children)
                        if len(parent.children) == 0:
                            # Select and delete the parent
                            bpy.ops.object.select_all(action='DESELECT')
                            parent.select_set(True)
                            bpy.ops.object.delete()
        
                        obj.select_set(False)  # Deselect the object after processing
        
        # Ensure we're in object mode to modify object hierarchy
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        reparent_preserve_transform()
        return {'FINISHED'}
        
# The operator for removing the numbered suffix from a mesh. Use this after renaming from an empty to restore the original name.
class OBJECT_OT_Drop_Number_Suffix(bpy.types.Operator):
    bl_idname = "object.drop_number_suffix"
    bl_label = "Drop Number Suffix"
    bl_description = "This will drop the numbered suffix from a mesh. This is used if you have a mesh with .00X in the name"
                    
    def execute(self, context):
        def rename_selected_meshes():
            for obj in bpy.context.selected_objects:  # Loop through all selected objects
                if obj.type == 'MESH' and (obj.name.endswith('.001') or obj.name.endswith('.002') or obj.name.endswith('.003') or obj.name.endswith('.004') or obj.name.endswith('.005') or obj.name.endswith('.006') or obj.name.endswith('.007') or obj.name.endswith('.008') or obj.name.endswith('.009')):  # Check if it's a mesh and name ends with '.00X'
                    new_name = obj.name[:-4]  # Remove the last 4 characters ('.001') from the name
                    obj.name = new_name  # Assign the new name to the object

        # Ensure we're in object mode to modify object names
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        rename_selected_meshes()
        return {'FINISHED'}

# # The operator for validating if each alignment empty exists. This was needed due to issue with the UI logic showing the alignment buttons. 
def check_empty_existence(scene):
    if scene is None:
        return  # Exit early if scene is None

    # Check if all four empties exist in the scene
    empties_exist = all(name in bpy.data.objects for name in ["NR_Alignment_F", "NR_Alignment_R", "KN5_Alignment_F", "KN5_Alignment_R"])
    scene.is_alignment_active = empties_exist

# The operator for the updating detail multiplier value. Afffects only the UI. 
class OBJECT_OT_update_detail_multiplier(bpy.types.Operator):
    bl_idname = "object.update_detail_multiplier"
    bl_label = "Update Detail Multiplier"
    bl_description = "Update the detail multiplier value. This will change the tiling scale once applied."
    
    def execute(self, context):
        active_object = context.active_object
        
        if active_object is not None and active_object.type == 'MESH':
            material_slots = active_object.material_slots
            for slot in material_slots:
                if slot.material and slot.material.use_nodes:
                    nodes = slot.material.node_tree.nodes
                    
                    # Check if the material has a ksMaterial Detail node
                    ks_material_detail_node = None
                    for node in nodes:
                        if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                            ks_material_detail_node = node
                            break
                    
                    detail_multiplier_node = nodes.get("Detail Multiplier")
                    if detail_multiplier_node:
                        # Update the value of the Detail Multiplier node
                        detail_multiplier_node.outputs[0].default_value = context.scene.my_detail_multiplier
                        ks_material_detail_node.inputs['Detail Mult'].default_value = context.scene.my_detail_multiplier
                        break  # Stop searching after the first match
        
        return {'FINISHED'}
        
# The function for upading the multiplier from the active object.
def update_detail_multiplier_from_active_object(context):
    active_object = context.active_object
    if active_object is not None and active_object.type == 'MESH':
        for slot in active_object.material_slots:
            if slot.material and slot.material.use_nodes:
                nodes = slot.material.node_tree.nodes
                detail_multiplier_node = nodes.get("Detail Multiplier")
                if detail_multiplier_node:
                    # Assuming the detail multiplier is stored in a socket like inputs or a property
                    context.scene.my_detail_multiplier = detail_multiplier_node.outputs[0].default_value
                    break

# The operator for the updating detail multiplier value. Afffects only the UI. 
class OBJECT_OT_update_pbr_multiplier(bpy.types.Operator):
    bl_idname = "object.update_pbr_multiplier"
    bl_label = "Update PBRMultiplier"
    bl_description = "Update the PBR multiplier value. This will change the tiling scale once applied."
    
    def execute(self, context):
        active_object = context.active_object
        
        if active_object is not None and active_object.type == 'MESH':
            material_slots = active_object.material_slots
            for slot in material_slots:
                if slot.material and slot.material.use_nodes:
                    nodes = slot.material.node_tree.nodes
                    
                    # Check if the material has a ksMaterial Detail node
                    ks_material_detail_node = None
                    for node in nodes:
                        if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                            ks_material_detail_node = node
                            break
                    
                    pbr_multiplier_node = nodes.get("PBRMultiplier")
                    if pbr_multiplier_node:
                        # Update the value of the PBRMultiplier node
                        pbr_multiplier_node.outputs[0].default_value = context.scene.my_pbr_multiplier
                        ks_material_detail_node.inputs['PBR Mult'].default_value = context.scene.my_pbr_multiplier
                        break  # Stop searching after the first match
        
        return {'FINISHED'}
        
# The function for upading the multiplier from the active object.
def update_pbr_multiplier_from_active_object(context):
    active_object = context.active_object
    if active_object is not None and active_object.type == 'MESH':
        for slot in active_object.material_slots:
            if slot.material and slot.material.use_nodes:
                nodes = slot.material.node_tree.nodes
                pbr_multiplier_node = nodes.get("PBRMultiplier")
                if pbr_multiplier_node:
                    # Assuming the detail multiplier is stored in a socket like inputs or a property
                    context.scene.my_pbr_multiplier = pbr_multiplier_node.outputs[0].default_value
                    break

# Define the operator for the "Map Base Color" button
class OBJECT_OT_acet_map_basecolor(bpy.types.Operator):
    bl_idname = "acet.map_basecolor"
    bl_label = "Map Base Color"
    bl_description = "This will remap the Base Texture color back to the shader. Use this if you applied Detail or PBR and want to revert."
    
    def execute(self, context):
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # Find the ksMaterial Detail node
                        ksmaterial_node = None
                        for node in nodes:
                            if node.name == "ksMaterial Details":
                                ksmaterial_node = node
                                break  # Stop after finding the first 
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                
                                # If Principled BSDF node is found, make connections
                                if principled_bsdf_node and node.name == "Image Texture":
                                    # Connect the color output of the Image Texture node to the Base Color input of the Principled BSDF
                                    if 'Base Color' in principled_bsdf_node.inputs and 'Color' in node.outputs:
                                        links.new(node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
                                        
                                        # Set ksMaterial Detail updates
                                        ksmaterial_node.inputs[0].default_value = True #IsBaseColor
                                        #ksmaterial_node.inputs[1].default_value = True #IsNormal
                                        #ksmaterial_node.inputs[2].default_value = True #IsTextureMap
                                        ksmaterial_node.inputs[3].default_value = False #IsUseDetail
                                        ksmaterial_node.inputs[4].default_value = False #IsPBR
                                        #ksmaterial_node.inputs[5].default_value = True #IsTransparent
                                        
                                        eobj += 1
                                        
                                    # Print node index, node name, and image name
                                    print(f"Diffuse Image Node, Node index: {index}, Node name: '{node.name}', Image name: '{node.image.name}'")
                                
                                print(f"")
        self.report({'INFO'}, 'ACET: Applied Base Color map shading to ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}

# Define the operator for the "Map Normal" button
class OBJECT_OT_acet_map_normal(bpy.types.Operator):
    bl_idname = "acet.map_normal"
    bl_label = "Map Normal"
    bl_description = "This will map the Normal Texture to the shader. This can be used if you applied PBR and want to revert back to standard normal use."
    
    def execute(self, context):
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                                
                        # Check if the material has a ksMaterial Detail node
                        ksmaterial_node = None
                        for node in nodes:
                            if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                                ksmaterial_node = node
                                break
                                
                        # Find the Normal node
                        normal_map_node = None
                        for node in nodes:
                            if node.type == 'NORMAL_MAP' and node.name == "Normal Map 1":
                                normal_map_node = node
                                break  # Stop after finding the first
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                
                                # If Principled BSDF node is found, make connections
                                if principled_bsdf_node and node.name == "Image Texture.001":
                                    
                                    # Ensure the image node is set to Non-Color Data
                                    node.image.colorspace_settings.name = 'Non-Color'
                                    
                                    if not normal_map_node:
                                        # Add a Normal Map node
                                        normal_map_node = nodes.new(type='ShaderNodeNormalMap')
                                        normal_map_node.name = "Normal Map 1"
                    
                                        # Position the new node for clarity (optional)
                                        normal_map_node.location = node.location
                                        normal_map_node.location.x = -20
                                        normal_map_node.location.y = -700
                    
                                    # Connect Image Texture node to Normal Map node
                                    links.new(node.outputs['Color'], normal_map_node.inputs['Color'])
                    
                                    # Connect Normal Map node to Principled BSDF node, if it exists
                                    if principled_bsdf_node and 'Normal' in principled_bsdf_node.inputs:
                                        links.new(normal_map_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
                                        
                                        # Set ksMaterial Detail updates
                                        #ksmaterial_node.inputs[0].default_value = True #IsBaseColor
                                        ksmaterial_node.inputs[1].default_value = True #IsNormal
                                        #ksmaterial_node.inputs[2].default_value = True #IsTextureMap
                                        #ksmaterial_node.inputs[3].default_value = False #IsUseDetail
                                        ksmaterial_node.inputs[4].default_value = False #IsPBR
                                        #ksmaterial_node.inputs[5].default_value = True #IsTransparent
                                        
                                    eobj += 1
                                        
                                    # Print node index, node name, and image name
                                    print(f"Normal Image Node, Node index: {index}, Node name: '{node.name}', Image name: '{node.image.name}'")
                                
                                print(f"")
                                
        self.report({'INFO'}, 'ACET: Applied Normal Map shading to ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}

# Define the operator for the "Map Texture Map" button
class OBJECT_OT_acet_map_texture(bpy.types.Operator):
    bl_idname = "acet.map_texture"
    bl_label = "Map Texture Map"
    bl_description = "This will apply and affix Texture Map details to the shader. Use this if texture map is present."
    
    def execute(self, context):
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        separate_color_node = None
                        math1_node = None
                        math2_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                                
                        for node in nodes:
                            if node.type == 'SEPARATE_COLOR' and node.name == "TxtMap Separate Color":
                                separate_color_node = node
                                break  # Stop after finding the first
                                
                        for node in nodes:
                            if node.type == 'MATH':
                                if node.name == "TxtMap Math 1":
                                    math1_node = node
                                if node.name == "TxtMap Math 2":
                                    math2_node = node
                                    
                        # Check if the material has a ksMaterial Detail node
                        ksmaterial_node = None
                        for node in nodes:
                            if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                                ksmaterial_node = node
                                break
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                
                                # If Principled BSDF node is found, make connections
                                if principled_bsdf_node and node.name == "Image Texture.002":
                                    
                                    # Ensure the image node is set to Non-Color Data
                                    node.image.colorspace_settings.name = 'Non-Color'
                                    
                                    if separate_color_node is None:
                                        # Add a Separate Color node
                                        separate_color_node = nodes.new(type='ShaderNodeSeparateColor')
                                        separate_color_node.name = "TxtMap Separate Color"
                                        
                                        # Set Location
                                        separate_color_node.location = node.location
                                        separate_color_node.location.y -= 700
                                        
                                    if math1_node is None:
                                        # Add a first Math node
                                        math1_node = nodes.new(type='ShaderNodeMath')
                                        math1_node.name = "TxtMap Math 1"
                                        
                                        # Set default values
                                        math1_node.operation = 'MULTIPLY'
                                        math1_node.inputs[1].default_value = -1
                                        
                                        # Set Location
                                        math1_node.location = node.location
                                        math1_node.location.y -= 700
                                        math1_node.location.x += 300
                                        
                                    if math2_node is None:
                                        # Add a first Math node
                                        math2_node = nodes.new(type='ShaderNodeMath')
                                        math2_node.name = "TxtMap Math 2"
                                        
                                        # Set default values
                                        math2_node.operation = 'MULTIPLY'
                                        math2_node.inputs[1].default_value = -1
                                        
                                        # Set Location
                                        math2_node.location = node.location
                                        math2_node.location.y -= 400
                                        math2_node.location.x += 300
                                    
                    
                                    # Connect Image Texture node to Normal Map node
                                    links.new(node.outputs['Color'], separate_color_node.inputs['Color'])
                    
                                    # Connect Separate Red node to Principled BSDF node, if it exists
                                    if principled_bsdf_node and 'Specular' in principled_bsdf_node.inputs:
                                        links.new(separate_color_node.outputs[0], principled_bsdf_node.inputs['Specular'])
                                        
                                    # Connect Separate Green node to Principled BSDF node, if it exists
                                    if principled_bsdf_node and 'Roughness' in principled_bsdf_node.inputs:
                                        links.new(separate_color_node.outputs[1], math1_node.inputs[0])
                                        links.new(math1_node.outputs[0], principled_bsdf_node.inputs['Roughness'])
                                        
                                    # Connect Separate Green node to Principled BSDF node, if it exists
                                    if principled_bsdf_node and 'Metallic' in principled_bsdf_node.inputs:
                                        links.new(separate_color_node.outputs[2], math2_node.inputs[0])
                                        links.new(math2_node.outputs[0], principled_bsdf_node.inputs['Metallic'])
                                        
                                    # Set ksMaterial Detail updates
                                    #ksmaterial_node.inputs[0].default_value = True #IsBaseColor
                                    #ksmaterial_node.inputs[1].default_value = True #IsNormal
                                    ksmaterial_node.inputs[2].default_value = True #IsTextureMap
                                    #ksmaterial_node.inputs[3].default_value = False #IsUseDetail
                                    #ksmaterial_node.inputs[4].default_value = False #IsPBR
                                    #ksmaterial_node.inputs[5].default_value = True #IsTransparent
                                        
                                    eobj += 1
                                        
                                    # Print node index, node name, and image name
                                    print(f"Normal Image Node, Node index: {index}, Node name: '{node.name}', Image name: '{node.image.name}'")
                                
                                print(f"")
                                
        self.report({'INFO'}, 'ACET: Applied Texture Map shading to ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}

# Define the operator for the "Map Detail" button
class OBJECT_OT_acet_map_detail(bpy.types.Operator):
    bl_idname = "acet.map_detail"
    bl_label = "Map Detail"
    bl_description = "This will map Details texture information to the shader. Once this is set, you can apply the Detail Multiplier to scale the titling. Using this function is like having UseDetail = 1 in ksEditor."
    
    def execute(self, context):
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                                
                        # Find the Diffuse Texture node
                        base_color_node = None
                        for node in nodes:
                            if node.type == 'TEX_IMAGE' and node.name == 'Image Texture':
                                base_color_node = node
                                break  # Stop after finding the first  
                                
                        # Find the Detail Texture node
                        detail_color_node = None
                        for node in nodes:
                            if node.type == 'TEX_IMAGE' and node.name == 'Image Texture.003':
                                detail_color_node = node
                                break  # Stop after finding the first       
                                
                        # Find the Mapping node
                        mapping_node = None
                        for node in nodes:
                            if node.type == 'MAPPING' and node.name == 'Detail Mapping':
                                mapping_node = node
                                break  # Stop after finding the first
                                
                        # Find the Text Coordinate node
                        tc_node = None
                        for node in nodes:
                            if node.type == 'TEX_COORD' and node.name == 'Detail Texture Coordinate':
                                tc_node = node
                                break  # Stop after finding the first       
                                
                        # Find the Text Coordinate node
                        detail_mult_node = None
                        for node in nodes:
                            if node.type == 'VALUE' and node.name == 'Detail Multiplier':
                                detail_mult_node = node
                                break  # Stop after finding the first  
                                
                        # Find the Text Coordinate node
                        detail_mix_node = None
                        for node in nodes:
                            if node.type == 'MIX' and node.name == 'Detail Mix':
                                detail_mix_node = node
                                break  # Stop after finding the first
                                
                        # Check if the material has a ksMaterial Detail node
                        ksmaterial_node = None
                        for node in nodes:
                            if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                                ksmaterial_node = node
                                break
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                
                                # If Principled BSDF node is found, make connections
                                if principled_bsdf_node and node.name == "Image Texture.003":
                                    
                                    if not mapping_node:
                                        # Add a Normal Map node
                                        mapping_node = nodes.new(type='ShaderNodeMapping')
                                        mapping_node.name = "Detail Mapping"
                    
                                        # Position the new node for clarity (optional)
                                        mapping_node.location = node.location
                                        mapping_node.location.x = -1120
                                        mapping_node.location.y = 74
                                        
                                    if not tc_node:
                                        # Add a Normal Map node
                                        tc_node = nodes.new(type='ShaderNodeTexCoord')
                                        tc_node.name = "Detail Texture Coordinate"
                    
                                        # Position the new node for clarity (optional)
                                        tc_node.location = node.location
                                        tc_node.location.x = -1300
                                        tc_node.location.y = 74    
                                        
                                    if not detail_mult_node:
                                        # Add a Normal Map node
                                        detail_mult_node = nodes.new(type='ShaderNodeValue')
                                        detail_mult_node.name = "Detail Multiplier"
                    
                                        # Position the new node for clarity (optional)
                                        detail_mult_node.location = node.location
                                        detail_mult_node.location.x = -1310
                                        detail_mult_node.location.y = -196
                                        
                                        # Set Default Value
                                        detail_mult_node.outputs[0].default_value = 1   
                                        
                                    if not detail_mix_node:
                                        # Add a Normal Map node
                                        detail_mix_node = nodes.new(type='ShaderNodeMix')
                                        detail_mix_node.name = "Detail Mix"
                    
                                        # Position the new node for clarity (optional)
                                        detail_mix_node.location = node.location
                                        detail_mix_node.location.x = 10
                                        detail_mix_node.location.y = 570

                                    # Connect the mix nodes and set the base color on the Principled BSDF
                                    if principled_bsdf_node:
                                        links.new(detail_mix_node.outputs[2], principled_bsdf_node.inputs['Base Color'])
                                        
                                        links.new(base_color_node.outputs[0], detail_mix_node.inputs[6])
                                        
                                        links.new(detail_color_node.outputs[1], detail_mix_node.inputs[0])
                                        
                                        links.new(detail_color_node.outputs[0], detail_mix_node.inputs[7])
                                        
                                        # Connect Image Texture node to Mapping node
                                        links.new(mapping_node.outputs['Vector'], node.inputs['Vector'])
                                        # Connect Tex Coord node to Mapping node, if it exists
                                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                                        # Connect Tex Coord node to Mapping node, if it exists
                                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                                        
                                        # Set ksMaterial Detail updates
                                        ksmaterial_node.inputs[0].default_value = False #IsBaseColor
                                        #ksmaterial_node.inputs[1].default_value = True #IsNormal
                                        #ksmaterial_node.inputs[2].default_value = True #IsTextureMap
                                        ksmaterial_node.inputs[3].default_value = True #IsUseDetail
                                        ksmaterial_node.inputs[4].default_value = False #IsPBR
                                        #ksmaterial_node.inputs[5].default_value = True #IsTransparent
                                        
                                    # Set Default Value
                                    detail_mix_node.data_type = 'RGBA'
                                    detail_mix_node.blend_type = 'MIX'
                                    detail_mix_node.clamp_factor = 0
                                    detail_mix_node.clamp_result = 0
                                    detail_mix_node.factor_mode = 'NON_UNIFORM'
                                    
                                    eobj += 1
                                
        self.report({'INFO'}, 'ACET: Applied Detail shading to ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}

# Define the operator for the "Map PBR" button
class OBJECT_OT_acet_map_pbr(bpy.types.Operator):
    bl_idname = "acet.map_pbr"
    bl_label = "Map PBR"
    bl_description = "This will map PBR materials to the shader data. Use this if PBR materials were configured in the ext config for the object being used. This will have a multiplier value after being set to control titling on the material."
    
    def execute(self, context):
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                                
                        # Find the Diffuse Texture node
                        pbr_normal_node = None
                        for node in nodes:
                            if node.type == 'TEX_IMAGE' and node.name == 'Image Texture.004':
                                pbr_normal_node = node
                                break  # Stop after finding the first  
                                
                        # Find the PBR Texture node
                        pbr_color_node = None
                        for node in nodes:
                            if node.type == 'TEX_IMAGE' and node.name == 'Image Texture.003':
                                pbr_color_node = node
                                break  # Stop after finding the first       
                                
                        # Find the Mapping node
                        mapping_node = None
                        for node in nodes:
                            if node.type == 'MAPPING' and node.name == 'PBRMapping':
                                mapping_node = node
                                break  # Stop after finding the first
                                
                        # Find the Text Coordinate node
                        tc_node = None
                        for node in nodes:
                            if node.type == 'TEX_COORD' and node.name == 'PBRTexture Coordinate':
                                tc_node = node
                                break  # Stop after finding the first       
                                
                        # Find the Text Coordinate node
                        detail_mult_node = None
                        for node in nodes:
                            if node.type == 'VALUE' and node.name == 'PBRMultiplier':
                                detail_mult_node = node
                                break  # Stop after finding the first  
                                
                        # Find the Text Coordinate node
                        normal_node = None
                        for node in nodes:
                            if node.type == 'NORMAL_MAP' and node.name == 'Normal Map 1':
                                normal_node = node
                                break  # Stop after finding the first  
                                
                        # Check if the material has a ksMaterial Detail node
                        ksmaterial_node = None
                        for node in nodes:
                            if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                                ksmaterial_node = node
                                break
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                
                                # If Principled BSDF node is found, make connections
                                if principled_bsdf_node:
                                    
                                    if not mapping_node:
                                        # Add a Normal Map node
                                        mapping_node = nodes.new(type='ShaderNodeMapping')
                                        mapping_node.name = "PBRMapping"
                    
                                        # Position the new node for clarity (optional)
                                        mapping_node.location = node.location
                                        mapping_node.location.x = -1120
                                        mapping_node.location.y = -300
                                        
                                    if not tc_node:
                                        # Add a Normal Map node
                                        tc_node = nodes.new(type='ShaderNodeTexCoord')
                                        tc_node.name = "PBRTexture Coordinate"
                    
                                        # Position the new node for clarity (optional)
                                        tc_node.location = node.location
                                        tc_node.location.x = -1300
                                        tc_node.location.y = -300    
                                        
                                    if not detail_mult_node:
                                        # Add a Normal Map node
                                        detail_mult_node = nodes.new(type='ShaderNodeValue')
                                        detail_mult_node.name = "PBRMultiplier"
                    
                                        # Position the new node for clarity (optional)
                                        detail_mult_node.location = node.location
                                        detail_mult_node.location.x = -1310
                                        detail_mult_node.location.y = -570
                                        
                                        # Set Default Value
                                        detail_mult_node.outputs[0].default_value = 1   
                                        
                                    if not normal_node:
                                        # Add a Normal Map node
                                        normal_node = nodes.new(type='ShaderNodeNormalMap')
                                        normal_node.name = "Normal Map 1"
                    
                                        # Position the new node for clarity (optional)
                                        normal_node.location = node.location
                                        normal_node.location.x = -20
                                        normal_node.location.y = -700

                                    # Connect the pbr diffuse and normal on the Principled BSDF
                                    if principled_bsdf_node:
                                        links.new(pbr_color_node.outputs[0], principled_bsdf_node.inputs['Base Color'])
                                        links.new(pbr_normal_node.outputs[0], normal_node.inputs['Color'])
                                        links.new(normal_node.outputs[0], principled_bsdf_node.inputs['Normal'])
                                        
                                        # Connect Image Texture nodes to Mapping node
                                        links.new(mapping_node.outputs['Vector'], pbr_normal_node.inputs['Vector'])
                                        links.new(mapping_node.outputs['Vector'], pbr_color_node.inputs['Vector'])
                                        # Connect Tex Coord node to Mapping node, if it exists
                                        links.new(tc_node.outputs['UV'], mapping_node.inputs['Vector'])
                                        # Connect Tex Coord node to Mapping node, if it exists
                                        links.new(detail_mult_node.outputs['Value'], mapping_node.inputs['Scale'])
                                        
                                        # Configure normal image for pbr and remove alpha links so full alpha is displayed
                                        pbr_normal_node.image.colorspace_settings.name = 'Non-Color'
                                        
                                        # Set ksMaterial Detail updates
                                        ksmaterial_node.inputs[0].default_value = False #IsBaseColor
                                        ksmaterial_node.inputs[1].default_value = False #IsNormal
                                        #ksmaterial_node.inputs[2].default_value = True #IsTextureMap
                                        ksmaterial_node.inputs[3].default_value = False #IsUseDetail
                                        ksmaterial_node.inputs[4].default_value = True #IsPBR
                                        #ksmaterial_node.inputs[5].default_value = True #IsTransparent
                                        
                                        # Remove alpha links from Principled BSDF node
                                        for link in principled_bsdf_node.inputs['Alpha'].links:
                                            links.remove(link)
                                        
                                        # Set alpha to 1.0 (full opacity)
                                        principled_bsdf_node.inputs['Alpha'].default_value = 1.0

                                        
                                    
            eobj += 1
                                
        self.report({'INFO'}, 'ACET: Applied PBR Shading to ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}

# Define the operator for the "Set Transparent" button
class OBJECT_OT_acet_set_transparent(bpy.types.Operator):
    bl_idname = "acet.set_transparent"
    bl_label = "Set Transparent"
    bl_description = "This will set the alpha on the base texture in the shader data. This is disabled by default. If base texture does not have transparency in the alpha channel this will not have any effect."
    
    def execute(self, context):
        sobj = len(bpy.context.selected_objects)
        eobj = 0
        
        # Iterate over all selected objects
        for obj in bpy.context.selected_objects:
            # Ensure the object is a mesh with material slots
            if obj.type == 'MESH' and obj.material_slots:
                
                print(f"Working with current object: '{obj.name}'")
                
                eobj += 1
                    
                # Handle the texture conversion and node connections
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material.use_nodes:
                        nodes = mat_slot.material.node_tree.nodes
                        links = mat_slot.material.node_tree.links
                        
                        # Set the blend mode to Alpha Blend
                        mat_slot.material.blend_method = 'HASHED'
                        mat_slot.material.show_transparent_back = 0
                        
                        # Check if the material has a ksMaterial Detail node
                        ksmaterial_node = None
                        for node in nodes:
                            if node.type == 'GROUP' and node.name == 'ksMaterial Details':
                                ksmaterial_node = node
                                break
                        
                        # Find the Principled BSDF node
                        principled_bsdf_node = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                principled_bsdf_node = node
                                break  # Stop after finding the first Principled BSDF node
                        
                        for index, node in enumerate(nodes):
                            if node.type == 'TEX_IMAGE' and node.image:
                                
                                # If Principled BSDF node is found, make connections
                                if principled_bsdf_node and node.name == "Image Texture":
                                    # Connect the alpha output of the Image Texture node to the Alpha input of the Principled BSDF (if it exists)
                                    if 'Alpha' in node.outputs and 'Alpha' in principled_bsdf_node.inputs:
                                        links.new(node.outputs['Alpha'], principled_bsdf_node.inputs['Alpha'])
                                        
                                    # Print node index, node name, and image name
                                    print(f"Diffuse Image Node, Node index: {index}, Node name: '{node.name}', Image name: '{node.image.name}'")
                                    
                                    # Set ksMaterial Detail updates
                                    #ksmaterial_node.inputs[0].default_value = True #IsBaseColor
                                    #ksmaterial_node.inputs[1].default_value = True #IsNormal
                                    #ksmaterial_node.inputs[2].default_value = True #IsTextureMap
                                    #ksmaterial_node.inputs[3].default_value = False #IsUseDetail
                                    #ksmaterial_node.inputs[4].default_value = False #IsPBR
                                    ksmaterial_node.inputs[5].default_value = True #IsTransparent
                                
                                print(f"")
                        
        self.report({'INFO'}, 'ACET: Applied Transparency to ' + str(eobj) + '/' + str(sobj) + ' objects.')
        
        return {'FINISHED'}

# The operator for Rerig auto operation. This rigs the NR object to the KN5 dummies using a guess type algorithm. 
class OBJECT_OT_acet_rerig_auto(bpy.types.Operator):
    bl_idname = "acet.rerig_auto"
    bl_label = "ReRig Automatic"
    bl_description = "ReRig objects from the NR rip to the original skeleton. This will guess compared to how close the mesh is to the original KN5. This will also hide matches so only unmatched items can be seen after"

    def execute(self, context):
        # Create "NR" collection if it doesn't exist
        create_NR_collection()

        # Move objects not in "KN5" collection to "NR" collection
        move_objects_to_NR()

        # Remove all collections except "NR" and "KN5"
        remove_other_collections()

        # Process the objects
        process_rerig_objects()

        return {'FINISHED'}

# The operator for the Rerig manual operation. This does the same as the auto, except instead of automatic guessing it relies on you selecting the two objects it should rig. 
class OBJECT_OT_acet_rerig_manual(bpy.types.Operator):
    bl_idname = "acet.rerig_manual"
    bl_label = "ReRig Manual"
    bl_description = "ReRig objects from the NR rip to the original skeleton. Must select 2 objects. Active (last selected) object will be the target"

    def execute(self, context):
        # Process the objects
        process_rerig_single_object()

        return {'FINISHED'}

# The function for creating the NR collection. This is used for some functions to make it easier to move objects around. 
def create_NR_collection():
    collection_name = "NR"
    
    # Check if the collection already exists
    if collection_name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(collection_name)
        print(f"NR Collection created.")
    else:
        new_collection = bpy.data.collections.get(collection_name)
        print(f"NR Collection already exists.")
        
    # Link the new collection to the scene collection
    scene_collection = bpy.context.scene.collection
    scene_collection.children.link(new_collection)

# The funciton to move said objects to the NR collection. This is used with the create NR collection above.
def move_objects_to_NR():
    kn5_collection = bpy.data.collections.get("KN5")
    nr_collection = bpy.data.collections.get("NR")
    
    objcount = 0
    
    if kn5_collection and nr_collection:
        for obj in bpy.data.objects:
            # Check if the object is not in KN5 or NR collection
            if all(collection not in [kn5_collection, nr_collection] for collection in obj.users_collection):
                # Move the object to the NR collection
                nr_collection.objects.link(obj)
                objcount += 1
    print(f"Moved " + str(objcount) + " objects to the NR collection.")

# The operator for deleting other collections besides the KN5 and NR collections. It is just clutter at this point so we might as well clean it up.
def remove_other_collections():
    collections_to_keep = {"KN5", "NR"}
    collections_to_remove = [c for c in bpy.data.collections if c.name not in collections_to_keep]
    for collection in collections_to_remove:
        # Unlink objects from the collection
        for obj in collection.objects:
            collection.objects.unlink(obj)
        # Remove the collection
        bpy.data.collections.remove(collection)

# Specify this array outside of the functions as it gets emptied and reused with each run. We can dispose and save some overhead. 
mat_renames = []

# The operator for actually rerigging. The logic here follows a few different points to determine how to rig an object. We check if 
# the verticies count matches. If there are multiples we check which side of the origin the object is on. If that still matches we then
# check if the normals match. If we can not determine a match we leave it alone for manual clean up after. This function also will 
# clean up the materials as well. We grab the material from the KN5 object. If we already fixed it just apply the existing material. No dupes needed. 
def process_rerig_objects():
    # Define a function to store the original world coordinates of vertices
    def store_original_vertex_coordinates(obj):
        original_coordinates = {}
        for v in obj.data.vertices:
            original_coordinates[v.index] = obj.matrix_world @ v.co
        return original_coordinates
    
    # Define a function to reapply the original world coordinates to vertices
    def reapply_original_vertex_coordinates(obj, original_coordinates):
        for v in obj.data.vertices:
            v.co = obj.matrix_world.inverted() @ original_coordinates[v.index]
    
    # Define the collections to compare
    collection1_name = "KN5"
    collection2_name = "NR"
    
    obj_to_delete = []
    col1 = []
    col2 = []
    if isinstance(mat_renames, list):
        mat_renames.clear()
    
    # Get the collections
    collection1 = bpy.data.collections.get(collection1_name)
    collection2 = bpy.data.collections.get(collection2_name)
    
    if collection1 and collection2:
        # Create a dictionary to store objects based on vertex count
        objects_by_vertex_count = {}
    
        # Iterate through objects in collection1 and store them by vertex count
        for obj in collection1.objects:
            if obj.type == 'MESH' and obj.data:
                vertex_count = len(obj.data.vertices)
                if vertex_count not in objects_by_vertex_count:
                    objects_by_vertex_count[vertex_count] = []
                objects_by_vertex_count[vertex_count].append(obj)
    
        # Iterate through objects in collection2 and compare with collection1
        for obj2 in collection2.objects:
            if obj2.type == 'MESH' and obj2.data:
                vertex_count2 = len(obj2.data.vertices)
    
                # Check if there are matching vertex counts in collection1
                if vertex_count2 in objects_by_vertex_count:
                    matching_objects1 = objects_by_vertex_count[vertex_count2]
    
                    # Check if there is only one matching object based on vertex count
                    if len(matching_objects1) == 1 and matching_objects1[0].name not in col1 and obj2.name not in col2:
                        obj1 = matching_objects1[0]
    
                        # Store original vertex coordinates for both objects
                        original_coordinates_obj1 = store_original_vertex_coordinates(obj1)
                        original_coordinates_obj2 = store_original_vertex_coordinates(obj2)
    
                        # Remember the original transformation of the target object
                        original_matrix_world = obj2.matrix_world.copy()
    
                        # Parent the target object to the parent of the source object
                        if obj1.parent:
                            obj2.parent = obj1.parent
    
                        # Apply the transforms of the source object to the target object
                        obj2.matrix_world = obj1.matrix_world
    
                        # Rename the target object to match the name of the source object
                        obj2.name = obj1.name
    
                        # Append "_old" to the name of the source object for clarification
                        obj1.name += "_old"
    
                        # Rename the material of the target object to match the name of the source object's material
                        if obj1.active_material:
                            # Get the original material name
                            new_mat_name = obj1.active_material.name
                            
                            # Check if the material has been renamed before
                            if new_mat_name not in mat_renames:
                                if obj2.active_material.name + "_old" in mat_renames:
                                    # Create new material named temp_mat
                                    temp_mat = bpy.data.materials.new(name="temp_mat")
                                    
                                    # Assume 'temp_mat' is the material to which you want to copy nodes
                                    # 'obj2.active_material' is the material from which you're copying
                                    
                                    # First, ensure 'temp_mat' has nodes enabled and clear any existing nodes
                                    temp_mat.use_nodes = True
                                    temp_mat.node_tree.nodes.clear()
                                    
                                    # Then, copy nodes and links from 'obj2.active_material' to 'temp_mat'
                                    for node in obj2.active_material.node_tree.nodes:
                                        new_node = temp_mat.node_tree.nodes.new(type=node.bl_idname)
                                        # Copy attributes of the node
                                        for attr in dir(node):
                                            # Filter out attributes that are read-only or irrelevant for copying
                                            if not attr.startswith(("_", "bl_", "rna_", "is_", "type", "output", "inputs", "outputs")):
                                                try:
                                                    setattr(new_node, attr, getattr(node, attr))
                                                except AttributeError:
                                                    pass  # Some attributes might still be read-only; ignore these
                                    
                                    # Now, copy node links
                                    for link in obj2.active_material.node_tree.links:
                                        # Get the corresponding new nodes and sockets
                                        from_node = temp_mat.node_tree.nodes.get(link.from_node.name)
                                        to_node = temp_mat.node_tree.nodes.get(link.to_node.name)
                                        if from_node and to_node:
                                            from_socket = from_node.outputs.get(link.from_socket.name)
                                            to_socket = to_node.inputs.get(link.to_socket.name)
                                            if from_socket and to_socket:
                                                temp_mat.node_tree.links.new(from_socket, to_socket)
                                    
                                    # Rename the material with "_old"
                                    obj1.active_material.name += "_old"
                                    # Add the material name to the list of renamed materials
                                    mat_renames.append(obj1.active_material.name)
                                    # Set the material of the new object to the original material
                                    obj2.active_material = temp_mat
                                    obj2.active_material.name = new_mat_name
                                    
                                    print(f"NR Material renamed to {new_mat_name} \n")
                                else:
                                    # Rename the material with "_old"
                                    obj1.active_material.name += "_old"
                                    # Add the material name to the list of renamed materials
                                    mat_renames.append(obj1.active_material.name)
                                    # Set the material of the new object to the original material
                                    obj2.active_material.name = new_mat_name
                                    print(f"NR Material renamed to {new_mat_name} \n")

                            else:
                                # Find the original material (without "_old")
                                original_mat_name = new_mat_name.replace("_old", "")
                                found_mat = bpy.data.materials.get(original_mat_name)
                                if found_mat:
                                    # Apply the original material to the new object
                                    obj2.active_material = found_mat
                                else:
                                    # If the original material is not found something went wrong because that shit should exist
                                    print(f"Original material {new_mat_name} not found. Skipping material. \n")
                                    pass  # Add your desired handling here
    
                        # Reapply the original vertex coordinates to both objects
                        reapply_original_vertex_coordinates(obj1, original_coordinates_obj1)
                        reapply_original_vertex_coordinates(obj2, original_coordinates_obj2)
                        
                        collection1.objects.link(obj2)
                        
                        # Remove object from NR collection
                        # Remove the object from the NR collection
                        if obj2.users_collection:
                            for coll in obj2.users_collection:
                                if coll.name == collection2_name:
                                    coll.objects.unlink(obj2)
                                    break  # Assuming obj2 is only in one collection
                        
                        # Print confirmation
                        print(f"  -Single matching objects found and processed:")
                        print(f"  -Source Object: {obj1.name} -> Target Object: {obj2.name} with Material: {new_mat_name}")
                        print(f"")
                        
                        col1 += [obj1.name]
                        col2 += [obj2.name]
                        
                        #bpy.data.objects.remove(obj1, do_unlink=True)
                        obj_to_delete += [obj1.name]
                        
                        hide_object_and_parent(obj2)
                        
                        
                    elif len(matching_objects1) >= 2:
                        # Get the mesh location according to world origin (either positive or negative)
                        orig_x, orig_y, orig_avg_x, orig_avg_y = get_mesh_vertices_origin(obj2)
                        orig_no = get_face_orientation(obj2)
                        print(f"NR Object name: {obj2.name} with x dir: {orig_x} and y dir: {orig_y}. NO: {orig_no} Average X = {orig_avg_x} and Average Y = {orig_avg_y}")
                        obj1 = None
                        
                        multimatch = False
                        #threshold = 0.01  # You can adjust this value as needed
                        threshold = 0.05  # You can adjust this value as needed
                        previous_threshold_x = 100.0
                        previous_threshold_y = 100.0
                        
                        # Iterate through the duplicate objects to try to find the matching one
                        for dupe_obj in matching_objects1:
                            dupe_obj_x, dupe_obj_y, dupe_avg_x, dupe_avg_y = get_mesh_vertices_origin(dupe_obj)
                            dupe_no = get_face_orientation(dupe_obj)
                            
                            print(f"--KN5 Object name: {dupe_obj.name} with x dir: {dupe_obj_x} and y dir: {dupe_obj_y}. NO: {dupe_no} Average X = {dupe_avg_x} and Average Y = {dupe_avg_y}. Threshold X: {abs(dupe_avg_x - orig_avg_x)}, Y: {abs(dupe_avg_y - orig_avg_y)}")
                            if (dupe_obj_x == orig_x and dupe_obj_y == orig_y) and (abs(dupe_avg_x - orig_avg_x) < threshold and abs(dupe_avg_y - orig_avg_y) < threshold) and multimatch == False and "old" not in dupe_obj.name: #and (obj2.name not in col2)
                                # If X and Y direction match, the object has not matched already, there is no multimatch and the normal orientation matches
                                if obj1 is None:
                                    obj1 = dupe_obj
                                    previous_thresholds_x = abs(dupe_avg_x - orig_avg_x) 
                                    previous_thresholds_y = abs(dupe_avg_y - orig_avg_y)
                                    print(f"Object set to {obj1.name}")
                                # If a match was found already and the normal orientation matches, then we have a multi match and should not map this object.
                                elif obj1 is not None and (previous_thresholds_x > abs(dupe_avg_x - orig_avg_x) and previous_thresholds_y > abs(dupe_avg_y - orig_avg_y)):
                                    if dupe_no == orig_no:
                                        print(f"----Object {obj1.name} being unset due to lower threshold found or normal orientations being corrected.")
                                        obj1 = dupe_obj
                                        previous_thresholds_x = abs(dupe_avg_x - orig_avg_x) 
                                        previous_thresholds_y = abs(dupe_avg_y - orig_avg_y)
                                        print(f"Object set to {obj1.name}")
                                #elif obj1 is not None and dupe_no == orig_no:
                                #    multimatch = True
                                #    print(f"Multimatch found removing object")
                                else:
                                    # If we get to this point then we have confirmed that there is an existing obj1 and the normal orientation does not match
                                    #obj1 = None
                                    print(f"")
                            else:
                                if obj1 is None:
                                    obj1 = None
                                    print(f"----Object not set. Skipping match.")
                                
                        if obj1 is not None and multimatch == False:
                            
                            
                            # Store original vertex coordinates for both objects
                            original_coordinates_obj1 = store_original_vertex_coordinates(obj1)
                            original_coordinates_obj2 = store_original_vertex_coordinates(obj2)
        
                            # Remember the original transformation of the target object
                            original_matrix_world = obj2.matrix_world.copy()
        
                            # Parent the target object to the parent of the source object
                            if obj1.parent:
                                obj2.parent = obj1.parent
        
                            # Apply the transforms of the source object to the target object
                            obj2.matrix_world = obj1.matrix_world
        
                            # Rename the target object to match the name of the source object
                            obj2.name = obj1.name
        
                            # Append "_old" to the name of the source object for clarification
                            obj1.name += "_old"
        
                            # Rename the material of the target object to match the name of the source object's material
                            if obj1.active_material:
                                # Get the original material name
                                new_mat_name = obj1.active_material.name
                                
                                # Check if the material has been renamed before
                                if new_mat_name not in mat_renames:
                                    if obj2.active_material.name + "_old" in mat_renames:
                                        # Create new material named temp_mat
                                        temp_mat = bpy.data.materials.new(name="temp_mat")
                                        
                                        # Assume 'temp_mat' is the material to which you want to copy nodes
                                        # 'obj2.active_material' is the material from which you're copying
                                        
                                        # First, ensure 'temp_mat' has nodes enabled and clear any existing nodes
                                        temp_mat.use_nodes = True
                                        temp_mat.node_tree.nodes.clear()
                                        
                                        # Then, copy nodes and links from 'obj2.active_material' to 'temp_mat'
                                        for node in obj2.active_material.node_tree.nodes:
                                            new_node = temp_mat.node_tree.nodes.new(type=node.bl_idname)
                                            # Copy attributes of the node
                                            for attr in dir(node):
                                                # Filter out attributes that are read-only or irrelevant for copying
                                                if not attr.startswith(("_", "bl_", "rna_", "is_", "type", "output", "inputs", "outputs")):
                                                    try:
                                                        setattr(new_node, attr, getattr(node, attr))
                                                    except AttributeError:
                                                        pass  # Some attributes might still be read-only; ignore these
                                        
                                        # Now, copy node links
                                        for link in obj2.active_material.node_tree.links:
                                            # Get the corresponding new nodes and sockets
                                            from_node = temp_mat.node_tree.nodes.get(link.from_node.name)
                                            to_node = temp_mat.node_tree.nodes.get(link.to_node.name)
                                            if from_node and to_node:
                                                from_socket = from_node.outputs.get(link.from_socket.name)
                                                to_socket = to_node.inputs.get(link.to_socket.name)
                                                if from_socket and to_socket:
                                                    temp_mat.node_tree.links.new(from_socket, to_socket)
                                        
                                        # Rename the material with "_old"
                                        obj1.active_material.name += "_old"
                                        # Add the material name to the list of renamed materials
                                        mat_renames.append(obj1.active_material.name)
                                        # Set the material of the new object to the original material
                                        obj2.active_material = temp_mat
                                        obj2.active_material.name = new_mat_name
                                        
                                        print(f"NR Material renamed to {new_mat_name} \n")
                                    else:
                                        # Rename the material with "_old"
                                        obj1.active_material.name += "_old"
                                        # Add the material name to the list of renamed materials
                                        mat_renames.append(obj1.active_material.name)
                                        # Set the material of the new object to the original material
                                        obj2.active_material.name = new_mat_name
                                        print(f"NR Material renamed to {new_mat_name} \n")
    
                                else:
                                    # Find the original material (without "_old")
                                    original_mat_name = new_mat_name.replace("_old", "")
                                    found_mat = bpy.data.materials.get(original_mat_name)
                                    if found_mat:
                                        # Apply the original material to the new object
                                        obj2.active_material = found_mat
                                    else:
                                        # If the original material is not found something went wrong because that shit should exist
                                        print(f"Original material {new_mat_name} not found. Skipping material. \n")
                                        pass  # Add your desired handling here
        
                            # Reapply the original vertex coordinates to both objects
                            reapply_original_vertex_coordinates(obj1, original_coordinates_obj1)
                            reapply_original_vertex_coordinates(obj2, original_coordinates_obj2)
                            
                            collection1.objects.link(obj2)
                            
                            # Remove object from NR collection
                            # Remove the object from the NR collection
                            if obj2.users_collection:
                                for coll in obj2.users_collection:
                                    if coll.name == collection2_name:
                                        coll.objects.unlink(obj2)
                                        break  # Assuming obj2 is only in one collection
                            
                            # Print confirmation
                            print(f"  -Matching objects found and processed:")
                            print(f"  -Source Object: {obj1.name} -> Target Object: {obj2.name} with Material: {new_mat_name}")
                            print(f"")
                            
                            col1 += [obj1.name]
                            col2 += [obj2.name]
                            
                            #bpy.data.objects.remove(obj1, do_unlink=True)
                            obj_to_delete += [obj1.name]
                            
                            hide_object_and_parent(obj2)
                    
                    else:
                        # No matching vertex count in collection1
                        print(f"No matching vertex count in Collection 1 for Object: {obj2.name}")
                        print(f"")
    
    # Delete objectsthat are original objects. Currently this is commented out to debug if objects are being guessed incorrectly
    for obj_name in obj_to_delete:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

# The operator for manual rerig. Follows the same logic but works on sigular objects manually. 
def process_rerig_single_object():
    # Define a function to store the original world coordinates of vertices
    def store_original_vertex_coordinates(obj):
        original_coordinates = {}
        for v in obj.data.vertices:
            original_coordinates[v.index] = obj.matrix_world @ v.co
        return original_coordinates
    
    # Define a function to reapply the original world coordinates to vertices
    def reapply_original_vertex_coordinates(obj, original_coordinates):
        for v in obj.data.vertices:
            v.co = obj.matrix_world.inverted() @ original_coordinates[v.index]
            
    obj_to_delete = []
    col1 = []
    col2 = []
    
    # Define the collections to compare
    collection1_name = "KN5"
    collection2_name = "NR"
    
    # Get the collections
    collection1 = bpy.data.collections.get(collection1_name)
    collection2 = bpy.data.collections.get(collection2_name)
    
    # Get selected objects
    selected_objects = bpy.context.selected_objects
    
    # Ensure there are exactly two selected objects
    if len(selected_objects) == 2:
        # Determine the target and source objects
        target_object = bpy.context.active_object
        source_object = selected_objects[0] if selected_objects[0] != target_object else selected_objects[1]
    
        # Check if both objects are meshes
        if target_object.type == 'MESH' and source_object.type == 'MESH':
            # Store original vertex coordinates for both objects
            original_coordinates_target = store_original_vertex_coordinates(target_object)
            original_coordinates_source = store_original_vertex_coordinates(source_object)
    
            # Remember the original transformation of the target object
            original_matrix_world = target_object.matrix_world.copy()
    
            # Parent the target object to the parent of the source object
            if source_object.parent:
                target_object.parent = source_object.parent
    
            # Apply the transforms of the source object to the target object
            target_object.matrix_world = source_object.matrix_world
    
            # Rename the target object to match the name of the source object
            target_object.name = source_object.name
    
            # Append "_old" to the name of the source object for clarification
            source_object.name += "_old"
    
            # Rename the material of the target object to match the name of the source object's material
            if source_object.active_material:
                # Get the original material name
                new_mat_name = source_object.active_material.name
                
                # Check if the material has been renamed before
                if new_mat_name not in mat_renames:
                    if target_object.active_material.name + "_old" in mat_renames:
                        # Create new material named temp_mat
                        temp_mat = bpy.data.materials.new(name="temp_mat")
                        
                        # Assume 'temp_mat' is the material to which you want to copy nodes
                        # 'target_object.active_material' is the material from which you're copying
                        
                        # First, ensure 'temp_mat' has nodes enabled and clear any existing nodes
                        temp_mat.use_nodes = True
                        temp_mat.node_tree.nodes.clear()
                        
                        # Then, copy nodes and links from 'target_object.active_material' to 'temp_mat'
                        for node in target_object.active_material.node_tree.nodes:
                            new_node = temp_mat.node_tree.nodes.new(type=node.bl_idname)
                            # Copy attributes of the node
                            for attr in dir(node):
                                # Filter out attributes that are read-only or irrelevant for copying
                                if not attr.startswith(("_", "bl_", "rna_", "is_", "type", "output", "inputs", "outputs")):
                                    try:
                                        setattr(new_node, attr, getattr(node, attr))
                                    except AttributeError:
                                        pass  # Some attributes might still be read-only; ignore these
                        
                        # Now, copy node links
                        for link in target_object.active_material.node_tree.links:
                            # Get the corresponding new nodes and sockets
                            from_node = temp_mat.node_tree.nodes.get(link.from_node.name)
                            to_node = temp_mat.node_tree.nodes.get(link.to_node.name)
                            if from_node and to_node:
                                from_socket = from_node.outputs.get(link.from_socket.name)
                                to_socket = to_node.inputs.get(link.to_socket.name)
                                if from_socket and to_socket:
                                    temp_mat.node_tree.links.new(from_socket, to_socket)
                        
                        # Rename the material with "_old"
                        source_object.active_material.name += "_old"
                        # Add the material name to the list of renamed materials
                        mat_renames.append(source_object.active_material.name)
                        # Set the material of the new object to the original material
                        target_object.active_material = temp_mat
                        target_object.active_material.name = new_mat_name
                        
                        print(f"NR Material renamed to {new_mat_name} \n")
                    else:
                        # Rename the material with "_old"
                        source_object.active_material.name += "_old"
                        # Add the material name to the list of renamed materials
                        mat_renames.append(source_object.active_material.name)
                        # Set the material of the new object to the original material
                        target_object.active_material.name = new_mat_name
                        print(f"NR Material renamed to {new_mat_name} \n")
            else:
                    # Find the original material (without "_old")
                    original_mat_name = new_mat_name.replace("_old", "")
                    found_mat = bpy.data.materials.get(original_mat_name)
                    if found_mat:
                        # Apply the original material to the new object
                        target_object.active_material = found_mat
                    else:
                        # If the original material is not found something went wrong because that shit should exist
                        print(f"Original material {new_mat_name} not found. Skipping material. \n")
                        pass  # Add your desired handling here
    
            # Reapply the original vertex coordinates to both objects
            reapply_original_vertex_coordinates(target_object, original_coordinates_target)
            reapply_original_vertex_coordinates(source_object, original_coordinates_source)
            
            collection1.objects.link(target_object)
            
            # Remove object from NR collection
            # Remove the object from the NR collection
            if target_object.users_collection:
                for coll in target_object.users_collection:
                    if coll.name == collection2_name:
                        coll.objects.unlink(target_object)
                        break  # Assuming target_object is only in one collection
    
            # Print confirmation
            print(f"Objects processed:")
            print(f"Source Object: {source_object.name} -> Target Object: {target_object.name}")
            
            obj_to_delete += [source_object.name]
                            
            hide_object_and_parent(target_object)
            
            bpy.data.objects.remove(source_object, do_unlink=True)
            
        else:
            print("Both selected objects must be meshes.")
    else:
        print("Exactly two objects must be selected.")

# The function to get a meshes vertices origin. This is important when updating origins to make sure its on the mesh and not the object. 
def get_mesh_vertices_origin(mesh_obj):
    # Get the world matrix of the object
    world_matrix = mesh_obj.matrix_world
    
    # Get the world coordinates of each vertex
    world_coords = [world_matrix @ v.co for v in mesh_obj.data.vertices]
    
    # Calculate the average x and y coordinates
    avg_x = sum(coord.x for coord in world_coords) / len(world_coords)
    avg_y = sum(coord.y for coord in world_coords) / len(world_coords)
    
    # Check if the origin is in the positive or negative direction
    x_direction = "positive" if avg_x >= 0.001 else "negative" if avg_x <= -0.001 else "center"
    y_direction = "positive" if avg_y >= 0.001 else "negative" if avg_y <= -0.001 else "center"

    
    return  x_direction, y_direction , avg_x, avg_y

# The function to get the normal orientation such in facing in or facing out.
def get_face_orientation(obj):
    if obj.type != 'MESH':
        return None
    
    mesh = obj.data
    if not mesh.polygons:
        return None
    
    # Calculate the average normal vector
    average_normal = mathutils.Vector()
    for poly in mesh.polygons:
        normal = poly.normal
        average_normal += normal
    average_normal /= len(mesh.polygons)
    
    # Check if the average normal vector points outward or inward
    # You can use the dot product with the object's Z axis to determine orientation
    dot_product = obj.matrix_world.to_quaternion().inverted() @ average_normal
    if dot_product.z >= 0:
        return "outside"
    else:
        return "inside"
        
# a function to hide objects and its parents. This is used at the end of rerig to make sure you only see the stuff that needs rigging still.
def hide_object_and_parent(obj):
    obj.hide_set(True)
    if obj.parent:
        obj.parent.hide_set(True)

# The operator for creating the wheels straightening dummies. 
class OBJECT_OT_create_stage_empties(bpy.types.Operator):
    bl_idname = "object.create_stage_empties"
    bl_label = "Create Stage Empties"
    bl_description = "Creates empties for staging Wheel correction. Be sure to apply scale to all Empties and objects before using or else results can be incorrect."

    def execute(self, context):
        for name in ("WS_BOTTOM", "WS_TOP", "WS_FRONT", "WS_BACK"):
            if not bpy.data.objects.get(name):
                bpy.ops.object.empty_add(location=(0, 0, 0))
                context.active_object.name = name
        return {'FINISHED'}

# The operator for applying the wheel straightening logic.
class OBJECT_OT_apply_straightening(bpy.types.Operator):
    bl_idname = "object.apply_straightening"
    bl_label = "Apply Straightening"
    bl_description = "Straightens the selected objects based off of the empties. Make sure to select all objects related to the Wheel."

    def execute(self, context):
        # Ensure we're in object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        active_obj = bpy.context.active_object
        selected_objs = bpy.context.selected_objects
        empties_names = ["WS_BOTTOM", "WS_TOP", "WS_FRONT", "WS_BACK"]
        empties = {name: bpy.data.objects.get(name) for name in empties_names}
        isRight = False
        
        # Damped track constraint to the bottom empty and apply so it has real world coordinates before moving
        damped_track_constraint = empties["WS_BOTTOM"].constraints.new('DAMPED_TRACK')
        damped_track_constraint.target = empties["WS_TOP"]
        damped_track_constraint.track_axis = 'TRACK_Z'
        
        apply_constraint_to_object("WS_BOTTOM", "Damped Track")
        

        # Step 1: Unparent all objects while keeping transforms
        # Ensure we're in object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Deselect all objects first to ensure the operation only applies to one object at a time
        bpy.ops.object.select_all(action='DESELECT')
        
        parent_dict = {}
        for obj in selected_objs:
            if obj.type == 'MESH':
                # Clear selection
                bpy.ops.object.select_all(action='DESELECT')
                
                # Make the current object the only selected and active object
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                # Store the parent name before clearing if you wish to use it after clearing
                print(f"Object {obj.name} current parent: {obj.parent.name if obj.parent else 'None'}")
                parent_dict[obj.name] = obj.parent.name if obj.parent else None
            
                # Now, the parent_clear operator will only affect the active object
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM') # 'CLEAR', 'CLEAR_KEEP_TRANSFORM', 'CLEAR_INVERSE']
        
        # Optionally, reselect the original objects after operation is complete
        for obj in selected_objs:
            if obj.type == 'MESH':
                obj.select_set(True)

        # Step 2: Apply constraints
        # Limit distance constraint to the top empty
        limit_distance_constraint = empties["WS_TOP"].constraints.new('LIMIT_DISTANCE')
        limit_distance_constraint.target = empties["WS_BOTTOM"]
        limit_distance_constraint.distance = 0
        limit_distance_constraint.limit_mode = 'LIMITDIST_ONSURFACE'
        
        # Damped track constraint to the bottom empty
        damped_track_constraint = empties["WS_BOTTOM"].constraints.new('DAMPED_TRACK')
        damped_track_constraint.target = empties["WS_TOP"]
        damped_track_constraint.track_axis = 'TRACK_Z'
        
        # Step 3: Parent selected objects and front/back empties to the bottom empty
        for obj in selected_objs + [empties["WS_FRONT"], empties["WS_BACK"]]:
        #for obj in selected_objs:
            if obj.type == 'MESH' or obj in empties:
                obj.parent = empties["WS_BOTTOM"]
                obj.matrix_parent_inverse = empties["WS_BOTTOM"].matrix_world.inverted()
        
        # Align the top empty 1with the bottom so it is flat
        empties["WS_TOP"].location.x = empties["WS_BOTTOM"].location.x
        
        # Apply the damped track constraint
        apply_constraint_to_object("WS_BOTTOM", "Damped Track")
        
        if empties["WS_BOTTOM"].location.x < 0.0:
            isRight = True
        
        #bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.ops.object.select_all(action='DESELECT')
        #
        #for obj in selected_objs:
        #    if obj.type == 'MESH':
        #        obj.select_set(True)
        #        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        #        obj.select_set(False)
        #
        #for obj in selected_objs:
        #    if obj.type == 'MESH':
        #        obj.select_set(True)
        #
        #
        # Step 4: Ensure front and back empties are aligned on the X axis
        if empties["WS_FRONT"].location.x != empties["WS_BACK"].location.x:
            rotation_angle = self.calculate_rotation(empties["WS_FRONT"], empties["WS_BACK"], empties["WS_BOTTOM"])
            empties["WS_BOTTOM"].rotation_euler[2] += rotation_angle
            empties["WS_BOTTOM"].rotation_euler[2] += math.radians(-90)
            
        # Step 5: Do the same but for the front and back empties
        # This didn't work. I don't want to delete the code, but I sure aint going to use it
        
        ## Ensure we're in object mode
        #bpy.ops.object.mode_set(mode='OBJECT')
        #
        ## Deselect all objects first to ensure the operation only applies to one object at a time
        #bpy.ops.object.select_all(action='DESELECT')
        #
        #for obj in selected_objs + [empties["WS_FRONT"], empties["WS_BACK"]]:
        #    if obj.type == 'MESH' or obj in (empties["WS_FRONT"], empties["WS_BACK"]):
        #        # Clear selection
        #        bpy.ops.object.select_all(action='DESELECT')
        #        
        #        # Make the current object the only selected and active object
        #        obj.select_set(True)
        #        bpy.context.view_layer.objects.active = obj
        #    
        #        # Now, the parent_clear operator will only affect the active object
        #        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM') # 'CLEAR', 'CLEAR_KEEP_TRANSFORM', 'CLEAR_INVERSE']
        #
        ## Optionally, reselect the original objects after operation is complete
        #for obj in selected_objs:
        #    if obj.type == 'MESH':
        #        obj.select_set(True)
        #
        ## Damped track constraint to the bottom empty and apply so it has real world coordinates before moving
        #damped_track_constraint = empties["WS_BACK"].constraints.new('DAMPED_TRACK')
        #damped_track_constraint.target = empties["WS_FRONT"]
        #damped_track_constraint.track_axis = 'TRACK_Y'
        #
        #apply_constraint_to_object("WS_BACK", "Damped Track")
        #
        #for obj in selected_objs:
        #    if obj.type == 'MESH':
        #        obj.parent = empties["WS_BACK"]
        #        obj.matrix_parent_inverse = empties["WS_BACK"].matrix_world.inverted()
        #
        #damped_track_constraint = empties["WS_BACK"].constraints.new('DAMPED_TRACK')
        #damped_track_constraint.target = empties["WS_FRONT"]
        #damped_track_constraint.track_axis = 'TRACK_Y'
        #
        #empties["WS_FRONT"].location.x = empties["WS_BACK"].location.x
        #
        #apply_constraint_to_object("WS_BACK", "Damped Track")
            
        # Step 6: Set origin to selection for each object
        bpy.context.view_layer.objects.active = active_obj
        
        selected_objs = bpy.context.selected_objects
        set_origin_to_active_object_vertices(selected_objs)
        
        
        # Debugging: Print original parent names
        print("Original parent names:", parent_dict)
        
        # Step 7: Unparent and reapply transformations
        for obj in selected_objs:
            if obj.type == 'MESH':
                original_parent_name = parent_dict[obj.name]
                parented_wm = obj.matrix_world.copy()
                obj.parent = None
                obj.matrix_world = parented_wm
                obj.rotation_euler = (0, 0, 0)
                obj.location = (0, 0, 0)
                if isRight == False:
                    obj.rotation_euler[2] += math.radians(-180)
            
                # Debugging: Verify the original parent still exists
                if original_parent_name and original_parent_name in bpy.data.objects:
                    print(f"Re-parenting {obj.name} to {original_parent_name}")
                    obj.parent = bpy.data.objects[original_parent_name]
                else:
                    print(f"Original parent {original_parent_name} for {obj.name} not found or not specified.")
                    # Force a scene update to reflect changes
        bpy.context.view_layer.update()
        
        # Delete the empties
        for empty in empties.values():
            bpy.data.objects.remove(empty, do_unlink=True)

        return {'FINISHED'}

    def calculate_rotation(self, front_empty, back_empty, bottom_empty):
        # Calculate the vector pointing from back to front empty
        direction_vector = front_empty.location - back_empty.location
        
        # Calculate the angle of this vector relative to the global X-axis
        # Note: atan2 returns the angle in radians between the positive X-axis and the point given by the parameters
        angle = math.atan2(direction_vector.y, direction_vector.x)
        
        # Since we want to rotate around the Z-axis to align them, we need the negative of this angle
        # This is because the rotation needed to align them is in the opposite direction of the angle calculated
        return -angle
        
# A function to set the origin of the selected objects to the active object
def set_origin_to_active_object_vertices(selected_objs):
    # Save the current location of the 3D cursor
    saved_cursor_loc = bpy.context.scene.cursor.location.copy()
    
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get the active object
    active_obj = bpy.context.view_layer.objects.active
    
    # Check if the active object is a mesh
    if active_obj.type == 'MESH':
        # Deselect all objects first to ensure a clean state
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select the active object and make it the only selected object
        active_obj.select_set(True)
        bpy.context.view_layer.objects.active = active_obj

        # Switch to edit mode to select all vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Snap cursor to selected vertices
        bpy.ops.view3d.snap_cursor_to_selected()

        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Set origin for each originally selected object to the cursor's location
        for obj in selected_objs:
            obj.select_set(True)  # Ensure the object is selected for the operation
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Restore the 3D cursor's original location
        bpy.context.scene.cursor.location = saved_cursor_loc

        # Reselect originally selected objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objs:
            obj.select_set(True)
    else:
        print("Active object is not a mesh. Cannot enter edit mode.")
        
# Function to apply a constraint by its name on a given object
def apply_constraint_to_object(obj_name, constraint_name):
    # Ensure the object exists in the scene
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        print(f"Object {obj_name} not found.")
        return False

    # Make the object the active object
    bpy.context.view_layer.objects.active = obj

    # Ensure the object is selected
    obj.select_set(True)

    # Apply the constraint
    try:
        bpy.ops.constraint.apply(constraint=constraint_name, owner='OBJECT')
        print(f"Constraint {constraint_name} applied to {obj_name}.")
        return True
    except Exception as e:
        print(f"Failed to apply constraint {constraint_name} to {obj_name}: {e}")
        return False

# UI nonsense for the panel

def draw_warning(layout, warning_text):
    words = warning_text.split()
    lines = []
    current_line = ''
    for word in words:
        if len(current_line) + len(word) < 30:  # Adjust the line length as needed
            current_line += ' ' + word
        else:
            lines.append(current_line.strip())
            current_line = word
    if current_line:
        lines.append(current_line.strip())

    for line in lines:
        layout.label(text=line)

# The operator for updating objects to the selected vertices from edit mode. This is useful if you have rotating objects that are off from the origin of the parent.
class OBJECT_OT_acet_update_origin_from_edit(bpy.types.Operator):
    bl_idname = "acet.update_origin_from_edit"
    bl_label = "Update Origin From Edit"
    bl_description = "This will update the origin from selected vertices on a mesh object, if the object has parents, it will update the origin on the parents as well. This can ONLY be ran from EDIT mode. Ensure that the vertices selected are from the active object"
    
    def execute(self, context):

        def get_root_parent(obj):
            """Find the root parent of an object."""
            while obj.parent:
                obj = obj.parent
            return obj
        
        def get_highest_parent(obj, root):
            """Find the highest parent under the root object."""
            while obj.parent:
                if obj.parent != root:
                    obj = obj.parent
                else:
                    return obj
            return obj
        
        if bpy.context.active_object.mode == 'EDIT':
            
            selected_obj = bpy.context.selected_objects
            
            saved_cursor_loc = bpy.context.scene.cursor.location.copy()
            
            # Get the active object
            active_obj = bpy.context.active_object
            
            root_obj = get_root_parent(active_obj)
            
            highest_obj = get_highest_parent(active_obj, root_obj)
            
            # Find the VIEW_3D area and temporarily override the context
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    with bpy.context.temp_override(area=area):
                        bpy.ops.view3d.snap_cursor_to_selected()
                    break
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            new_orig = bpy.context.scene.cursor.location.copy()
            
            # Apply origin to Cursor position
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
            if highest_obj != root_obj or highest_obj != active_obj:
            
                highest_obj.location = new_orig
                
                bpy.context.view_layer.objects.active = highest_obj
                
                # Find the VIEW_3D area and temporarily override the context
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        with bpy.context.temp_override(area=area):
                            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                        break
                
                for obj in selected_obj:
                    if obj is not highest_obj:
                        obj.location = 0,0,0
                    
            
            # Reset 3D Cursor position  
            bpy.context.scene.cursor.location = saved_cursor_loc
            #bpy.ops.object.mode_set(mode='EDIT')
        else:
            self.report({'ERROR'}, 'ACET: Functionality only available if in EDIT mode.')
    
        return {'FINISHED'}

# The operator for upading multiple objects origins which share the same parent.
class OBJECT_OT_acet_update_origin_shared_parent(bpy.types.Operator):
    bl_idname = "acet.update_origin_shared_parent"
    bl_label = "Update Origin Shared Parent"
    bl_description = "This will update the origin of the selected objects. Use this if the objects share a parent dummy. Must select the object itself not the dummies."
    
    def execute(self, context):
        
        def get_root_parent(obj):
            while obj.parent:
                obj = obj.parent
            return obj
        
        def calculate_world_mesh_center(obj):
            # This calculates the mesh center in world space
            mesh = obj.data
            vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
            center = sum(vertices, mathutils.Vector()) / len(vertices)
            return center
        
        def adjust_parent_and_origin(obj, new_world_origin):
            # Store original vertex coordinates in world space
            orig_vert = store_original_vertex_coordinates(obj)
            
            # Calculate difference between new origin and current location in world space
            offset = new_world_origin - obj.matrix_world.translation
            
            # Move parent to the new origin (which is the calculated center of mesh in world space)
            if obj.parent:
                obj.parent.matrix_world.translation += offset
            
            # Set object's local location to (0,0,0), making it appear at the parent's location
            obj.matrix_world.translation = new_world_origin
            
            # Reapply the original vertex coordinates
            reapply_original_vertex_coordinates(obj, orig_vert)
        
        def store_original_vertex_coordinates(obj):
            original_coordinates = {}
            for v in obj.data.vertices:
                # Store world space coordinates of the vertices
                original_coordinates[v.index] = obj.matrix_world @ v.co
            return original_coordinates
        
        def reapply_original_vertex_coordinates(obj, original_coordinates):
            world_matrix_inverse = obj.matrix_world.inverted()
            for v_index, co in original_coordinates.items():
                # Apply the inverse world matrix to bring vertices back to their original world space locations
                obj.data.vertices[v_index].co = world_matrix_inverse @ co
            obj.data.update()
        
        selected_objs = bpy.context.selected_objects
        saved_cursor_loc = bpy.context.scene.cursor.location.copy()
        
        # Get the root parent
        root_parent = get_root_parent(selected_objs[0])
        
        for obj in selected_objs:
            parent_obj = obj.parent
            if parent_obj.parent is not root_parent:
                # Your existing logic here remains unchanged
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                saved_x = obj.location.x - obj.parent.location.x
                saved_y = obj.location.y - obj.parent.location.y
                saved_z = obj.location.z - obj.parent.location.z
                obj.parent.location.x = obj.location.x
                obj.parent.location.y = obj.location.y
                obj.parent.location.z = obj.location.z
                if obj.parent:
                    obj.location.x -= saved_x
                    obj.location.y -= saved_y
                    obj.location.z -= saved_z
            else:
                # For the 'else' case, adjust as needed
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
        
                # Calculate the world mesh center
                world_mesh_center = calculate_world_mesh_center(obj)
        
                # Adjust the object and parent based on the new world mesh center
                adjust_parent_and_origin(obj, world_mesh_center)

        
        self.report({'INFO'}, 'ACET: Origins updated on objects.')
        
        return {'FINISHED'}

# Define the panel for the custom tab
class OBJECT_PT_acet_panel(bpy.types.Panel):
    bl_label = "AC Encryption Tools"
    bl_idname = "OBJECT_PT_acet_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ACET'  # Specify the tab's name here
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        empty_prop = scene.is_alignment_active
        
        box = layout.box()
        box.label(text="WARNING", icon='ERROR')
        draw_warning(box, "Please be sure to save before each operation. Failure to do so may result in loss of project.")
        
        # Text block that says "Standard Conversion"
        row = layout.row()
        row.label(text="Standard Operations", icon='PLUS')
        
        layout.operator("acet.importnr", text="1. Import NR")
        
        # "Convert" button
        layout.operator("acet.convert", text="2. Configure NR")
        
        # "Convert" button
        layout.operator("acet.convertall", text="3. Import FBX (KN5)")
        
        # "Convert" button
        layout.operator("acet.align_parent", text="4. Align KN5 and NR")
        
        # Draw the buttons only if the empties exist
        if empty_prop:
            row = layout.row()
            # Draw the buttons for NR empties
            row.operator("object.move_empty_to_cursor", text="NR F", icon='EMPTY_DATA').empty_name = "NR_Alignment_F"
            row.operator("object.move_empty_to_cursor", text="NR R", icon='EMPTY_DATA').empty_name = "NR_Alignment_R"
    
            row = layout.row()
            # Draw the buttons for KN5 empties
            row.operator("object.move_empty_to_cursor", text="KN5 F", icon='EMPTY_DATA').empty_name = "KN5_Alignment_F"
            row.operator("object.move_empty_to_cursor", text="KN5 R", icon='EMPTY_DATA').empty_name = "KN5_Alignment_R"
            
            row = layout.row()
            row.separator()
        
        # "Automatic Rerig button" button
        layout.operator("acet.rerig_auto", text="5. ReRig - Auto")
        
        # "Manual rerig" button
        layout.operator("acet.rerig_manual", text="6. ReRig - Manual")
        
        # "Read INI" button
        layout.operator("acet.read_ini", text="7. Read INI and Apply")
        
        # "Revert" button
        #layout.operator("acet.ddsrevert", text="Revert to DDS")
        
        #row = layout.row()
        #row.alignment = 'CENTER'
        #row.label(text="_________________________", icon='NONE')
        
        # Separator
        layout.separator()
        
        row = layout.row()
        row.label(text="Post Conversion Operations", icon='PLUS')
        
        # Check for the existence of the empties
        empties_exist = all([bpy.data.objects.get(name) for name in ("WS_BOTTOM", "WS_TOP", "WS_FRONT", "WS_BACK")])
    
        if not empties_exist:
            layout.operator("object.create_stage_empties", icon='NONE', text="Stage Wheel Straightening")
        else:
            self.draw_move_empty_buttons(layout)
    
            # Assuming this button should always appear after the empties are created
            layout.operator("object.apply_straightening", icon='NONE', text="Apply Straightening")
            
        # Update origin from active selected verticies for object and parents
        layout.operator("acet.update_origin_from_edit", icon='NONE', text="Update Origin From Edit")
        
        # Update origin from active selected verticies for object and parents
        layout.operator("acet.update_origin_shared_parent", icon='NONE', text="Update Origin Shared Parent")
        
        # Update origin from active selected verticies for object and parents
        layout.operator("object.renameduplicateobject", icon='NONE', text="Rename Mesh From Empty")
        
        # Update origin from active selected verticies for object and parents
        layout.operator("object.drop_number_suffix", icon='NONE', text="Drop Numbered Suffix")
            
            
        # Layout prop DO NOT DELETE
        # Layout prop DO NOT DELETE
        layout.prop(context.scene, "show_collapsible_section", text="Shader Options")
        
        # Check if the boolean property is True, if so, display the collapsible section
        if scene.show_collapsible_section:
            box = layout.box()
            box.label(text="Visual Options")
            
            # Swap Detail Value
            box.operator("acet.swap_detail_value", text="Swap Detail Value")
            
            # Swap Detail Value
            box.operator("acet.swap_detail_texture", text="Swap Detail Texture")
            
            # Swap Detail Value
            box.operator("acet.swap_metallic_value", text="Swap Metallic Value")
            
            box.separator()
            
            box.label(text="Manual Add Shader")
            
            # "Map Base Color" button
            box.operator("acet.map_basecolor", text="Map Base Color")
            
            # "Map Normal" button
            box.operator("acet.map_normal", text="Map Normal")
            
            # "Map Texture Map" button
            box.operator("acet.map_texture", text="Map Texture Map")
            
            # "Map Detail" button
            box.operator("acet.map_detail", text="Map Detail")
            active_object = context.active_object
            if active_object is not None and active_object.type == 'MESH':
                material_slots = active_object.material_slots
                for slot in material_slots:
                    if slot.material and slot.material.use_nodes:
                        nodes = slot.material.node_tree.nodes
                        detail_multiplier_node = nodes.get("Detail Multiplier")
                        detail_mix_node = nodes.get("Detail Mix")
                        pbsdf_node = nodes.get("Principled BSDF")
                        if detail_multiplier_node:
                            # Check if Principled BSDF node and Detail Mix node are linked
                            if pbsdf_node and detail_mix_node:
                                link_exists = False
                                for link in slot.material.node_tree.links:
                                    if (link.from_node == pbsdf_node and link.to_node == detail_mix_node) or (link.from_node == detail_mix_node and link.to_node == pbsdf_node):
                                        link_exists = True
                                        break
                                if link_exists:
                                    # Display a float number box for the Detail Multiplier value
                                    box.prop(context.scene, "my_detail_multiplier", text="Detail Multiplier")
                                    box.operator("object.update_detail_multiplier", text="Update Detail Mult")
                                else:
                                    box.label(text="Detail not applied.")
                            else:
                                box.label(text="Detail not applied.")
                        else:
                            # If the node doesn't exist, display a message
                            box.label(text="Detail not applied.")
            else:
                box.label(text="Select a mesh object to use this tool.")
            
            
            # "Map pbr" button
            box.operator("acet.map_pbr", text="Map PBR")
            if active_object is not None and active_object.type == 'MESH':
                material_slots = active_object.material_slots
                for slot in material_slots:
                    if slot.material and slot.material.use_nodes:
                        nodes = slot.material.node_tree.nodes
                        pbr_multiplier_node = nodes.get("PBRMultiplier")
                        pbr_normal_node = nodes.get("Image Texture.004")
                        normal_node = nodes.get("Normal Map 1")
                        if pbr_multiplier_node:
                            # Check if normal map node and pbr normal node are linked
                            if normal_node and pbr_normal_node:
                                link_exists = False
                                for link in slot.material.node_tree.links:
                                    if (link.from_node == normal_node and link.to_node == pbr_normal_node) or (link.from_node == pbr_normal_node and link.to_node == normal_node):
                                        link_exists = True
                                        break
                                if link_exists:
                                    # Display a float number box for the pbr Multiplier value
                                    box.prop(context.scene, "my_pbr_multiplier", text="PBR Multiplier")
                                    box.operator("object.update_pbr_multiplier", text="Update PBR Mult")
                                else:
                                    box.label(text="PBR not applied.")
                            else:
                                box.label(text="PBR not applied.")
                        else:
                            # If the node doesn't exist, display a message
                            box.label(text="PBR not applied.")
            else:
                box.label(text="Select a mesh object to use this tool.")
            
            # "Set Transparent" button
            box.operator("acet.set_transparent", text="Set Transparent")
            
         
        
                
        #row = layout.row()
        #row.alignment = 'CENTER'
        #row.label(text="_________________________", icon='NONE')
        
        # Separator
        layout.separator()
        
        # Text block that says "Merging Operations"
        #row = layout.row()
        #row.label(text="Merging Operations", icon='DOT')
        
        # "Merge Material" button
        #layout.operator("acet.merge_material", text="Merge Material")
        
        # "Delete Unused Materials" button
        #layout.operator("acet.remove_material", text="Delete Unused Mats")
        
        # "Export" button
        #layout.operator("acet.export_material_details", text="Export Mat Details")
        
    def draw_move_empty_buttons(self, layout):
        # Logic to draw the move empty buttons
        row = layout.row()
        row.operator("object.move_empty_to_cursor", text="TOP", icon='EMPTY_DATA').empty_name = "WS_TOP"
        
        row = layout.row()
        row.operator("object.move_empty_to_cursor", text="FRONT", icon='EMPTY_DATA').empty_name = "WS_FRONT"
        row.operator("object.move_empty_to_cursor", text="BACK", icon='EMPTY_DATA').empty_name = "WS_BACK"
        
        row = layout.row()
        row.operator("object.move_empty_to_cursor", text="BOTTOM", icon='EMPTY_DATA').empty_name = "WS_BOTTOM"
        

# ----------------------------------------------------------------------------

# Handle registration of all objects and functions

def register_handlers():
    bpy.app.handlers.depsgraph_update_post.append(active_object_change_handler)
    bpy.app.handlers.depsgraph_update_post.append(check_empty_existence)


def unregister_handlers():
    bpy.app.handlers.depsgraph_update_post.remove(active_object_change_handler)
    bpy.app.handlers.depsgraph_update_post.remove(check_empty_existence)


# Register the operators and panel
def register():
    bpy.types.Scene.my_detail_multiplier = bpy.props.FloatProperty(
        name="My Detail Multiplier",
        default=1.0,
        min=0.0,
        description="Detail Multiplier Value"
    )
    
    bpy.types.Scene.my_pbr_multiplier = bpy.props.FloatProperty(
        name="My PBRMultiplier",
        default=1.0,
        min=0.0,
        description="PBRMultiplier Value"
    )
    
    bpy.types.Scene.is_alignment_active = bpy.props.BoolProperty(
        name="Is Alignment Active",
        default=False,
        description="Check if alignment empties exist"
    )
    
    bpy.types.Scene.show_collapsible_section = bpy.props.BoolProperty(
        name="Show Collapsible Section",
        default=False
    )
    
    #bpy.utils.register_class(OBJECT_OT_acet_export_material_details)
    bpy.utils.register_class(OBJECT_OT_update_pbr_multiplier)
    bpy.utils.register_class(OBJECT_OT_update_detail_multiplier)
    bpy.utils.register_class(OBJECT_OT_acet_convert)
    bpy.utils.register_class(OBJECT_OT_acet_importnr)
    #bpy.utils.register_class(OBJECT_OT_acet_ddsrevert)
    bpy.utils.register_class(OBJECT_OT_acet_convertall)
    bpy.utils.register_class(OBJECT_OT_acet_alignparent)
    bpy.utils.register_class(OBJECT_OT_acet_map_basecolor)
    bpy.utils.register_class(OBJECT_OT_acet_map_normal)
    bpy.utils.register_class(OBJECT_OT_acet_map_texture)
    bpy.utils.register_class(OBJECT_OT_acet_map_detail)
    bpy.utils.register_class(OBJECT_OT_acet_map_pbr)
    bpy.utils.register_class(OBJECT_OT_acet_set_transparent)
    #bpy.utils.register_class(OBJECT_OT_acet_merge_material)
    #bpy.utils.register_class(OBJECT_OT_acet_remove_material)
    bpy.utils.register_class(OBJECT_PT_acet_panel)
    bpy.utils.register_class(OpenNRFilebrowser)
    bpy.utils.register_class(OpenFBXFilebrowser)
    bpy.utils.register_class(OBJECT_OT_MoveEmptyToCursor)
    bpy.utils.register_class(OBJECT_OT_acet_rerig_auto)
    bpy.utils.register_class(OBJECT_OT_acet_rerig_manual)
    bpy.utils.register_class(OBJECT_OT_acet_read_ini)
    bpy.utils.register_class(OBJECT_OT_acet_swap_detail_value)
    bpy.utils.register_class(OBJECT_OT_acet_swap_metallic_value)
    bpy.utils.register_class(OBJECT_OT_acet_swap_detail_texture)
    bpy.utils.register_class(OBJECT_OT_create_stage_empties)
    bpy.utils.register_class(OBJECT_OT_apply_straightening)
    bpy.utils.register_class(OBJECT_OT_acet_update_origin_from_edit)
    bpy.utils.register_class(OBJECT_OT_acet_update_origin_shared_parent)
    bpy.utils.register_class(OBJECT_OT_RenameDuplicateObject)
    bpy.utils.register_class(OBJECT_OT_Drop_Number_Suffix)
    

    register_handlers()

# Unregister the operators and panel
def unregister():
    #bpy.utils.unregister_class(OBJECT_OT_acet_export_material_details)
    bpy.utils.unregister_class(OBJECT_OT_acet_importnr)
    bpy.utils.unregister_class(OBJECT_OT_acet_convert)
    bpy.utils.unregister_class(OBJECT_OT_acet_convertall)
    bpy.utils.unregister_class(OBJECT_OT_acet_alignparent)
    #bpy.utils.unregister_class(OBJECT_OT_acet_ddsrevert)
    bpy.utils.unregister_class(OBJECT_OT_acet_map_basecolor)
    bpy.utils.unregister_class(OBJECT_OT_acet_map_normal)
    bpy.utils.unregister_class(OBJECT_OT_acet_map_texture)
    bpy.utils.unregister_class(OBJECT_OT_acet_map_detail)
    bpy.utils.unregister_class(OBJECT_OT_acet_map_pbr)
    bpy.utils.unregister_class(OBJECT_OT_acet_set_transparent)
    #bpy.utils.unregister_class(OBJECT_OT_acet_merge_material)
    #bpy.utils.unregister_class(OBJECT_OT_acet_remove_material)
    bpy.utils.unregister_class(OBJECT_PT_acet_panel)
    bpy.utils.unregister_class(OBJECT_OT_update_detail_multiplier)
    bpy.utils.unregister_class(OBJECT_OT_update_pbr_multiplier)
    bpy.utils.unregister_class(OpenNRFilebrowser)
    bpy.utils.unregister_class(OpenFBXFilebrowser)
    bpy.utils.unregister_class(OBJECT_OT_MoveEmptyToCursor)
    bpy.utils.unregister_class(OBJECT_PT_acet_panel)
    bpy.utils.unregister_class(OBJECT_OT_acet_rerig_auto)
    bpy.utils.unregister_class(OBJECT_OT_acet_rerig_manual)
    bpy.utils.unregister_class(OBJECT_OT_acet_read_ini)
    bpy.utils.unregister_class(OBJECT_OT_acet_swap_detail_value)
    bpy.utils.unregister_class(OBJECT_OT_acet_swap_metallic_value)
    bpy.utils.unregister_class(OBJECT_OT_acet_swap_detail_texture)
    bpy.utils.unregister_class(OBJECT_OT_create_stage_empties)
    bpy.utils.unregister_class(OBJECT_OT_apply_straightening)
    bpy.utils.unregister_class(OBJECT_OT_acet_update_origin_from_edit)
    bpy.utils.unregister_class(OBJECT_OT_acet_update_origin_shared_parent)
    bpy.utils.unregister_class(OBJECT_OT_RenameDuplicateObject)
    bpy.utils.unregister_class(OBJECT_OT_Drop_Number_Suffix)
    
    del bpy.types.Scene.my_pbr_multiplier
    del bpy.types.Scene.my_detail_multiplier
    del bpy.types.Scene.is_alignment_active
    del bpy.types.Scene.show_collapsible_section
    
    unregister_handlers()
    


if __name__ == "__main__":
    register()
