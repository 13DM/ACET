import bpy
import textwrap 
import mathutils


#---------------------------------------------------------------------------------------------
#---------------------------------------- Settings- ------------------------------------------
#---------------------------------------------------------------------------------------------

class MySettings(bpy.types.PropertyGroup):
	# ---------------- LEFT FRONT -------------------------------------

    #Hub properties
    lf_hub_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF HUB DUMMY")
    lf_hub_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF HUB DIR")
    lf_hub_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF HUB MESH", options={'LIBRARY_EDITABLE'})
    active_lf_hub_mesh_index: bpy.props.IntProperty(name="Active LF HUB Mesh Index", default=0)
    lf_hub_stiffness: bpy.props.FloatProperty(name="LF HUB STIFFNESS", description="The stiffness of the hub when looking at the pivot point. Default Value is 0.18", default=0.18, min=0.0, max=1.0 )
    
    #LCA properties
    lf_lca_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF LCA DUMMY")
    lf_lca_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF LCA DIR")
    lf_lca_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF LCA MESH", options={'LIBRARY_EDITABLE'})
    active_lf_lca_mesh_index: bpy.props.IntProperty(name="Active LF LCA Mesh Index", default=0)
    
    #Tension properties
    lf_tension_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF TENSION DUMMY")
    lf_tension_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF TENSION DIR")
    lf_tension_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF TENSION MESH", options={'LIBRARY_EDITABLE'})
    active_lf_tension_mesh_index: bpy.props.IntProperty(name="Active LF TENSION Mesh Index", default=0)
    
    #Suspension properties
    lf_susp_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF SUSP DUMMY")
    lf_susp_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF SUSP DIR")
    lf_susp_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF SUSP MESH", options={'LIBRARY_EDITABLE'})
    active_lf_susp_mesh_index: bpy.props.IntProperty(name="Active LF Susp Mesh Index", default=0)
    
    #Coilover properties
    lf_coil_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF COILOVER DUMMY")
    lf_coil_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF COILOVER DIR")
    lf_coil_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF COILOVER MESH", options={'LIBRARY_EDITABLE'})
    active_lf_coil_mesh_index: bpy.props.IntProperty(name="Active LF Coilover Mesh Index", default=0)
    
    #Spring properties
    lf_spring_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF SPRING DUMMY")
    lf_spring_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF SPRING DIR")
    lf_spring_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF SPRING MESH", options={'LIBRARY_EDITABLE'})
    active_lf_spring_mesh_index: bpy.props.IntProperty(name="Active LF spring Mesh Index", default=0)
    
    #Steer properties
    lf_steer_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF steer DUMMY")
    lf_steer_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="LF steer DIR")
    lf_steer_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF steer MESH", options={'LIBRARY_EDITABLE'})
    active_lf_steer_mesh_index: bpy.props.IntProperty(name="Active LF steer Mesh Index", default=0)
    
    #Wheel properties
    lf_wheel_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF WHEEL DUMMY")
    lf_wheel_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LV WHEEL MESH", options={'LIBRARY_EDITABLE'})
    active_lf_wheel_mesh_index: bpy.props.IntProperty(name="Active LF Wheel Mesh Index", default=0)
    
    #Rim properties
    lf_rim_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF rim DUMMY")
    lf_rim_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF rim MESH", options={'LIBRARY_EDITABLE'})
    active_lf_rim_mesh_index: bpy.props.IntProperty(name="Active LF rim Mesh Index", default=0)
    
    #Tyre properties
    lf_tyre_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="LF tyre DUMMY")
    lf_tyre_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LF tyre MESH", options={'LIBRARY_EDITABLE'})
    active_lf_tyre_mesh_index: bpy.props.IntProperty(name="Active LF tyre Mesh Index", default=0)
    
    #Boolean properties for use on checking configuration prior to Animating
    lf_hub_parent: bpy.props.BoolProperty(name="LF Hub Parent", default=False)
    lf_hub_configured: bpy.props.BoolProperty(name="LF Hub Configured", default=False)
    lf_lca_parent: bpy.props.BoolProperty(name="LF LCA Parent", default=False)
    lf_lca_configured: bpy.props.BoolProperty(name="LF LCA Configured", default=False)
    lf_tension_parent: bpy.props.BoolProperty(name="LF Tension Parent", default=False)
    lf_tension_configured: bpy.props.BoolProperty(name="LF Tension Configured", default=False)
    lf_susp_parent: bpy.props.BoolProperty(name="LF Susp Parent", default=False)
    lf_coilover_parent: bpy.props.BoolProperty(name="LF Coilover Parent", default=False)
    lf_coilover_configured: bpy.props.BoolProperty(name="LF Coilover Configured", default=False)
    lf_spring_parent: bpy.props.BoolProperty(name="LF Spring Parent", default=False)
    lf_spring_configured: bpy.props.BoolProperty(name="LF Spring Configured", default=False)
    lf_steer_parent: bpy.props.BoolProperty(name="LF Steer Parent", default=False)
    lf_steer_configured: bpy.props.BoolProperty(name="LF Steer Configured", default=False)
    lf_wheel_parent: bpy.props.BoolProperty(name="LF Wheel Parent", default=False)
    lf_rim_parent: bpy.props.BoolProperty(name="LF Rim Parent", default=False)
    lf_tyre_parent: bpy.props.BoolProperty(name="LF Tyre Parent", default=False)
	
	# ---------------- RIGHT FRONT -------------------------------------
	
	#Hub properties
    rf_hub_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF HUB DUMMY")
    rf_hub_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF HUB DIR")
    rf_hub_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF HUB MESH", options={'LIBRARY_EDITABLE'})
    active_rf_hub_mesh_index: bpy.props.IntProperty(name="Active RF HUB Mesh Index", default=0)
    rf_hub_stiffness: bpy.props.FloatProperty(name="RF HUB STIFFNESS", description="The stiffness of the hub when looking at the pivot point. Default Value is 0.18", default=0.18, min=0.0, max=1.0 )
    
    #LCA properties
    rf_lca_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF LCA DUMMY")
    rf_lca_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF LCA DIR")
    rf_lca_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF LCA MESH", options={'LIBRARY_EDITABLE'})
    active_rf_lca_mesh_index: bpy.props.IntProperty(name="Active RF LCA Mesh Index", default=0)
    
    #Tension properties
    rf_tension_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF TENSION DUMMY")
    rf_tension_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF TENSION DIR")
    rf_tension_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF TENSION MESH", options={'LIBRARY_EDITABLE'})
    active_rf_tension_mesh_index: bpy.props.IntProperty(name="Active RF TENSION Mesh Index", default=0)
    
    #Suspension properties
    rf_susp_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF SUSP DUMMY")
    rf_susp_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF SUSP DIR")
    rf_susp_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF SUSP MESH", options={'LIBRARY_EDITABLE'})
    active_rf_susp_mesh_index: bpy.props.IntProperty(name="Active RF Susp Mesh Index", default=0)
    
    #Coilover properties
    rf_coil_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF COILOVER DUMMY")
    rf_coil_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF COILOVER DIR")
    rf_coil_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF COILOVER MESH", options={'LIBRARY_EDITABLE'})
    active_rf_coil_mesh_index: bpy.props.IntProperty(name="Active RF Coilover Mesh Index", default=0)
    
    #Spring properties
    rf_spring_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF SPRING DUMMY")
    rf_spring_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF SPRING DIR")
    rf_spring_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF SPRING MESH", options={'LIBRARY_EDITABLE'})
    active_rf_spring_mesh_index: bpy.props.IntProperty(name="Active RF spring Mesh Index", default=0)
    
    #Steer properties
    rf_steer_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF steer DUMMY")
    rf_steer_dir: bpy.props.PointerProperty(type=bpy.types.Object, name="RF steer DIR")
    rf_steer_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF steer MESH", options={'LIBRARY_EDITABLE'})
    active_rf_steer_mesh_index: bpy.props.IntProperty(name="Active RF steer Mesh Index", default=0)
    
    #Wheel properties
    rf_wheel_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF WHEEL DUMMY")
    rf_wheel_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="LV WHEEL MESH", options={'LIBRARY_EDITABLE'})
    active_rf_wheel_mesh_index: bpy.props.IntProperty(name="Active RF Wheel Mesh Index", default=0)
    
    #Rim properties
    rf_rim_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF rim DUMMY")
    rf_rim_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF rim MESH", options={'LIBRARY_EDITABLE'})
    active_rf_rim_mesh_index: bpy.props.IntProperty(name="Active RF rim Mesh Index", default=0)
    
    #Tyre properties
    rf_tyre_dummy: bpy.props.PointerProperty(type=bpy.types.Object, name="RF tyre DUMMY")
    rf_tyre_mesh: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name="RF tyre MESH", options={'LIBRARY_EDITABLE'})
    active_rf_tyre_mesh_index: bpy.props.IntProperty(name="Active RF tyre Mesh Index", default=0)
    
    #Boolean properties for use on checking configuration prior to Animating
    rf_hub_parent: bpy.props.BoolProperty(name="RF Hub Parent", default=False)
    rf_hub_configured: bpy.props.BoolProperty(name="RF Hub Configured", default=False)
    rf_lca_parent: bpy.props.BoolProperty(name="RF LCA Parent", default=False)
    rf_lca_configured: bpy.props.BoolProperty(name="RF LCA Configured", default=False)
    rf_tension_parent: bpy.props.BoolProperty(name="RF Tension Parent", default=False)
    rf_tension_configured: bpy.props.BoolProperty(name="RF Tension Configured", default=False)
    rf_susp_parent: bpy.props.BoolProperty(name="RF Susp Parent", default=False)
    rf_coilover_parent: bpy.props.BoolProperty(name="RF Coilover Parent", default=False)
    rf_coilover_configured: bpy.props.BoolProperty(name="RF Coilover Configured", default=False)
    rf_spring_parent: bpy.props.BoolProperty(name="RF Spring Parent", default=False)
    rf_spring_configured: bpy.props.BoolProperty(name="RF Spring Configured", default=False)
    rf_steer_parent: bpy.props.BoolProperty(name="RF Steer Parent", default=False)
    rf_steer_configured: bpy.props.BoolProperty(name="RF Steer Configured", default=False)
    rf_wheel_parent: bpy.props.BoolProperty(name="RF Wheel Parent", default=False)
    rf_rim_parent: bpy.props.BoolProperty(name="RF Rim Parent", default=False)
    rf_tyre_parent: bpy.props.BoolProperty(name="RF Tyre Parent", default=False)

