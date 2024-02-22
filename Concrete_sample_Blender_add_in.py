bl_info = {
    "name": "Concrete Sample Generator",
    "author": "Xinyi Hu",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "description": "This plug-in is for generating the concrete geometrical model, delicating for the mesoscal modeling of concrete and multiple phases materials. Hopefully it is helpful for the researcheres of concrete domain.",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

import bpy
from bpy.props import EnumProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty
from bpy.types import Operator, Panel, PropertyGroup

# Part 1: mold generatior
def delete_face_update(self, context):
    obj = bpy.context.active_object
    if obj is None:
        return

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if self.delete_top:
        # Find the face with a normal in the positive Z direction
        top_face = next((p for p in obj.data.polygons if p.normal.z > 0), None)
        if top_face is not None:
            top_face.select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.object.mode_set(mode='OBJECT')

    if self.delete_bottom:
        # Find the face with a normal in the negative Z direction
        bottom_face = next((p for p in obj.data.polygons if p.normal.z < 0), None)
        if bottom_face is not None:
            bottom_face.select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.object.mode_set(mode='OBJECT')
             
class MoldGenerator(bpy.types.Operator):
    bl_idname = "object.mold_generator"
    bl_label = "Mold Generator"
        
    def execute(self, context):
        my_tool = context.window_manager.my_tool

        if my_tool.mold_shape == 'CUBE':
            bpy.ops.mesh.primitive_cube_add(size=my_tool.cube_size)
            self.top_face_index = len(bpy.context.object.data.polygons) - 1
            self.bottom_face_index = 0
        elif my_tool.mold_shape == 'CYLINDER':
            bpy.ops.mesh.primitive_cylinder_add(radius=my_tool.cylinder_radius, depth=my_tool.cylinder_depth)
            self.top_face_index = len(bpy.context.object.data.polygons) - 1
            self.bottom_face_index = 0
        
        return {'FINISHED'}
    
# Part 2: Rigid Body setting
class RigidBodySetting(bpy.types.Operator):
    bl_idname = "object.rigid_body_setting"
    bl_label = "Rigid Body Setting"
    
    
    type: EnumProperty(
        name="Type",
        items=[('ACTIVE', 'Active', ''), ('PASSIVE', 'Passive', '')],
        default='PASSIVE',
    )
    
    collision_shape: EnumProperty(
        name="Shape",
        items=[('BOX', 'Box', ''), ('SPHERE', 'Sphere', ''), ('MESH', 'Mesh', '')],
        default='MESH',
    )
    
    mass_mode: EnumProperty(
        name="Mass Mode",
        items=[('CUSTOM', 'Custom', ''), ('DENSITY', 'Density', '')],
        default='DENSITY',)
        
    mass: FloatProperty(name='Mass', default=1.0)
    density: FloatProperty(name="Density", default=2500)
    friction: FloatProperty(name="Friction", default=0.5)
    bounciness: FloatProperty(name="Bounciness", default=0)
    use_margin: BoolProperty(name="Use Margin", default=True)  
    collision_margin: FloatProperty(name="Collision Margin", default=0.1)
    
    def execute(self, context):
        my_tool = context.window_manager.my_tool
        # set the rigid body properties
        obj = bpy.context.object
        bpy.ops.rigidbody.object_add(type=my_tool.type)
        obj.rigid_body.collision_shape = my_tool.collision_shape
        obj.rigid_body.friction = my_tool.friction
        obj.rigid_body.restitution = my_tool.bounciness
        obj.rigid_body.use_margin = my_tool.use_margin
        if my_tool.use_margin:  # Only set collision_margin if use_margin is True
            obj.rigid_body.collision_margin = my_tool.collision_margin
        # Set the mass
        if my_tool.mass_mode == 'CUSTOM':
            obj.rigid_body.mass = my_tool.mass
            bpy.context.scene.update() 
        elif my_tool.mass_mode == 'DENSITY':
            bpy.context.object.select_set(True)  # Select the object
            bpy.ops.rigidbody.mass_calculate(density=my_tool.density)
        
        return {'FINISHED'}

# Part 3��vibration
class Vibration(bpy.types.Operator):
    bl_idname = "object.vibration"
    bl_label = "Vibration"
    
    direction: EnumProperty(
        name="Direction",
        items=[('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')],
        default='X',
    )
    
    amplitude: FloatProperty(name="Amplitude", default=1)
    phase_multiplier: FloatProperty(name="Phase Multiplier", default=1)
    phase_offset: FloatProperty(name="Phase Offset", default=1)
    value_offset: FloatProperty(name="Value Offset", default=1)
    use_restricted_range: BoolProperty(name="Restrict influence range", default=True)
    frame_start: IntProperty(name="Frame Start", default=0)
    frame_end: IntProperty(name="Frame End", default=100)
    blend_in: FloatProperty(name="Blend In", default=10)
    blend_out: FloatProperty(name="Blend Out", default=10)

    def execute(self, context):
            obj = bpy.context.object
            if obj.animation_data is None:
                obj.animation_data_create()

            if obj.animation_data.action is None:
                obj.animation_data.action = bpy.data.actions.new(name="VibrationAction")

            # Set the index based on the direction
            if self.direction == 'X':
                index = 0
            elif self.direction == 'Y':
                index = 1
            elif self.direction == 'Z':
                index = 2
            # Check if the fcurve already exists
            fcurve = next((fc for fc in obj.animation_data.action.fcurves if fc.data_path == "location" and fc.array_index == index), None)
            
            if fcurve is None:
                fcurve = obj.animation_data.action.fcurves.new(data_path= "location", index=index)
                mod = fcurve.modifiers.new(type='FNGENERATOR')   
            else:
                mod = fcurve.modifiers[0]
            
            mod.amplitude = self.amplitude
            mod.phase_multiplier = self.phase_multiplier
            mod.phase_offset = self.phase_offset
            mod.value_offset = self.value_offset
            mod.use_additive = False
            mod.use_restricted_range = self.use_restricted_range
            if self.use_restricted_range:
                mod.frame_start = self.frame_start
                mod.frame_end = self.frame_end
                mod.blend_in = self.blend_in
                mod.blend_out = self.blend_out
            return {'FINISHED'}


# Properties definition
class MyProperties(bpy.types.PropertyGroup):
    # parameters for mold properties
    mold_shape: EnumProperty(
        name="Mold Shape",
        items=[('CUBE', "Cube", ""), ('CYLINDER', "Cylinder", "")],
        default='CUBE',
    )

    cube_size: FloatProperty(name="Cube Size", default=100.0)
    cylinder_radius: FloatProperty(name="Cylinder Radius", default=50.0)
    cylinder_depth: FloatProperty(name="Cylinder Depth", default=150.0)

    delete_top: BoolProperty(name='Delete Top', default=False, update=delete_face_update)
    delete_bottom: BoolProperty(name='Delete Bottom', default=False, update=delete_face_update)
 
    # parameters for rigid body properties
    type: EnumProperty(
        name="Type",
        items=[('ACTIVE', 'Active', ''), ('PASSIVE', 'Passive', '')],
        default='PASSIVE',
    )
    collision_shape: EnumProperty(
        name="Shape",
        items=[('BOX', 'Box', ''), ('SPHERE', 'Sphere', ''), ('MESH', 'Mesh', '')],
        default='BOX',
    )
    mass_mode: EnumProperty(
        name="Mass Mode",
        items=[('CUSTOM', 'Custom', ''), ('DENSITY', 'Density', '')],
        default='DENSITY',)
        
    mass: FloatProperty(name='Mass', default=1.0)
    density: FloatProperty(name="Density", default=2500)
    friction: FloatProperty(name="Friction", default=0.5)
    bounciness: FloatProperty(name="Bounciness", default=0)
    use_margin: BoolProperty(name="Use Margin", default=True) 
    collision_margin: FloatProperty(name="Collision Margin", default=0.1)
    
    # parameters for vibration properties
    direction: EnumProperty(
        name="Direction",
        items=[('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')],
        default='X',
    )
    amplitude: FloatProperty(name="Amplitude", default=1)
    phase_multiplier: FloatProperty(name="Phase Multiplier", default=1)
    phase_offset: FloatProperty(name="Phase Offset", default=1)
    value_offset: FloatProperty(name="Value Offset", default=1)
    use_restricted_range: BoolProperty(name="Use Frame Range", default=False)
    frame_start: IntProperty(name="Frame Start", default=400)
    frame_end: IntProperty(name="Frame End", default=1000)
    blend_in: FloatProperty(name="Blend In", default=10)
    blend_out: FloatProperty(name="Blend Out", default=10)
    
class MoldGeneratorPanel(bpy.types.Panel):
    bl_label = "Mold Generator"
    bl_idname = "OBJECT_PT_mold_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Concrete sample"

    def draw(self, context):
        layout = self.layout
        my_tool = context.window_manager.my_tool

        # Mold Generator
        box = layout.box()
        
        box.prop(my_tool, "mold_shape")
        if my_tool.mold_shape == 'CUBE':
            box.prop(my_tool, "cube_size", text="Cube Size")
            box.prop(my_tool, "cylinder_radius", text="Cylinder Radius", emboss=False)
            box.prop(my_tool, "cylinder_depth", text="Cylinder Depth", emboss=False)
        elif my_tool.mold_shape == 'CYLINDER':
            box.prop(my_tool, "cube_size", text="Cube Size", emboss=False)
            box.prop(my_tool, "cylinder_radius", text="Cylinder Radius")
            box.prop(my_tool, "cylinder_depth", text="Cylinder Depth")
        box.prop(my_tool, "delete_top", text="Delete Top")
        box.prop(my_tool, "delete_bottom", text="Delete Bottom")
        box.operator("object.mold_generator", text="Applied!")

class RigidBodySettingPanel(bpy.types.Panel):
    bl_label = "Rigid Body Setting"
    bl_idname = "OBJECT_PT_rigid_body_setting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Concrete sample"

    def draw(self, context):
        layout = self.layout
        my_tool = context.window_manager.my_tool        
        # Rigid Body Setting
        box = layout.box()
        
        box.prop(my_tool, "type")
        box.prop(my_tool, 'collision_shape')
        box.prop(my_tool, "friction")
        box.prop(my_tool, "bounciness")
        box.prop(my_tool, "use_margin") 
        if my_tool.use_margin:
            box.prop(my_tool, "collision_margin")
        box.prop(my_tool, "mass_mode")  
        if my_tool.mass_mode == 'CUSTOM':
            box.prop(my_tool, "mass")  
        elif my_tool.mass_mode == 'DENSITY':
            box.prop(my_tool, "density")  
        box.operator("object.rigid_body_setting", text="Applied!")
        
class VibrationPanel(bpy.types.Panel):
    bl_label = "Vibration setting"
    bl_idname = "OBJECT_PT_Vibration"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Concrete sample"
    
    def draw(self, context):
        layout = self.layout
        my_tool = context.window_manager.my_tool           
        # Vibration
        box = layout.box()
        
        box.prop(my_tool, "direction")
        box.prop(my_tool, "amplitude")
        box.prop(my_tool, "phase_multiplier")
        box.prop(my_tool, "phase_offset")
        box.prop(my_tool, "value_offset")
        box.prop(my_tool, "use_restricted_range")
        if my_tool.use_restricted_range:
            box.prop(my_tool, "frame_start")
            box.prop(my_tool, "frame_end")
            box.prop(my_tool, "blend_in")
            box.prop(my_tool, "blend_out")
        
        op = box.operator("object.vibration", text="Applied!")
                
        op.direction = my_tool.direction
        op.amplitude = my_tool.amplitude
        op.phase_multiplier = my_tool.phase_multiplier
        op.phase_offset = my_tool.phase_offset
        op.value_offset = my_tool.value_offset
        op.use_restricted_range = my_tool.use_restricted_range
        op.frame_start = my_tool.frame_start
        op.frame_end = my_tool.frame_end
        op.blend_in = my_tool.blend_in
        op.blend_out = my_tool.blend_out


def register():
    bpy.utils.register_class(MoldGenerator)
    bpy.utils.register_class(RigidBodySetting)
    bpy.utils.register_class(Vibration)
    bpy.utils.register_class(MoldGeneratorPanel)
    bpy.utils.register_class(RigidBodySettingPanel)
    bpy.utils.register_class(VibrationPanel)
    bpy.utils.register_class(MyProperties)
    bpy.types.WindowManager.my_tool = bpy.props.PointerProperty(type=MyProperties)

def unregister():
    bpy.utils.unregister_class(MoldGenerator)
    bpy.utils.unregister_class(RigidBodySetting)
    bpy.utils.unregister_class(Vibration)
    bpy.utils.unregister_class(MoldGeneratorPanel)
    bpy.utils.unregister_class(RigidBodySettingPanel)
    bpy.utils.unregister_class(VibrationPanel)
    bpy.utils.unregister_class(MyProperties)
    del bpy.types.WindowManager.my_tool

if __name__ == "__main__":
    register()
