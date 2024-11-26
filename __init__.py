import bpy

bl_info = {
    "name": "Dody's Shortcuts",
    "author": "Dodylectable",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "category": "Interface",
    "location": "View 3D -> Side Bar",
    "support": 'COMMUNITY',
    "description": "A simple plugin I've written to quickly do some functions while modding, saves a lot of clicks."
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__init__":
    register()

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
        row.operator("object.check_shapekey_count", text="Check Shape Key Count")
        
class RemoveVertexGroupsOperator(bpy.types.Operator):
    """Remove an object's vertex groups"""
    bl_idname = "object.remove_vertex_groups"
    bl_label = "Remove Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            obj.vertex_groups.clear()
        print("Vertex Groups are deleted!")
        return {'FINISHED'}

class RemoveModifiersOperator(bpy.types.Operator):
    """Remove an object's modifiers"""
    bl_idname = "object.remove_modifiers"
    bl_label = "Remove Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            for mod in obj.modifiers:
                obj.modifiers.remove(mod)
        print("Modifiers are deleted!")
        return {'FINISHED'}
        
class RemoveVertexColorsOperator(bpy.types.Operator):
    """Remove an object's vertex colors"""
    bl_idname = "object.remove_vertex_colors"
    bl_label = "Remove Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            for att in list(obj.data.attributes):
                if att.data_type in {'FLOAT_COLOR', 'BYTE_COLOR'}:
                    obj.data.attributes.remove(att)
        print("Vertex Colors are deleted!")
        return {'FINISHED'}
    
class RemoveShapeKeysOperator(bpy.types.Operator):
    """Remove an object's shape keys"""
    bl_idname = "object.remove_shape_keys"
    bl_label = "Remove Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.data.shape_keys:
                shape_keys = obj.data.shape_keys.key_blocks
                for key in list(shape_keys)[1:]:
                    obj.shape_key_remove(key)
                if len(shape_keys) == 1:
                    obj.shape_key_remove(shape_keys[0])
        print("Shape Keys are deleted!")
        return {'FINISHED'}
    
class CheckShapeKeyCount(bpy.types.Operator):
    """Check how many shape keys does an object have"""
    bl_idname = "object.check_shapekey_count"
    bl_label = "Check Shape Key Count"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_object = bpy.context.active_object

        if active_object and active_object.type == 'MESH':
            shape_keys = active_object.data.shape_keys
            
            if shape_keys:
                print(f"Object '{active_object.name}' has {len(shape_keys.key_blocks)} shape keys.")
            else:
                print(f"Object '{active_object.name}' has no shape keys.")
        else:
            print("Please select a mesh object.")
        return {'FINISHED'}
        
classes = [
    RemovePanel,
    RemoveVertexGroupsOperator,
    RemoveModifiersOperator,
    RemoveVertexColorsOperator,
    RemoveShapeKeysOperator,
    CheckShapeKeyCount,
]