#---------------------------------------------------------------------------------------------
#---------------------------------------- UI Panels ------------------------------------------
#---------------------------------------------------------------------------------------------

#create the Left Front Animation Panel. This houses all the animation components for the left front
class CreateEmpty_Panel(bpy.types.Panel):
    bl_label = "Create Empty"
    bl_idname = "CE_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SUSP ANIM"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        
        #Begin Box for Create Empty
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Create New Empty", icon='EMPTY_ARROWS')
        
        textWrap = "Use this to create a new Y up, Z forward empty object. This creates an empty that is configured to work with Assetto Corsa."
        twrap = textwrap.TextWrapper(width=45)
        wList = twrap.wrap(text=textWrap)
        for text in wList: 
            row = box.row(align = True)
            row.alignment = 'CENTER'
            row.scale_y = 0.5
            row.label(text=text)
            
        row = box.row()
        row.operator("my.create_empty")

#create the Left Front Animation Panel. This houses all the animation components for the left front
class LF_Panel(bpy.types.Panel):
    bl_label = "LF Animation Properties"
    bl_idname = "LF_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SUSP ANIM"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        
        textWrap = "Below are all of the Front Left properties. Fill out all properties as needed."
        twrap = textwrap.TextWrapper(width=45)
        wList = twrap.wrap(text=textWrap)
        for text in wList: 
            row = layout.row(align = True)
            row.alignment = 'CENTER'
            row.scale_y = 0.5
            row.label(text=text)
            
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.operator("lf_preanimation.show_status")
    
        #Begin Box for LF hub Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="hub Properties", icon='EVENT_H')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_hub_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_hub_dir", text="")
    
        row = box.row()
        row.scale_y = 1
        col1 = row.column(align=True)
        row.label(text="CHILDREN | STIFFNESS")
        col2 = row.column(align=True)
        col2.prop(settings, "lf_hub_stiffness", text="")
        col1.scale_x = 2.5
        col1.scale_y = 1.0
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_hub_meshes", "", settings, "lf_hub_mesh", settings, "active_lf_hub_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_hub_mesh")
        row.operator("mesh.remove_lf_hub_mesh")
    
        row = box.row()
        row.operator("lf_hub_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("lf_hub_button.config")
        row.alignment = 'CENTER'
        
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF LCA Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="LCA Properties", icon='EVENT_L')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_lca_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_lca_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_lca_meshes", "", settings, "lf_lca_mesh", settings, "active_lf_lca_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_lca_mesh")
        row.operator("mesh.remove_lf_lca_mesh")
    
        row = box.row()
        row.operator("lf_lca_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("lf_lca_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF TENSION Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="TENSION Properties", icon='EVENT_L')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_tension_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_tension_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_tension_meshes", "", settings, "lf_tension_mesh", settings, "active_lf_tension_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_tension_mesh")
        row.operator("mesh.remove_lf_tension_mesh")
    
        row = box.row()
        row.operator("lf_tension_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("lf_tension_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF Suspension Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Suspension Properties", icon='EVENT_S')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_susp_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_susp_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_susp_meshes", "", settings, "lf_susp_mesh", settings, "active_lf_susp_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_susp_mesh")
        row.operator("mesh.remove_lf_susp_mesh")
    
        row = box.row()
        row.operator("lf_susp_button.parent_fun")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
    
        #Begin Box for LF Coilover Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Coilover Properties", icon='EVENT_C')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_coil_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_coil_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_coil_meshes", "", settings, "lf_coil_mesh", settings, "active_lf_coil_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_coil_mesh")
        row.operator("mesh.remove_lf_coil_mesh")
    
        row = box.row()
        row.operator("lf_coil_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("lf_coil_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF spring Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="spring Properties", icon='MOD_SCREW')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_spring_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_spring_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_spring_meshes", "", settings, "lf_spring_mesh", settings, "active_lf_spring_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_spring_mesh")
        row.operator("mesh.remove_lf_spring_mesh")
    
        row = box.row()
        row.operator("lf_spring_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("lf_spring_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF steer Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="steer Properties", icon='CURVE_BEZCIRCLE')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_steer_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "lf_steer_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_steer_meshes", "", settings, "lf_steer_mesh", settings, "active_lf_steer_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_steer_mesh")
        row.operator("mesh.remove_lf_steer_mesh")
    
        row = box.row()
        row.operator("lf_steer_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("lf_steer_button.config")
        row.alignment = 'CENTER'
        
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF Wheel Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Wheel Properties", icon='EVENT_W')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_wheel_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_wheel_meshes", "", settings, "lf_wheel_mesh", settings, "active_lf_wheel_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_wheel_mesh")
        row.operator("mesh.remove_lf_wheel_mesh")
    
        row = box.row()
        row.operator("lf_wheel_button.parent_fun")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF rim Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Rim Properties", icon='EVENT_R')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_rim_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_rim_meshes", "", settings, "lf_rim_mesh", settings, "active_lf_rim_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_rim_mesh")
        row.operator("mesh.remove_lf_rim_mesh")
    
        row = box.row()
        row.operator("lf_rim_button.parent_fun")
        row.operator("lf_rim_button.zero_trans")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for LF tyre Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Tyre Properties", icon='EVENT_T')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "lf_tyre_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_lf_tyre_meshes", "", settings, "lf_tyre_mesh", settings, "active_lf_tyre_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_lf_tyre_mesh")
        row.operator("mesh.remove_lf_tyre_mesh")
    
        row = box.row()
        row.operator("lf_tyre_button.parent_fun")
        row.operator("lf_tyre_button.zero_trans")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()


