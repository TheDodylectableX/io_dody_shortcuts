# --------
# IMPORTS
# --------

import bpy
import bmesh

# -------------------
# PLUGIN INFORMATION
# -------------------

bl_info = {
    "name": "Dody's Shortcuts",
    "author": "Dodylectable",
    "version": (1, 0, 2),
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

# ----------
# THE PANEL
# ----------

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
        row.operator("object.remove_materials", text="Remove Materials")

        row = layout.row()
        row.operator("object.remove_unused_vertex_groups", text="Remove Unused Vertex Groups")

        layout.separator()

        row = layout.row()
        row.operator("object.check_shapekey_count", text="Check Shape Key Count")


        row = layout.row()
        row.operator("object.flip_uv_horizontally", text="Flip UV Maps Horizontally")

        row = layout.row()
        row.operator("object.flip_uv_vertically", text="Flip UV Maps Vertically")

        row = layout.row()
        row.operator("object.add_custom_vertex_color", text="Quickly Add Custom Vertex Colors")

# --------
# CLASSES
# --------
        
class RemoveVertexGroupsOperator(bpy.types.Operator):
    """Remove all Vertex Groups from the selected objects"""
    bl_idname = "object.remove_vertex_groups"
    bl_label = "Remove Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.vertex_groups for obj in context.selected_objects)

    def execute(self, context):
        removed_groups_report = {}

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.vertex_groups:
                removed_groups = [group.name for group in obj.vertex_groups]
                obj.vertex_groups.clear()
                removed_groups_report[obj.name] = removed_groups

        if not removed_groups_report:
            self.report({'WARNING'}, "No Vertex Groups to remove.")
        else:
            for obj_name, groups in removed_groups_report.items():
                self.report({'INFO'}, f"Removed Vertex Groups from '{obj_name}': {', '.join(groups)}")

        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------

class RemoveModifiersOperator(bpy.types.Operator):
    """Remove all Modifiers from the selected objects"""
    bl_idname = "object.remove_modifiers"
    bl_label = "Remove Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.modifiers for obj in context.selected_objects)

    def execute(self, context):
        removed_modifiers_report = {}

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.modifiers:
                removed_modifiers = [mod.name for mod in obj.modifiers]
                while obj.modifiers:
                    obj.modifiers.remove(obj.modifiers[0])
                removed_modifiers_report[obj.name] = removed_modifiers

        if not removed_modifiers_report:
            self.report({'WARNING'}, "No Modifiers to remove.")
        else:
            for obj_name, mods in removed_modifiers_report.items():
                self.report({'INFO'}, f"Removed Modifiers from '{obj_name}': {', '.join(mods)}")

        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------
        
class RemoveVertexColorsOperator(bpy.types.Operator):
    """Remove all Vertex Colors from the selected objects"""
    bl_idname = "object.remove_vertex_colors"
    bl_label = "Remove Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and any(att.data_type in {'FLOAT_COLOR', 'BYTE_COLOR'} for att in obj.data.attributes) for obj in context.selected_objects)

    def execute(self, context):
        removed_colors_report = {}

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.data:
                removed_colors = []
                for att in list(obj.data.attributes):
                    if att.data_type in {'FLOAT_COLOR', 'BYTE_COLOR'}:
                        removed_colors.append(att.name)
                        obj.data.attributes.remove(att)
                if removed_colors:
                    removed_colors_report[obj.name] = removed_colors

        if not removed_colors_report:
            self.report({'WARNING'}, "No Vertex Colors to remove.")
        else:
            for obj_name, colors in removed_colors_report.items():
                self.report({'INFO'}, f"Removed Vertex Colors from '{obj_name}': {', '.join(colors)}")

        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------
    
class RemoveShapeKeysOperator(bpy.types.Operator):
    """Remove all Shape Keys from the selected objects"""
    bl_idname = "object.remove_shape_keys"
    bl_label = "Remove Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.data.shape_keys and obj.data.shape_keys.key_blocks for obj in context.selected_objects)

    def execute(self, context):
        removed_keys_report = {}

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.data.shape_keys:
                removed_keys = [key.name for key in obj.data.shape_keys.key_blocks]
                for key in list(obj.data.shape_keys.key_blocks):
                    obj.shape_key_remove(key)
                removed_keys_report[obj.name] = removed_keys

        if not removed_keys_report:
            self.report({'WARNING'}, "No Shape Keys to remove.")
        else:
            for obj_name, keys in removed_keys_report.items():
                self.report({'INFO'}, f"Removed Shape Keys from '{obj_name}': {', '.join(keys)}")

        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------
    
class RemoveUVMapsOperator(bpy.types.Operator):
    """Remove all UV Maps from the selected objects"""
    bl_idname = "object.remove_uv_maps"
    bl_label = "Remove UV Maps"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.data.uv_layers for obj in context.selected_objects)

    def execute(self, context):
        removed_uv_maps_report = {}

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.data.uv_layers:
                removed_uv_maps = [uv.name for uv in obj.data.uv_layers]
                while obj.data.uv_layers:
                    obj.data.uv_layers.remove(obj.data.uv_layers[0])
                removed_uv_maps_report[obj.name] = removed_uv_maps

        if not removed_uv_maps_report:
            self.report({'WARNING'}, "No UV Maps to remove.")
        else:
            for obj_name, uv_maps in removed_uv_maps_report.items():
                self.report({'INFO'}, f"Removed UV Maps from '{obj_name}': {', '.join(uv_maps)}")

        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------
    
