# --------
# IMPORTS
# --------

import bpy

# -------------------
# PLUGIN INFORMATION
# -------------------

bl_info = {
    "name": "Dody's Shortcuts",
    "author": "Dodylectable",
    "version": (1, 0, 1),
    "blender": (4, 0, 0),
    "category": "Interface",
    "location": "View 3D -> Side Bar",
    "support": 'COMMUNITY',
    "description": "A simple plugin I've written to quickly do some functions while modding, saves a lot of clicks."
}

# -----------------
# REGISTER CLASSES
# -----------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__init__":
    register()

# --------
# CLASSES
# --------

class RemovePanel(bpy.types.Panel):
    bl_label = "Dody's Shortcuts"
    bl_idname = "OBJECT_PT_remove"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dody's Shortcuts"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.remove_vertex_groups", text="Remove Vertex Groups")
        
        row = layout.row()
        row.operator("object.remove_modifiers", text="Remove Modifiers")
        
        row = layout.row()
        row.operator("object.remove_vertex_colors", text="Remove Vertex Colors")

        row = layout.row()
        row.operator("object.remove_shape_keys", text="Remove Shape Keys")

        row = layout.row()
        row.operator("object.remove_uv_maps", text="Remove UV Maps")

        row = layout.row()
        row.operator("object.check_shapekey_count", text="Check Shape Key Count")
        
class RemoveVertexGroupsOperator(bpy.types.Operator):
    """Remove all Vertex Groups from the selected objects"""
    bl_idname = "object.remove_vertex_groups"
    bl_label = "Remove Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        objects_with_groups = 0
        active_object = context.active_object

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.vertex_groups:
                obj.vertex_groups.clear()
                objects_with_groups += 1

        if objects_with_groups > 0:
            if objects_with_groups == 1 and active_object:
                self.report({'INFO'}, f"Vertex Groups removed from '{active_object.name}'.")
            else:
                self.report({'INFO'}, f"Vertex Groups removed from {objects_with_groups} objects.")
        else:
            self.report({'WARNING'}, f"Object '{active_object.name}' had no Vertex Groups.")
        return {'FINISHED'}

class RemoveModifiersOperator(bpy.types.Operator):
    """Remove all Modifiers from the selected objects"""
    bl_idname = "object.remove_modifiers"
    bl_label = "Remove Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        objects_with_modifiers = 0
        active_object = context.active_object

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.modifiers:
                while obj.modifiers:
                    obj.modifiers.remove(obj.modifiers[0])
                objects_with_modifiers += 1

        if objects_with_modifiers > 0:
            if objects_with_modifiers == 1 and active_object:
                self.report({'INFO'}, f"Modifiers removed from '{active_object.name}'.")
            else:
                self.report({'INFO'}, f"Modifiers removed from {objects_with_modifiers} objects.")
        else:
            self.report({'WARNING'}, f"Object '{active_object.name}' had no Modifiers.")
        return {'FINISHED'}
        
class RemoveVertexColorsOperator(bpy.types.Operator):
    """Remove all Vertex Colors from the selected objects"""
    bl_idname = "object.remove_vertex_colors"
    bl_label = "Remove Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(
            obj.type == 'MESH' and obj.data is not None for obj in context.selected_objects
        )

    def execute(self, context):
        objects_with_colors = 0
        active_object = context.active_object

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.data:
                removed_colors = 0
                for att in list(obj.data.attributes):
                    if att.data_type in {'FLOAT_COLOR', 'BYTE_COLOR'}:
                        obj.data.attributes.remove(att)
                        removed_colors += 1
                if removed_colors > 0:
                    objects_with_colors += 1

        if objects_with_colors > 0:
            if objects_with_colors == 1 and active_object:
                self.report({'INFO'}, f"Vertex Colors removed from '{active_object.name}'.")
            else:
                self.report({'INFO'}, f"Vertex Colors removed from {objects_with_colors} objects.")
        else:
            self.report({'WARNING'}, f"Object '{active_object.name}' had no Vertex Colors.")
        return {'FINISHED'}
    
class RemoveShapeKeysOperator(bpy.types.Operator):
    """Remove all Shape Keys from the selected objects"""
    bl_idname = "object.remove_shape_keys"
    bl_label = "Remove Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        active_object = context.active_object

        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            if obj.data.shape_keys:
                shape_keys = obj.data.shape_keys.key_blocks

                if len(shape_keys) == 0:
                    self.report({'WARNING'}, f"Object '{obj.name}' has no Shape Keys.")
                else:
                    for key in list(shape_keys)[1:]:
                        obj.shape_key_remove(key)
                    
                    if len(shape_keys) == 1:
                        obj.shape_key_remove(shape_keys[0])
                    
                    self.report({'INFO'}, f"Shape Keys for '{obj.name}' are deleted!")
            else:
                self.report({'WARNING'}, f"Object '{obj.name}' has no Shape Keys.")

        return {'FINISHED'}
    
class RemoveUVMapsOperator(bpy.types.Operator):
    """Remove all UV Maps from the selected objects"""
    bl_idname = "object.remove_uv_maps"
    bl_label = "Remove UV Maps"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        objects_with_uv_maps = 0
        active_object = context.active_object

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.data.uv_layers:
                while obj.data.uv_layers:
                    obj.data.uv_layers.remove(obj.data.uv_layers[0])
                objects_with_uv_maps += 1

        if objects_with_uv_maps > 0:
            if objects_with_uv_maps == 1 and active_object:
                self.report({'INFO'}, f"UV Maps removed from '{active_object.name}'.")
            else:
                self.report({'INFO'}, f"UV Maps removed from {objects_with_uv_maps} objects.")
        else:
            self.report({'WARNING'}, f"Object '{obj.name}' has no UV Maps.")

        return {'FINISHED'}
    
class CheckShapeKeyCount(bpy.types.Operator):
    """Check how many shape keys does an object have"""
    bl_idname = "object.check_shapekey_count"
    bl_label = "Check Shape Key Count"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        active_object = context.active_object

        if active_object.data.shape_keys:
            shape_keys = active_object.data.shape_keys.key_blocks
            self.report({'INFO'}, f"Object '{active_object.name}' has {len(shape_keys)} Shape Keys.")
        else:
            self.report({'WARNING'}, f"Object '{active_object.name}' has no Shape Keys.")
        return {'FINISHED'}
    

classes = [
    RemovePanel,
    RemoveVertexGroupsOperator,
    RemoveModifiersOperator,
    RemoveVertexColorsOperator,
    RemoveShapeKeysOperator,
    RemoveUVMapsOperator,
    CheckShapeKeyCount,
]