#create the Right Front Animation Panel. This houses all the animation components for the right front
class RF_Panel(bpy.types.Panel):
    bl_label = "RF Animation Properties"
    bl_idname = "RF_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SUSP ANIM"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        
        textWrap = "Below are all of the Front Right properties. Fill out all properties as needed."
        twrap = textwrap.TextWrapper(width=45)
        wList = twrap.wrap(text=textWrap)
        for text in wList: 
            row = layout.row(align = True)
            row.alignment = 'CENTER'
            row.scale_y = 0.5
            row.label(text=text)
            
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.operator("rf_preanimation.show_status")
    
        #Begin Box for RF hub Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="hub Properties", icon='EVENT_H')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_hub_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_hub_dir", text="")
    
        row = box.row()
        row.scale_y = 1
        col1 = row.column(align=True)
        row.label(text="CHILDREN | STIFFNESS")
        col2 = row.column(align=True)
        col2.prop(settings, "rf_hub_stiffness", text="")
        col1.scale_x = 2.5
        col1.scale_y = 1.0
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_hub_meshes", "", settings, "rf_hub_mesh", settings, "active_rf_hub_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_hub_mesh")
        row.operator("mesh.remove_rf_hub_mesh")
    
        row = box.row()
        row.operator("rf_hub_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("rf_hub_button.config")
        row.alignment = 'CENTER'
        
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF LCA Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="LCA Properties", icon='EVENT_L')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_lca_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_lca_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_lca_meshes", "", settings, "rf_lca_mesh", settings, "active_rf_lca_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_lca_mesh")
        row.operator("mesh.remove_rf_lca_mesh")
    
        row = box.row()
        row.operator("rf_lca_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("rf_lca_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF TENSION Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="TENSION Properties", icon='EVENT_L')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_tension_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_tension_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_tension_meshes", "", settings, "rf_tension_mesh", settings, "active_rf_tension_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_tension_mesh")
        row.operator("mesh.remove_rf_tension_mesh")
    
        row = box.row()
        row.operator("rf_tension_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("rf_tension_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF Suspension Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Suspension Properties", icon='EVENT_S')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_susp_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_susp_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_susp_meshes", "", settings, "rf_susp_mesh", settings, "active_rf_susp_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_susp_mesh")
        row.operator("mesh.remove_rf_susp_mesh")
    
        row = box.row()
        row.operator("rf_susp_button.parent_fun")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
    
        #Begin Box for RF Coilover Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Coilover Properties", icon='EVENT_C')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_coil_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_coil_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_coil_meshes", "", settings, "rf_coil_mesh", settings, "active_rf_coil_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_coil_mesh")
        row.operator("mesh.remove_rf_coil_mesh")
    
        row = box.row()
        row.operator("rf_coil_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("rf_coil_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF spring Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="spring Properties", icon='MOD_SCREW')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_spring_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_spring_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_spring_meshes", "", settings, "rf_spring_mesh", settings, "active_rf_spring_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_spring_mesh")
        row.operator("mesh.remove_rf_spring_mesh")
    
        row = box.row()
        row.operator("rf_spring_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("rf_spring_button.config")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF steer Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="steer Properties", icon='CURVE_BEZCIRCLE')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_steer_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="SA_ Object")
        row = box.row()
        row.prop(settings, "rf_steer_dir", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_steer_meshes", "", settings, "rf_steer_mesh", settings, "active_rf_steer_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_steer_mesh")
        row.operator("mesh.remove_rf_steer_mesh")
    
        row = box.row()
        row.operator("rf_steer_button.parent_fun")
        row.alignment = 'CENTER'
        
        row = box.row()
        row.operator("rf_steer_button.config")
        row.alignment = 'CENTER'
        
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF Wheel Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Wheel Properties", icon='EVENT_W')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_wheel_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_wheel_meshes", "", settings, "rf_wheel_mesh", settings, "active_rf_wheel_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_wheel_mesh")
        row.operator("mesh.remove_rf_wheel_mesh")
    
        row = box.row()
        row.operator("rf_wheel_button.parent_fun")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF rim Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Rim Properties", icon='EVENT_R')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_rim_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_rim_meshes", "", settings, "rf_rim_mesh", settings, "active_rf_rim_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_rim_mesh")
        row.operator("mesh.remove_rf_rim_mesh")
    
        row = box.row()
        row.operator("rf_rim_button.parent_fun")
        row.operator("rf_rim_button.zero_trans")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()
        
        #Begin Box for RF tyre Properties
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Tyre Properties", icon='EVENT_T')
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="Empty Object")
        row = box.row()
        row.prop(settings, "rf_tyre_dummy", text="")
    
        row = box.row()
        row.scale_y = 0.5
        row.label(text="CHILDREN")
    
        row = box.row()
        row.scale_y = 0.75
        row.template_list("MESH_UL_rf_tyre_meshes", "", settings, "rf_tyre_mesh", settings, "active_rf_tyre_mesh_index")
    
        row = box.row()
        row.operator("mesh.add_rf_tyre_mesh")
        row.operator("mesh.remove_rf_tyre_mesh")
    
        row = box.row()
        row.operator("rf_tyre_button.parent_fun")
        row.operator("rf_tyre_button.zero_trans")
        row.alignment = 'CENTER'
    
        row = box.row(align=True)
        row.separator()

#---------------------------------------------------------------------------------------------
#---------------------------------- Operators and Classes ------------------------------------
#---------------------------------------------------------------------------------------------