class RemoveMaterialsOperator(bpy.types.Operator):
    """Remove all Materials from selected objects"""
    bl_idname = "object.remove_materials"
    bl_label = "Remove All Materials"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' and obj.material_slots for obj in context.selected_objects)

    def execute(self, context):
        removed_materials_report = {}

        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj.material_slots:
                removed_materials = [slot.material.name if slot.material else "None" for slot in obj.material_slots]
                for slot in obj.material_slots:
                    slot.material = None
                removed_materials_report[obj.name] = removed_materials

        if not removed_materials_report:
            self.report({'WARNING'}, "No Materials to remove.")
        else:
            for obj_name, materials in removed_materials_report.items():
                self.report({'INFO'}, f"Removed Materials from '{obj_name}': {', '.join(materials)}")

        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------

class RemoveUnusedVertexGroupsOperator(bpy.types.Operator):
    """Remove unused vertex groups from selected objects and normalize weights"""
    bl_idname = "object.remove_unused_vertex_groups"
    bl_label = "Remove Unused Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' and obj.vertex_groups for obj in context.selected_objects)

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        threshold = 0.1  # All groups below this threshold will be considered unused
        removed_groups_report = {}

        for obj in selected_objects:
            if not obj.vertex_groups:
                continue

            mesh = obj.data
            vertex_groups = obj.vertex_groups
            groups_to_remove = []

            for group in vertex_groups:
                is_used = False

                # Check each vertex for weights in this group
                for vertex in mesh.vertices:
                    for group_weight in vertex.groups:
                        if group_weight.group == group.index and group_weight.weight > threshold:
                            is_used = True
                            break
                    if is_used:
                        break

                if not is_used:
                    groups_to_remove.append(group.name)

            # Remove unused groups and add them to the report
            for group_name in groups_to_remove:
                vertex_groups.remove(vertex_groups[group_name])
            if groups_to_remove:
                removed_groups_report[obj.name] = groups_to_remove

            # Normalize weights
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.vertex_group_normalize_all(lock_active=False)

        if not removed_groups_report:
            self.report({'INFO'}, "No unused vertex groups found.")
        else:
            for obj_name, groups in removed_groups_report.items():
                self.report({'INFO'}, f"Removed groups from '{obj_name}': {', '.join(groups)}")

        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------
    
class CheckShapeKeyCount(bpy.types.Operator):
    """Check how many shape keys does an object have"""
    bl_idname = "object.check_shapekey_count"
    bl_label = "Check Shape Key Count"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.data.shape_keys and obj.data.shape_keys.key_blocks for obj in context.selected_objects)

    def execute(self, context):
        active_object = context.active_object

        if active_object.data.shape_keys:
            shape_keys = active_object.data.shape_keys.key_blocks
            key_names = [key.name for key in shape_keys]
            self.report(
                {'INFO'},
                f"Object '{active_object.name}' has {len(shape_keys)} Shape Keys: {', '.join(key_names)}."
            )
        else:
            self.report({'WARNING'}, f"Object '{active_object.name}' has no Shape Keys.")
        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------
    