#Create Empty Operator
class MY_OT_create_empty(bpy.types.Operator):
    bl_idname = "my.create_empty"
    bl_label = "Create Empty"

    def execute(self, context):
        bpy.ops.object.empty_add(type='ARROWS', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL')
        bpy.context.object.name = "NULL"
        bpy.context.object.empty_display_size = 0.1
        return {'FINISHED'}


# The Left Front preanimation status button. This is to show the current status of the 
# properties listed in the panel. They will either show True or False. These can be 
# overidden using the console.

class LF_PREANIMATION_Show_Status(bpy.types.Operator):
    bl_idname = "lf_preanimation.show_status"
    bl_label = "Check Status"

    def execute(self, context):
        settings = context.scene.settings
        
        msg="Left Front Pre-Animation Check status:\n\nLF_HUB_PARENT = " + str(settings.lf_hub_parent)+"\nLF_HUB_CONFIGURED = " + str(settings.lf_hub_configured)+"\nLF_LCA_PARENT = " + str(settings.lf_lca_parent)+"\nLF_LCA_CONFIGURED = " + str(settings.lf_lca_configured)+"\nLF_TENSION_PARENT = " + str(settings.lf_tension_parent)+"\nLF_TENSION_CONFIGURED = " + str(settings.lf_tension_configured)+"\nLF_SUSP_PARENT = " + str(settings.lf_susp_parent)+"\nLF_COILOVER_PARENT = " + str(settings.lf_coilover_parent)+"\nLF_COILOVER_CONFIGURED = " + str(settings.lf_coilover_configured)+"\nLF_SPRING_PARENT = " + str(settings.lf_spring_parent)+"\nLF_SPRING_CONFIGURED = " + str(settings.lf_spring_configured)+"\nLF_STEER_PARENT = " + str(settings.lf_steer_parent)+"\nLF_STEER_CONFIGURED = " + str(settings.lf_steer_configured)+"\nLF_WHEEL_PARENT = " + str(settings.lf_wheel_parent)+"\nLF_RIM_PARENT = " + str(settings.lf_rim_parent)+"\nLF_TYRE_PARENT = " + str(settings.lf_tyre_parent)
        
        self.report({'INFO'}, msg)

        # show message popup
        def draw_popup(self, context):
            self.layout.label(text="Status Results:")
            self.layout.label(text="")
            self.layout.label(text="LF_HUB_PARENT = " + str(settings.lf_hub_parent))
            self.layout.label(text="LF_HUB_CONFIGURED = " + str(settings.lf_hub_configured))
            self.layout.label(text="LF_LCA_PARENT = " + str(settings.lf_lca_parent))
            self.layout.label(text="LF_LCA_CONFIGURED = " + str(settings.lf_lca_configured))
            self.layout.label(text="LF_TENSION_PARENT = " + str(settings.lf_tension_parent))
            self.layout.label(text="LF_TENSION_CONFIGURED = " + str(settings.lf_tension_configured))
            self.layout.label(text="LF_SUSP_PARENT = " + str(settings.lf_susp_parent))
            self.layout.label(text="LF_COILOVER_PARENT = " + str(settings.lf_coilover_parent))
            self.layout.label(text="LF_COILOVER_CONFIGURED = " + str(settings.lf_coilover_configured))
            self.layout.label(text="LF_SPRING_PARENT = " + str(settings.lf_spring_parent))
            self.layout.label(text="LF_SPRING_CONFIGURED = " + str(settings.lf_spring_configured))
            self.layout.label(text="LF_STEER_PARENT = " + str(settings.lf_steer_parent))
            self.layout.label(text="LF_STEER_CONFIGURED = " + str(settings.lf_steer_configured))
            self.layout.label(text="LF_WHEEL_PARENT = " + str(settings.lf_wheel_parent))
            self.layout.label(text="LF_RIM_PARENT = " + str(settings.lf_rim_parent))
            self.layout.label(text="LF_TYRE_PARENT = " + str(settings.lf_tyre_parent))
            self.layout.label(text="")
            self.layout.label(text="These results may not be accurate ")
            self.layout.label(text="if modified outside of the script.")
        bpy.context.window_manager.popup_menu(draw_popup, title="Left Front Pre-Animation Check Status")

        return {'FINISHED'}
    
#---------------------- BEGIN LF HUB ---------------------------------------------

#Create Collection for LF hub
class MESH_UL_lf_hub_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF hub Collection
class MESH_OT_add_lf_hub_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_hub_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_hub_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF hub Collection
class MESH_OT_remove_lf_hub_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_hub_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_hub_mesh_index
        settings.lf_hub_mesh.remove(index)
        settings.active_lf_hub_mesh_index = min(max(0, index - 1), len(settings.lf_hub_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on hub prop
class LF_hub_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_hub_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_hub_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_hub_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_hub_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_hub_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_hub_parent = parent_without_transform(m_obj, settings.lf_hub_dummy, unparent=False)
        return {'FINISHED'}

#Operator for hub configuration button
class LF_hub_button_config(bpy.types.Operator):
    bl_idname = "lf_hub_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.lf_hub_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.lf_hub_dummy
        p_obj = settings.lf_hub_dir
        stiff = settings.lf_hub_stiffness
        
        res = damped_track_constraint(obj, p_obj, stiff,'TRACK_NEGATIVE_X')
        settings.lf_hub_configured = limit_distance_constraint(obj, p_obj, 1.0)
        
        return {'FINISHED'}

#---------------------- END LF HUB ---------------------------------------------

#---------------------- BEGIN LF LCA ---------------------------------------------

#Create Collection for LF LCA
class MESH_UL_lf_lca_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF LCA Collection
class MESH_OT_add_lf_lca_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_lca_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_lca_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF LCA Collection
class MESH_OT_remove_lf_lca_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_lca_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_lca_mesh_index
        settings.lf_lca_mesh.remove(index)
        settings.active_lf_lca_mesh_index = min(max(0, index - 1), len(settings.lf_lca_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on LCA prop
class LF_LCA_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_lca_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_lca_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_lca_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_lca_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_lca_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_lca_parent = parent_without_transform(m_obj, settings.lf_lca_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the lca configuration button
class LF_lca_button_config(bpy.types.Operator):
    bl_idname = "lf_lca_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.lf_lca_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.lf_lca_dummy
        p_obj = settings.lf_lca_dir
        
        settings.lf_lca_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_NEGATIVE_X')
        
        return {'FINISHED'}

#---------------------- END LF LCA ---------------------------------------------

#---------------------- BEGIN LF TENSION ---------------------------------------------

#Create Collection for LF TENSION
class MESH_UL_lf_tension_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF TENSION Collection
class MESH_OT_add_lf_tension_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_tension_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_tension_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF TENSION Collection
class MESH_OT_remove_lf_tension_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_tension_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_tension_mesh_index
        settings.lf_tension_mesh.remove(index)
        settings.active_lf_tension_mesh_index = min(max(0, index - 1), len(settings.lf_tension_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on TENSION prop
class LF_TENSION_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_tension_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_tension_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_tension_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_tension_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_tension_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_tension_parent = parent_without_transform(m_obj, settings.lf_tension_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the tension configuration button
class LF_tension_button_config(bpy.types.Operator):
    bl_idname = "lf_tension_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.lf_tension_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.lf_tension_dummy
        p_obj = settings.lf_tension_dir
        
        settings.lf_tension_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_NEGATIVE_X')
        
        return {'FINISHED'}

#---------------------- END LF TENSION ---------------------------------------------

#---------------------- BEGIN LF SUSPENSION ---------------------------------------------

#Create Collection for LF Suspension
class MESH_UL_lf_susp_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))

#Operator add mesh to LF Susp Collection
class MESH_OT_add_lf_susp_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_susp_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_susp_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF Susp Collection
class MESH_OT_remove_lf_susp_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_susp_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_susp_mesh_index
        settings.lf_susp_mesh.remove(index)
        settings.active_lf_susp_mesh_index = min(max(0, index - 1), len(settings.lf_susp_mesh) - 1)
        return {'FINISHED'}

#Operator for parent button on suspension prop
class LF_SUSP_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_susp_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_susp_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_susp_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_susp_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_susp_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_susp_parent = parent_without_transform(m_obj, settings.lf_susp_dummy, unparent=False)
        return {'FINISHED'}


#---------------------- END LF SUSPENSION ---------------------------------------------

#---------------------- BEGIN LF COILOVER ---------------------------------------------

#Create Collection for LF Coilover
class MESH_UL_lf_coil_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))

#Operator add mesh to LF Coilover Collection
class MESH_OT_add_lf_coil_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_coil_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_coil_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF Coilover Collection
class MESH_OT_remove_lf_coil_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_coil_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_coil_mesh_index
        settings.lf_coil_mesh.remove(index)
        settings.active_lf_coil_mesh_index = min(max(0, index - 1), len(settings.lf_coil_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on coilover prop
class LF_COIL_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_coil_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_coil_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_coil_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_coil_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_coilover_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_coilover_parent = parent_without_transform(m_obj, settings.lf_coil_dummy, unparent=False)
        return {'FINISHED'}

#Operator for the lf coil configuration button
class LF_coil_button_config(bpy.types.Operator):
    bl_idname = "lf_coil_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.lf_coil_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.lf_coil_dummy
        p_obj = settings.lf_coil_dir
        
        lf_coilover_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_Y')
        
        return {'FINISHED'}

#---------------------- END LF COILOVER ---------------------------------------------

#---------------------- BEGIN LF SPRING ---------------------------------------------

#Create Collection for LF spring
class MESH_UL_lf_spring_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF spring Collection
class MESH_OT_add_lf_spring_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_spring_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_spring_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF spring Collection
class MESH_OT_remove_lf_spring_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_spring_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_spring_mesh_index
        settings.lf_spring_mesh.remove(index)
        settings.active_lf_spring_mesh_index = min(max(0, index - 1), len(settings.lf_spring_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on spring prop
class LF_spring_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_spring_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_spring_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_spring_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_spring_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_spring_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_spring_parent = parent_without_transform(m_obj, settings.lf_spring_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the lf spring configuration button
class LF_spring_button_config(bpy.types.Operator):
    bl_idname = "lf_spring_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.lf_spring_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.lf_spring_dummy
        p_obj = settings.lf_spring_dir
        
        settings.lf_spring_configured = stretch_to_constraint(obj, p_obj, 1.0)
        
        return {'FINISHED'}

#---------------------- END LF SPRING ---------------------------------------------

#---------------------- BEGIN LF STEER ---------------------------------------------

#Create Collection for LF steer
class MESH_UL_lf_steer_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF steer Collection
class MESH_OT_add_lf_steer_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_steer_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_steer_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF steer Collection
class MESH_OT_remove_lf_steer_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_steer_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_steer_mesh_index
        settings.lf_steer_mesh.remove(index)
        settings.active_lf_steer_mesh_index = min(max(0, index - 1), len(settings.lf_steer_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on steer prop
class LF_steer_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_steer_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_steer_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_steer_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_steer_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_steer_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_steer_parent = parent_without_transform(m_obj, settings.lf_steer_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the steer configuration button
class LF_steer_button_config(bpy.types.Operator):
    bl_idname = "lf_steer_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.lf_steer_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.lf_steer_dummy
        p_obj = settings.lf_steer_dir
        
        settings.lf_steer_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_NEGATIVE_X')
        
        return {'FINISHED'}

#---------------------- END LF STEER ---------------------------------------------

#---------------------- BEGIN LF WHEEL ---------------------------------------------

#Create Collection for LF wheel
class MESH_UL_lf_wheel_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF Susp Collection
class MESH_OT_add_lf_wheel_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_wheel_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_wheel_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF wheel Collection
class MESH_OT_remove_lf_wheel_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_wheel_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_wheel_mesh_index
        settings.lf_wheel_mesh.remove(index)
        settings.active_lf_wheel_mesh_index = min(max(0, index - 1), len(settings.lf_wheel_mesh) - 1)
        return {'FINISHED'}
    
#Operator for parent button on wheel prop
class LF_WHEEL_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_wheel_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_wheel_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_susp_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_wheel_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_wheel_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_wheel_parent = parent_without_transform(m_obj, settings.lf_wheel_dummy, unparent=False)
        return {'FINISHED'}

#---------------------- END LF WHEEL ---------------------------------------------

#---------------------- BEGIN LF RIM ---------------------------------------------

#Create Collection for LF RIM
class MESH_UL_lf_rim_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF Rim Collection
class MESH_OT_add_lf_rim_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_rim_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_rim_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF rim Collection
class MESH_OT_remove_lf_rim_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_rim_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_rim_mesh_index
        settings.lf_rim_mesh.remove(index)
        settings.active_lf_rim_mesh_index = min(max(0, index - 1), len(settings.lf_rim_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on rim prop
class LF_rim_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_rim_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_rim_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_rim_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_rim_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_rim_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_rim_parent = parent_without_transform(m_obj, settings.lf_rim_dummy, unparent=False)
        return {'FINISHED'}
    
#Operator to zero out tyre group
class LF_rim_BUTTON_zero_trans(bpy.types.Operator):
    bl_idname = "lf_rim_button.zero_trans"
    bl_label = "Zero Transform"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_rim_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_rim_mesh:
            bpy.data.objects[obj.name].rotation_euler=(0,0,0)
            bpy.data.objects[obj.name].location=(0,0,0)
            
        return {'FINISHED'}

#---------------------- END LF RIM ---------------------------------------------

#---------------------- BEGIN LF TYRE ---------------------------------------------

#Create Collection for LF tyre
class MESH_UL_lf_tyre_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to LF tyre Collection
class MESH_OT_add_lf_tyre_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_lf_tyre_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.lf_tyre_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to LF tyre Collection
class MESH_OT_remove_lf_tyre_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_lf_tyre_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_lf_tyre_mesh_index
        settings.lf_tyre_mesh.remove(index)
        settings.active_lf_tyre_mesh_index = min(max(0, index - 1), len(settings.lf_tyre_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on tyre prop
class LF_tyre_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "lf_tyre_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_tyre_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_tyre_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.lf_tyre_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.lf_tyre_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.lf_tyre_parent = parent_without_transform(m_obj, settings.lf_tyre_dummy, unparent=False)
        return {'FINISHED'}
    
#Operator to zero out tyre group
class LF_tyre_BUTTON_zero_trans(bpy.types.Operator):
    bl_idname = "lf_tyre_button.zero_trans"
    bl_label = "Zero Transform"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.lf_tyre_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.lf_tyre_mesh:
            bpy.data.objects[obj.name].rotation_euler=(0,0,0)
            bpy.data.objects[obj.name].location=(0,0,0)
            
        return {'FINISHED'}

#---------------------- END LF TYRE ---------------------------------------------

# The Right Front preanimation status button. This is to show the current status of the 
# properties listed in the panel. They will either show True or False. These can be 
# overidden using the console.

class RF_PREANIMATION_Show_Status(bpy.types.Operator):
    bl_idname = "rf_preanimation.show_status"
    bl_label = "Check Status"

    def execute(self, context):
        settings = context.scene.settings
        
        msg="Right Front Pre-Animation Check status:\n\nRF_HUB_PARENT = " + str(settings.rf_hub_parent)+"\nRF_HUB_CONFIGURED = " + str(settings.rf_hub_configured)+"\nRF_LCA_PARENT = " + str(settings.rf_lca_parent)+"\nRF_LCA_CONFIGURED = " + str(settings.rf_lca_configured)+"\nRF_TENSION_PARENT = " + str(settings.rf_tension_parent)+"\nRF_TENSION_CONFIGURED = " + str(settings.rf_tension_configured)+"\nRF_SUSP_PARENT = " + str(settings.rf_susp_parent)+"\nRF_COILOVER_PARENT = " + str(settings.rf_coilover_parent)+"\nRF_COILOVER_CONFIGURED = " + str(settings.rf_coilover_configured)+"\nRF_SPRING_PARENT = " + str(settings.rf_spring_parent)+"\nRF_SPRING_CONFIGURED = " + str(settings.rf_spring_configured)+"\nRF_STEER_PARENT = " + str(settings.rf_steer_parent)+"\nRF_STEER_CONFIGURED = " + str(settings.rf_steer_configured)+"\nRF_WHEEL_PARENT = " + str(settings.rf_wheel_parent)+"\nRF_RIM_PARENT = " + str(settings.rf_rim_parent)+"\nRF_TYRE_PARENT = " + str(settings.rf_tyre_parent)
        
        self.report({'INFO'}, msg)

        # show message popup
        def draw_popup(self, context):
            self.layout.label(text="Status Results:")
            self.layout.label(text="")
            self.layout.label(text="RF_HUB_PARENT = " + str(settings.rf_hub_parent))
            self.layout.label(text="RF_HUB_CONFIGURED = " + str(settings.rf_hub_configured))
            self.layout.label(text="RF_LCA_PARENT = " + str(settings.rf_lca_parent))
            self.layout.label(text="RF_LCA_CONFIGURED = " + str(settings.rf_lca_configured))
            self.layout.label(text="RF_TENSION_PARENT = " + str(settings.rf_tension_parent))
            self.layout.label(text="RF_TENSION_CONFIGURED = " + str(settings.rf_tension_configured))
            self.layout.label(text="RF_SUSP_PARENT = " + str(settings.rf_susp_parent))
            self.layout.label(text="RF_COILOVER_PARENT = " + str(settings.rf_coilover_parent))
            self.layout.label(text="RF_COILOVER_CONFIGURED = " + str(settings.rf_coilover_configured))
            self.layout.label(text="RF_SPRING_PARENT = " + str(settings.rf_spring_parent))
            self.layout.label(text="RF_SPRING_CONFIGURED = " + str(settings.rf_spring_configured))
            self.layout.label(text="RF_STEER_PARENT = " + str(settings.rf_steer_parent))
            self.layout.label(text="RF_STEER_CONFIGURED = " + str(settings.rf_steer_configured))
            self.layout.label(text="RF_WHEEL_PARENT = " + str(settings.rf_wheel_parent))
            self.layout.label(text="RF_RIM_PARENT = " + str(settings.rf_rim_parent))
            self.layout.label(text="RF_TYRE_PARENT = " + str(settings.rf_tyre_parent))
            self.layout.label(text="")
            self.layout.label(text="These results may not be accurate ")
            self.layout.label(text="if modified outside of the script.")
        bpy.context.window_manager.popup_menu(draw_popup, title="Right Front Pre-Animation Check Status")

        return {'FINISHED'}
    
#---------------------- BEGIN RF HUB ---------------------------------------------

#Create Collection for RF hub
class MESH_UL_rf_hub_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF hub Collection
class MESH_OT_add_rf_hub_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_hub_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_hub_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF hub Collection
class MESH_OT_remove_rf_hub_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_hub_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_hub_mesh_index
        settings.rf_hub_mesh.remove(index)
        settings.active_rf_hub_mesh_index = min(max(0, index - 1), len(settings.rf_hub_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on hub prop
class RF_hub_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_hub_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_hub_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_hub_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_hub_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_hub_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_hub_parent = parent_without_transform(m_obj, settings.rf_hub_dummy, unparent=False)
        return {'FINISHED'}

#Operator for hub configuration button
class RF_hub_button_config(bpy.types.Operator):
    bl_idname = "rf_hub_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.rf_hub_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.rf_hub_dummy
        p_obj = settings.rf_hub_dir
        stiff = settings.rf_hub_stiffness
        
        res = damped_track_constraint(obj, p_obj, stiff,'TRACK_X')
        settings.rf_hub_configured = limit_distance_constraint(obj, p_obj, 1.0)
        
        return {'FINISHED'}

#---------------------- END RF HUB ---------------------------------------------

#---------------------- BEGIN RF LCA ---------------------------------------------

#Create Collection for RF LCA
class MESH_UL_rf_lca_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF LCA Collection
class MESH_OT_add_rf_lca_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_lca_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_lca_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF LCA Collection
class MESH_OT_remove_rf_lca_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_lca_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_lca_mesh_index
        settings.rf_lca_mesh.remove(index)
        settings.active_rf_lca_mesh_index = min(max(0, index - 1), len(settings.rf_lca_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on LCA prop
class RF_LCA_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_lca_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_lca_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_lca_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_lca_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_lca_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_lca_parent = parent_without_transform(m_obj, settings.rf_lca_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the lca configuration button
class RF_lca_button_config(bpy.types.Operator):
    bl_idname = "rf_lca_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.rf_lca_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.rf_lca_dummy
        p_obj = settings.rf_lca_dir
        
        settings.rf_lca_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_X')
        
        return {'FINISHED'}

#---------------------- END RF LCA ---------------------------------------------

#---------------------- BEGIN RF TENSION ---------------------------------------------

#Create Collection for RF TENSION
class MESH_UL_rf_tension_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF TENSION Collection
class MESH_OT_add_rf_tension_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_tension_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_tension_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF TENSION Collection
class MESH_OT_remove_rf_tension_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_tension_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_tension_mesh_index
        settings.rf_tension_mesh.remove(index)
        settings.active_rf_tension_mesh_index = min(max(0, index - 1), len(settings.rf_tension_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on TENSION prop
class RF_TENSION_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_tension_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_tension_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_tension_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_tension_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_tension_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_tension_parent = parent_without_transform(m_obj, settings.rf_tension_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the tension configuration button
class RF_tension_button_config(bpy.types.Operator):
    bl_idname = "rf_tension_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.rf_tension_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.rf_tension_dummy
        p_obj = settings.rf_tension_dir
        
        settings.rf_tension_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_X')
        
        return {'FINISHED'}

#---------------------- END RF TENSION ---------------------------------------------

#---------------------- BEGIN RF SUSPENSION ---------------------------------------------

#Create Collection for RF Suspension
class MESH_UL_rf_susp_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))

#Operator add mesh to RF Susp Collection
class MESH_OT_add_rf_susp_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_susp_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_susp_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF Susp Collection
class MESH_OT_remove_rf_susp_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_susp_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_susp_mesh_index
        settings.rf_susp_mesh.remove(index)
        settings.active_rf_susp_mesh_index = min(max(0, index - 1), len(settings.rf_susp_mesh) - 1)
        return {'FINISHED'}

#Operator for parent button on suspension prop
class RF_SUSP_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_susp_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_susp_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_susp_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_susp_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_susp_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_susp_parent = parent_without_transform(m_obj, settings.rf_susp_dummy, unparent=False)
        return {'FINISHED'}


#---------------------- END RF SUSPENSION ---------------------------------------------

#---------------------- BEGIN RF COILOVER ---------------------------------------------

#Create Collection for RF Coilover
class MESH_UL_rf_coil_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))

#Operator add mesh to RF Coilover Collection
class MESH_OT_add_rf_coil_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_coil_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_coil_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF Coilover Collection
class MESH_OT_remove_rf_coil_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_coil_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_coil_mesh_index
        settings.rf_coil_mesh.remove(index)
        settings.active_rf_coil_mesh_index = min(max(0, index - 1), len(settings.rf_coil_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on coilover prop
class RF_COIL_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_coil_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_coil_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_coil_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_coil_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_coilover_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_coilover_parent = parent_without_transform(m_obj, settings.rf_coil_dummy, unparent=False)
        return {'FINISHED'}

#Operator for the rf coil configuration button
class RF_coil_button_config(bpy.types.Operator):
    bl_idname = "rf_coil_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.rf_coil_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.rf_coil_dummy
        p_obj = settings.rf_coil_dir
        
        rf_coilover_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_Y')
        
        return {'FINISHED'}

#---------------------- END RF COILOVER ---------------------------------------------

#---------------------- BEGIN RF SPRING ---------------------------------------------

#Create Collection for RF spring
class MESH_UL_rf_spring_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF spring Collection
class MESH_OT_add_rf_spring_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_spring_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_spring_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF spring Collection
class MESH_OT_remove_rf_spring_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_spring_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_spring_mesh_index
        settings.rf_spring_mesh.remove(index)
        settings.active_rf_spring_mesh_index = min(max(0, index - 1), len(settings.rf_spring_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on spring prop
class RF_spring_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_spring_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_spring_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_spring_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_spring_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_spring_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_spring_parent = parent_without_transform(m_obj, settings.rf_spring_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the rf spring configuration button
class RF_spring_button_config(bpy.types.Operator):
    bl_idname = "rf_spring_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.rf_spring_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.rf_spring_dummy
        p_obj = settings.rf_spring_dir
        
        settings.rf_spring_configured = stretch_to_constraint(obj, p_obj, 1.0)
        
        return {'FINISHED'}

#---------------------- END RF SPRING ---------------------------------------------

#---------------------- BEGIN RF STEER ---------------------------------------------

#Create Collection for RF steer
class MESH_UL_rf_steer_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF steer Collection
class MESH_OT_add_rf_steer_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_steer_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_steer_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF steer Collection
class MESH_OT_remove_rf_steer_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_steer_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_steer_mesh_index
        settings.rf_steer_mesh.remove(index)
        settings.active_rf_steer_mesh_index = min(max(0, index - 1), len(settings.rf_steer_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on steer prop
class RF_steer_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_steer_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_steer_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_steer_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_steer_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_steer_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_steer_parent = parent_without_transform(m_obj, settings.rf_steer_dummy, unparent=False)
        return {'FINISHED'}
        
#Operator for the steer configuration button
class RF_steer_button_config(bpy.types.Operator):
    bl_idname = "rf_steer_button.config"
    bl_label = "Configure / Unconfigure"

    def execute(self, context):
        settings = context.scene.settings
        if settings.rf_steer_dummy == None:
            self.report({'WARNING'}, "No object to configure.")
            return {'CANCELLED'}
        
        obj = settings.rf_steer_dummy
        p_obj = settings.rf_steer_dir
        
        settings.rf_steer_configured = damped_track_constraint(obj, p_obj, 1.0, 'TRACK_X')
        
        return {'FINISHED'}

#---------------------- END RF STEER ---------------------------------------------

#---------------------- BEGIN RF WHEEL ---------------------------------------------

#Create Collection for RF wheel
class MESH_UL_rf_wheel_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF Susp Collection
class MESH_OT_add_rf_wheel_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_wheel_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_wheel_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF wheel Collection
class MESH_OT_remove_rf_wheel_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_wheel_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_wheel_mesh_index
        settings.rf_wheel_mesh.remove(index)
        settings.active_rf_wheel_mesh_index = min(max(0, index - 1), len(settings.rf_wheel_mesh) - 1)
        return {'FINISHED'}
    
#Operator for parent button on wheel prop
class RF_WHEEL_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_wheel_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_wheel_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_susp_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_wheel_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_wheel_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_wheel_parent = parent_without_transform(m_obj, settings.rf_wheel_dummy, unparent=False)
        return {'FINISHED'}

#---------------------- END RF WHEEL ---------------------------------------------

#---------------------- BEGIN RF RIM ---------------------------------------------

#Create Collection for RF RIM
class MESH_UL_rf_rim_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF Rim Collection
class MESH_OT_add_rf_rim_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_rim_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_rim_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF rim Collection
class MESH_OT_remove_rf_rim_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_rim_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_rim_mesh_index
        settings.rf_rim_mesh.remove(index)
        settings.active_rf_rim_mesh_index = min(max(0, index - 1), len(settings.rf_rim_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on rim prop
class RF_rim_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_rim_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_rim_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_rim_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_rim_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_rim_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_rim_parent = parent_without_transform(m_obj, settings.rf_rim_dummy, unparent=False)
        return {'FINISHED'}
    
#Operator to zero out tyre group
class RF_rim_BUTTON_zero_trans(bpy.types.Operator):
    bl_idname = "rf_rim_button.zero_trans"
    bl_label = "Zero Transform"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_rim_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_rim_mesh:
            bpy.data.objects[obj.name].rotation_euler=(0,0,0)
            bpy.data.objects[obj.name].location=(0,0,0)
            
        return {'FINISHED'}

#---------------------- END RF RIM ---------------------------------------------

#---------------------- BEGIN RF TYRE ---------------------------------------------

#Create Collection for RF tyre
class MESH_UL_rf_tyre_meshes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=layout.icon(item))
        
#Operator add mesh to RF tyre Collection
class MESH_OT_add_rf_tyre_mesh(bpy.types.Operator):
    bl_idname = "mesh.add_rf_tyre_mesh"
    bl_label = "Add Mesh"

    def execute(self, context):
        settings = context.scene.settings
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            item = settings.rf_tyre_mesh.add()
            item.name = obj.name
        
        return {'FINISHED'}

#Operator remove mesh to RF tyre Collection
class MESH_OT_remove_rf_tyre_mesh(bpy.types.Operator):
    bl_idname = "mesh.remove_rf_tyre_mesh"
    bl_label = "Remove Mesh"

    def execute(self, context):
        settings = context.scene.settings
        index = settings.active_rf_tyre_mesh_index
        settings.rf_tyre_mesh.remove(index)
        settings.active_rf_tyre_mesh_index = min(max(0, index - 1), len(settings.rf_tyre_mesh) - 1)
        return {'FINISHED'}
        
#Operator for parent button on tyre prop
class RF_tyre_BUTTON_parent_fun(bpy.types.Operator):
    bl_idname = "rf_tyre_button.parent_fun"
    bl_label = "Parent / Unparent"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_tyre_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_tyre_mesh:
            m_obj = bpy.data.objects[obj.name]
            p_obj = settings.rf_tyre_dummy.name
            if m_obj.parent != None and m_obj.parent.name == p_obj:
                settings.rf_tyre_parent = parent_without_transform(m_obj, p_obj, unparent=True)
            else:
                settings.rf_tyre_parent = parent_without_transform(m_obj, settings.rf_tyre_dummy, unparent=False)
        return {'FINISHED'}
    
#Operator to zero out tyre group
class RF_tyre_BUTTON_zero_trans(bpy.types.Operator):
    bl_idname = "rf_tyre_button.zero_trans"
    bl_label = "Zero Transform"

    def execute(self, context):
        settings = context.scene.settings
        if not settings.rf_tyre_mesh:
            self.report({'WARNING'}, "No objects in collection")
            return {'CANCELLED'}
        
        for obj in settings.rf_tyre_mesh:
            bpy.data.objects[obj.name].rotation_euler=(0,0,0)
            bpy.data.objects[obj.name].location=(0,0,0)
            
        return {'FINISHED'}

#---------------------- END RF TYRE ---------------------------------------------
    
#---------------------------------------------------------------------------------------------
#----------------------------------- Reusable Functions --------------------------------------
#---------------------------------------------------------------------------------------------

#Parent function to retain transforms. This can either add or remove a parent.
def parent_with_transform(mesh_object, parent_object, unparent=False):
    settings = bpy.context.scene.settings
    
    # Store the original transforms of the mesh object
    orig_location = mesh_object.location.copy()
    orig_rotation = mesh_object.rotation_euler.copy()
    orig_scale = mesh_object.scale.copy()
    
    #get the parent object
    target_obj = bpy.data.objects[parent_object] if isinstance(parent_object, str) else parent_object
    
    p_result = False

    if not unparent:
        # Parent the mesh object to the parent object
        mesh_object.parent = target_obj

        # Restore the original transforms of the mesh object
        mesh_object.matrix_parent_inverse = parent_object.matrix_world.inverted()
        mesh_object.location = orig_location
        mesh_object.rotation_euler = orig_rotation
        mesh_object.scale = orig_scale
        
        p_result = True

        
    else:
        # Unparent the mesh object from the parent object while retaining the transform
        mesh_object.parent = None
        mesh_object.location = orig_location
        mesh_object.rotation_euler = orig_rotation
        mesh_object.scale = orig_scale
        
        p_result = False
        
    return p_result

#
def parent_without_transform(mesh_object, parent_object, unparent=False):
    settings = bpy.context.scene.settings
    
    #get the parent object
    target_obj = bpy.data.objects[parent_object] if isinstance(parent_object, str) else parent_object
    
    p_result = False

    if not unparent:
        # Store the original transforms of the mesh object
        orig_location = mesh_object.matrix_world.translation.copy()
        orig_rotation = mesh_object.matrix_world.to_quaternion().copy()
        orig_scale = mesh_object.matrix_world.to_scale().copy()
        
        # Parent the mesh object to the parent object
        mesh_object.parent = target_obj

        # Apply the original transforms of the mesh object
        mesh_object.matrix_world = mathutils.Matrix.Translation(orig_location) @ orig_rotation.to_matrix().to_4x4() @ mathutils.Matrix.Scale(orig_scale[0], 4, (1.0,0.0,0.0)) @ mathutils.Matrix.Scale(orig_scale[1], 4, (0.0,1.0,0.0)) @ mathutils.Matrix.Scale(orig_scale[2], 4, (0.0,0.0,1.0))
        
        p_result = True

    else:
        # Store the original transforms of the mesh object
        orig_location = mesh_object.matrix_world.translation.copy()
        orig_rotation = mesh_object.matrix_world.to_quaternion().copy()
        orig_scale = mesh_object.matrix_world.to_scale().copy()

        # Unparent the mesh object from the parent object
        mesh_object.parent = None

        # Apply the original transforms of the mesh object in world space
        mesh_object.matrix_world = mathutils.Matrix.Translation(orig_location) @ orig_rotation.to_matrix().to_4x4() @ mathutils.Matrix.Scale(orig_scale[0], 4, (1.0,0.0,0.0)) @ mathutils.Matrix.Scale(orig_scale[1], 4, (0.0,1.0,0.0)) @ mathutils.Matrix.Scale(orig_scale[2], 4, (0.0,0.0,1.0))
        
        p_result = False
        
    return p_result

#
def parent_without_transform_zero(mesh_object, parent_object, unparent=False):
    settings = bpy.context.scene.settings

    #get the parent object
    target_obj = bpy.data.objects[parent_object] if isinstance(parent_object, str) else parent_object
    
    p_result = False

    if not unparent:
        # Parent the mesh object to the parent object
        mesh_object.parent = target_obj

        # Clear the object's location, rotation, and scale
        mesh_object.location = (0, 0, 0)
        mesh_object.rotation_euler = (0, 0, 0)
        
        p_result = True

    else:
        # Unparent the mesh object from the parent object
        mesh_object.parent = None
        
        p_result = False
        
    return p_result


# Damped Track to Constraint function. 
def damped_track_constraint(object, sa_object, inf, track="TRACK_NEGATIVE_X"):
    settings = bpy.context.scene.settings
    
    obj = bpy.data.objects[object.name]
    t_obj = bpy.data.objects[sa_object.name]
    
    dt_result = False
    
    if len(obj.constraints) > 0:
        # Loop over all constraints on obj1
        for constraint in obj.constraints:
            # Check if the constraint is a damped track constraint
            if constraint.type == 'DAMPED_TRACK':
                # Check if the target of the constraint matches obj2
                if constraint.target == t_obj:
                    # Remove the constraint
                    obj.constraints.remove(constraint)
                    dt_result = False
                    break
            else:
                track_constraint = obj.constraints.new('DAMPED_TRACK')
                track_constraint.target = t_obj
                track_constraint.track_axis = track
                track_constraint.influence = inf
                dt_result = True
    
    else:
        track_constraint = obj.constraints.new('DAMPED_TRACK')
        track_constraint.target = t_obj
        track_constraint.track_axis = track
        track_constraint.influence = inf
        
        dt_result = True
    
    return dt_result
    
# Limit Distance function. 
def limit_distance_constraint(object, sa_object, inf):
    settings = bpy.context.scene.settings
    
    obj = bpy.data.objects[object.name]
    t_obj = bpy.data.objects[sa_object.name]
    
    ld_result = False
    
    if len(obj.constraints) > 0:
        # Loop over all constraints on obj1
        for constraint in obj.constraints:
            # Check if the constraint is a limit distance constraint
            if constraint.type == 'LIMIT_DISTANCE':
                # Check if the target of the constraint matches obj2
                if constraint.target == t_obj:
                    # Remove the constraint
                    obj.constraints.remove(constraint)
                    ld_result = False
                    break
            else:
                distance_constraint = obj.constraints.new('LIMIT_DISTANCE')
                distance_constraint.target = t_obj
                distance_constraint.influence = inf
                ld_result = True
    
    else:
        distance_constraint = obj.constraints.new('LIMIT_DISTANCE')
        distance_constraint.target = t_obj
        distance_constraint.influence = inf
        
        ld_result = True
    
    return ld_result

#Stretch to constraint
def stretch_to_constraint(object, target_object, inf):
    obj = bpy.data.objects[object.name]
    target_obj = bpy.data.objects[target_object.name]
    
    stretch_result = False
    
    if len(obj.constraints) > 0:
        # Loop over all constraints on obj
        for constraint in obj.constraints:
            # Check if the constraint is a stretch-to constraint
            if constraint.type == 'STRETCH_TO':
                # Check if the target of the constraint matches target_object
                if constraint.target == target_obj:
                    # Remove the constraint
                    obj.constraints.remove(constraint)
                    stretch_result = False
                    break
            else:
                stretch_constraint = obj.constraints.new('STRETCH_TO')
                stretch_constraint.target = target_obj
                stretch_constraint.volume = 'NO_VOLUME'
                stretch_constraint.influence = inf
                stretch_constraint.keep_axis = 'PLANE_X'
                
                stretch_result = True
    
    else:
        stretch_constraint = obj.constraints.new('STRETCH_TO')
        stretch_constraint.target = target_obj
        stretch_constraint.volume = 'NO_VOLUME'
        stretch_constraint.influence = inf
        stretch_constraint.keep_axis = 'PLANE_X'
        
        stretch_result = True
    
    return stretch_result

#---------------------------------------------------------------------------------------------
#------------------------------- Registration and Insurance ----------------------------------
#---------------------------------------------------------------------------------------------

#Finally register all parts into existence
classes = [MySettings,
CreateEmpty_Panel,
LF_Panel,
MY_OT_create_empty,
LF_PREANIMATION_Show_Status,
MESH_UL_lf_hub_meshes,
MESH_OT_add_lf_hub_mesh,
MESH_OT_remove_lf_hub_mesh,
LF_hub_BUTTON_parent_fun,
LF_hub_button_config,
MESH_UL_lf_lca_meshes,
MESH_OT_add_lf_lca_mesh,
MESH_OT_remove_lf_lca_mesh,
LF_LCA_BUTTON_parent_fun,
LF_lca_button_config,
MESH_UL_lf_tension_meshes,
MESH_OT_add_lf_tension_mesh,
MESH_OT_remove_lf_tension_mesh,
LF_TENSION_BUTTON_parent_fun,
LF_tension_button_config,
MESH_UL_lf_susp_meshes,
MESH_OT_add_lf_susp_mesh,
MESH_OT_remove_lf_susp_mesh,
LF_SUSP_BUTTON_parent_fun,
MESH_UL_lf_coil_meshes,
MESH_OT_add_lf_coil_mesh,
MESH_OT_remove_lf_coil_mesh,
LF_COIL_BUTTON_parent_fun,
LF_coil_button_config,
MESH_UL_lf_spring_meshes,
MESH_OT_add_lf_spring_mesh,
MESH_OT_remove_lf_spring_mesh,
LF_spring_BUTTON_parent_fun,
LF_spring_button_config,
MESH_UL_lf_steer_meshes,
MESH_OT_add_lf_steer_mesh,
MESH_OT_remove_lf_steer_mesh,
LF_steer_BUTTON_parent_fun,
LF_steer_button_config,
MESH_UL_lf_wheel_meshes,
MESH_OT_add_lf_wheel_mesh,
MESH_OT_remove_lf_wheel_mesh,
LF_WHEEL_BUTTON_parent_fun,
MESH_UL_lf_rim_meshes,
MESH_OT_add_lf_rim_mesh,
MESH_OT_remove_lf_rim_mesh,
LF_rim_BUTTON_parent_fun,
LF_rim_BUTTON_zero_trans,
MESH_UL_lf_tyre_meshes,
MESH_OT_add_lf_tyre_mesh,
MESH_OT_remove_lf_tyre_mesh,
LF_tyre_BUTTON_parent_fun,
LF_tyre_BUTTON_zero_trans,
RF_Panel,
RF_PREANIMATION_Show_Status,
MESH_UL_rf_hub_meshes,
MESH_OT_add_rf_hub_mesh,
MESH_OT_remove_rf_hub_mesh,
RF_hub_BUTTON_parent_fun,
RF_hub_button_config,
MESH_UL_rf_lca_meshes,
MESH_OT_add_rf_lca_mesh,
MESH_OT_remove_rf_lca_mesh,
RF_LCA_BUTTON_parent_fun,
RF_lca_button_config,
MESH_UL_rf_tension_meshes,
MESH_OT_add_rf_tension_mesh,
MESH_OT_remove_rf_tension_mesh,
RF_TENSION_BUTTON_parent_fun,
RF_tension_button_config,
MESH_UL_rf_susp_meshes,
MESH_OT_add_rf_susp_mesh,
MESH_OT_remove_rf_susp_mesh,
RF_SUSP_BUTTON_parent_fun,
MESH_UL_rf_coil_meshes,
MESH_OT_add_rf_coil_mesh,
MESH_OT_remove_rf_coil_mesh,
RF_COIL_BUTTON_parent_fun,
RF_coil_button_config,
MESH_UL_rf_spring_meshes,
MESH_OT_add_rf_spring_mesh,
MESH_OT_remove_rf_spring_mesh,
RF_spring_BUTTON_parent_fun,
RF_spring_button_config,
MESH_UL_rf_steer_meshes,
MESH_OT_add_rf_steer_mesh,
MESH_OT_remove_rf_steer_mesh,
RF_steer_BUTTON_parent_fun,
RF_steer_button_config,
MESH_UL_rf_wheel_meshes,
MESH_OT_add_rf_wheel_mesh,
MESH_OT_remove_rf_wheel_mesh,
RF_WHEEL_BUTTON_parent_fun,
MESH_UL_rf_rim_meshes,
MESH_OT_add_rf_rim_mesh,
MESH_OT_remove_rf_rim_mesh,
RF_rim_BUTTON_parent_fun,
RF_rim_BUTTON_zero_trans,
MESH_UL_rf_tyre_meshes,
MESH_OT_add_rf_tyre_mesh,
MESH_OT_remove_rf_tyre_mesh,
RF_tyre_BUTTON_parent_fun,
RF_tyre_BUTTON_zero_trans]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=MySettings)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.settings


if __name__ == "__main__":
    register()