class FlipUVHorizontallyOperator(bpy.types.Operator):
    """Flip UV maps horizontally for selected objects"""
    bl_idname = "object.flip_uv_horizontally"
    bl_label = "Flip UV Maps Horizontally"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.data.uv_layers for obj in context.selected_objects)

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'WARNING'}, "No mesh objects selected.")
            return {'CANCELLED'}

        # Switch to Object Mode if in Edit Mode to access UVs
        original_mode = context.object.mode
        if original_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for obj in selected_objects:
            mesh = obj.data
            if not mesh.uv_layers:
                continue

            uv_layer = mesh.uv_layers.active.data

            for uv in uv_layer:
                uv.uv.x = 1.0 - uv.uv.x

        # Switch back to Edit Mode if it was active
        if original_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        if len(selected_objects) == 1:
            self.report({'INFO'}, f"UV maps flipped horizontally for '{selected_objects[0].name}'.")
        else:
            self.report({'INFO'}, f"UV maps flipped horizontally for {len(selected_objects)} objects.")
        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------

class FlipUVVerticallyOperator(bpy.types.Operator):
    """Flip UV maps vertically for selected objects"""
    bl_idname = "object.flip_uv_vertically"
    bl_label = "Flip UV Maps Vertically"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' and obj.data.uv_layers for obj in context.selected_objects)

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'WARNING'}, "No mesh objects selected.")
            return {'CANCELLED'}

        # Switch to Object Mode if in Edit Mode to access UVs
        original_mode = context.object.mode
        if original_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for obj in selected_objects:
            mesh = obj.data
            if not mesh.uv_layers:
                continue

            uv_layer = mesh.uv_layers.active.data

            for uv in uv_layer:
                uv.uv.y = 1.0 - uv.uv.y

        # Switch back to Edit Mode if it was active
        if original_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        if len(selected_objects) == 1:
            self.report({'INFO'}, f"UV maps flipped vertically for '{selected_objects[0].name}'.")
        else:
            self.report({'INFO'}, f"UV maps flipped vertically for {len(selected_objects)} objects.")
        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------

class AddCustomVertexColorOperator(bpy.types.Operator):
    """Add a Face Corner Byte Color attribute with a custom color and name to all selected objects"""
    bl_idname = "object.add_custom_vertex_color"
    bl_label = "Quickly Add Custom Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    # Property for the custom color (RGBA)
    custom_color: bpy.props.FloatVectorProperty(
        name="Vertex Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)  # Default is White
    ) # type: ignore

    # Property for the name of the vertex color attribute
    color_name: bpy.props.StringProperty(
        name="Color Name",
        default="Color",
        description="Name of the new vertex color attribute"
    ) # type: ignore

    def invoke(self, context, event):
        # Open the dialog for user input
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "color_name", text="Vertex Color Name")  # Input field for the attribute name
        layout.prop(self, "custom_color", text="Color Picker")     # Color picker field

    def execute(self, context):
        selected_objects = context.selected_objects
        processed_objects = []

        # Convert the custom color to Byte format (0-255)
        color_byte = tuple(int(channel * 255) for channel in self.custom_color)

        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data

                # Check if a color attribute with the same name already exists
                if self.color_name in mesh.attributes:
                    self.report({'WARNING'}, f"'{obj.name}' already has a vertex color named '{self.color_name}'. Skipping.")
                    continue

                # Create a new Byte Color attribute with the specified name
                color_layer = mesh.attributes.new(name=self.color_name, type='BYTE_COLOR', domain='CORNER')

                # Fill the color attribute with the custom color
                for corner_color in color_layer.data:
                    corner_color.color = color_byte

                processed_objects.append(obj.name)

        if processed_objects:
            self.report(
                {'INFO'},
                f"Vertex Color '{self.color_name}' added to {len(processed_objects)} object(s): {', '.join(processed_objects)}"
            )
        else:
            self.report({'WARNING'}, "No valid objects to process.")

        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------
        
classes = [
    RemovePanel,
    RemoveVertexGroupsOperator,
    RemoveModifiersOperator,
    RemoveVertexColorsOperator,
    RemoveShapeKeysOperator,
    RemoveUVMapsOperator,
    RemoveMaterialsOperator,
    RemoveUnusedVertexGroupsOperator,
    CheckShapeKeyCount,
    FlipUVHorizontallyOperator,
    FlipUVVerticallyOperator,
    AddCustomVertexColorOperator,
]