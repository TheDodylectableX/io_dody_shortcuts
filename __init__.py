# --------
# IMPORTS
# --------

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, CollectionProperty
from mathutils import Matrix, Vector
import numpy as np
import re

# -------------------
# PLUGIN INFORMATION
# -------------------

bl_info = {
    "name": "Dody's Shortcuts",
    "author": "Dodylectable",
    "version": (1, 0, 6),
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

class DodyPanel(bpy.types.Panel):
    bl_label = "Dody's Shortcuts"
    bl_idname = "OBJECT_PT_remove"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dody's Shortcuts"

    def draw(self, context):
        layout = self.layout

        # =============
        # THE REMOVERS
        # =============

        row = layout.row()
        row.operator("object.remove_vertex_groups", text="Remove Vertex Groups")

        row = layout.row()
        row.operator("object.remove_unused_vertex_groups", text="Remove Unused Vertex Groups")
        
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

        layout.separator()

        # ============
        # THE HELPERS
        # ============

        row = layout.row()
        row.operator("object.check_shapekey_count", text="Check Shape Key Count")

        row = layout.row()
        row.operator("object.flip_uv_horizontally", text="Flip UV Maps Horizontally")

        row = layout.row()
        row.operator("object.flip_uv_vertically", text="Flip UV Maps Vertically")

        row = layout.row()
        row.operator("object.project_key_to_color", text="Project Shape Key to Vertex Color")

        row = layout.row()
        row.operator("object.project_color_to_key", text="Project Vertex Color to Shape Key")

        row = layout.row()
        row.operator("object.make_collection_per_mesh", text="Make Collection Per Mesh")

        row = layout.row()
        row.operator("object.batch_tris_to_quads", text="Batch Convert Tris to Quads")

        layout.separator()

        row = layout.row()
        row.operator("object.merge_armatures", text="Merge Armatures")

        row = layout.row()
        row.operator("object.retarget_armatures", text="Retarget Armatures")

        layout.separator()

        # ===========
        # THE ADDERS
        # ===========

        row = layout.row()
        row.operator("object.batch_add_vertex_color", text="Add Vertex Colors")

        row = layout.row()
        row.operator("object.batch_add_material", text="Add Materials")

        row = layout.row()
        row.operator("object.batch_add_empty_shapekeys", text="Add Empty Shape Keys")

        if bpy.app.version >= (4, 5, 0):
            layout.separator()

            row = layout.row()
            row.operator("material.batch_cubic_interp_convert", text="Convert Textures' Interpolation to Cubic")

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
                        if group_weight.group == group.index:
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
            self.report({'INFO'},f"Object '{active_object.name}' has {len(shape_keys)} Shape Keys: {', '.join(key_names)}.")
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

class BatchAddVertexColorOperator(bpy.types.Operator):
    """Add a Face Corner Byte Color attribute with a custom color and name to all selected objects"""
    bl_idname = "object.batch_add_vertex_color"
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
            self.report({'INFO'}, f"Vertex Color '{self.color_name}' added to {len(processed_objects)} object(s): {', '.join(processed_objects)}")
        else:
            self.report({'WARNING'}, "No valid objects to process.")

        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------

def get_shape_keys(self, context):
    """Dynamically fetch shape keys when the operator is invoked."""
    obj = context.object
    if obj and obj.type == 'MESH' and obj.data.shape_keys:
        return [(key.name, key.name, "") for key in obj.data.shape_keys.key_blocks if key.name != "Basis"]
    return [("NONE", "No Shape Keys", "No shape keys available")]

class ProjectShapeKeyToVertexColorOperator(bpy.types.Operator):
    """Project a Shape Key's delta data into a Vertex Color Attribute"""
    bl_idname = "object.project_key_to_color"
    bl_label = "Project Shape Key to Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    shape_key_name: bpy.props.EnumProperty(
        name="Shape Key",
        description="Select the shape key to process",
        items=get_shape_keys  # Dynamically fetch shape keys
    ) # type: ignore

    displacement_value: bpy.props.FloatProperty(
        name="Displacement Value",
        description="Normalization value for displacement scaling",
        default=2.1943,
        min=0.001,  # Prevents division by zero
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH' and context.object.data.shape_keys

    def invoke(self, context, event):
        """Fetch shape keys dynamically before showing UI"""
        obj = context.object
        if obj and obj.data.shape_keys:
            shape_keys = get_shape_keys(self, context)
            if shape_keys and shape_keys[0][0] != "NONE":
                self.shape_key_name = shape_keys[0][0]  # Default to first available shape key

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        """Draw dropdown menu for shape key selection"""
        layout = self.layout
        layout.prop(self, "shape_key_name", text="Shape Key")
        layout.prop(self, "displacement_value")

    def execute(self, context):
        """Runs the conversion from shape key to vertex color"""
        obj = context.object
        if not obj or obj.type != 'MESH' or not obj.data.shape_keys:
            self.report({'ERROR'}, "No valid mesh object with shape keys selected.")
            return {'CANCELLED'}

        if self.shape_key_name not in obj.data.shape_keys.key_blocks:
            self.report({'ERROR'}, f"Shape key '{self.shape_key_name}' not found on object '{obj.name}'.")
            return {'CANCELLED'}

        self.shape_key_to_vector_color(obj, self.shape_key_name, self.displacement_value)
        return {'FINISHED'}

    def shape_key_to_vector_color(self, obj, shape_key_name, displacement_value):
        """
        Converts the raw delta vector data of a shape key into a vertex color map (RGB visualization).
        Areas with no morphing will be colored in #808080 (neutral gray).
        """

        shape_keys = obj.data.shape_keys.key_blocks
        basis_key = shape_keys["Basis"]
        target_key = shape_keys[shape_key_name]

        # Get vertex positions from both shape keys
        basis_vertices = np.array([v.co for v in basis_key.data])
        target_vertices = np.array([v.co for v in target_key.data])

        # Compute raw delta vectors per vertex
        deltas = target_vertices - basis_vertices

        # Normalize XYZ vectors from (-max, +max) to (0, 1)
        normalized_deltas = (((deltas / displacement_value) / 2) + 0.5)

        # Define the hex color #808080 (mid gray) as RGB (0–1 range)
        no_morph_color = (0.5, 0.5, 0.5, 1.0)

        # Name the vertex color layer after the shape key
        color_layer_name = f"{shape_key_name}_Vectors"

        # Ensure a vertex color layer exists
        color_layer = obj.data.color_attributes.get(color_layer_name)
        if not color_layer:
            color_layer = obj.data.color_attributes.new(name=color_layer_name, type='BYTE_COLOR', domain='POINT')

        # Assign the raw vector displacement to vertex colors
        for i, color in enumerate(color_layer.data):
            r, g, b = normalized_deltas[i]
            if np.allclose(deltas[i], 0, atol=1e-6):
                color.color = no_morph_color
            else:
                color.color = (r, g, b, 1.0)

        # Update mesh to reflect changes
        obj.data.update()

        self.report({'INFO'}, f"Vertex color '{color_layer_name}' created from shape key '{shape_key_name}' on '{obj.name}'.")

# --------------------------------------------------------------------------------------------------------------

def get_vertex_color_layers(self, context):
    """Fetch available vertex color layers dynamically using vertex_colors."""
    obj = context.object
    if obj and obj.type == 'MESH' and obj.data.vertex_colors:
        return [(layer.name, layer.name, "") for layer in obj.data.vertex_colors]
    return [("NONE", "No Vertex Colors", "No vertex color layers available")]

class ProjectVertexColorToShapeKeyOperator(bpy.types.Operator):
    """Project a Vertex Color Attribute to a Shape Key"""
    bl_idname = "object.project_color_to_key"
    bl_label = "Project Vertex Color to Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    color_layer: bpy.props.EnumProperty(
        name="Vertex Color Layer",
        description="Select the vertex color layer to use for projection",
        items=get_vertex_color_layers
    ) # type: ignore

    displacement_value: bpy.props.FloatProperty(
        name="Displacement Value",
        description="Normalization value for displacement scaling",
        default=2.1943,
        min=0.001  # Prevents division by zero
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH' and context.object.data.vertex_colors

    def invoke(self, context, event):
        """Show the UI dialog before executing"""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        """Draw UI properties"""
        layout = self.layout
        layout.prop(self, "color_layer")
        layout.prop(self, "displacement_value")

    def execute(self, context):
        """Run the vertex color to shape key conversion"""
        obj = context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No valid mesh object selected.")
            return {'CANCELLED'}

        success, color_layer_name, shape_key_name = self.vertex_color_to_morph(obj, self.color_layer, self.displacement_value)
        if success:
            self.report({'INFO'}, f"Vertex color '{color_layer_name}' projected to shape key '{shape_key_name}'.")
        else:
            self.report({'ERROR'}, "Vertex color projection failed.")
        return {'FINISHED'} if success else {'CANCELLED'}

    def vertex_color_to_morph(self, obj, color_layer_name, displacement_value):
        """Converts vertex colors to shape key offsets"""
        mesh = obj.data

        # Fetch selected vertex color layer
        vcol_layer = mesh.vertex_colors.get(color_layer_name)
        if not vcol_layer:
            self.report({'WARNING'}, f"Vertex color layer '{color_layer_name}' not found.")
            return False, None, None

        # Ensure Basis shape key exists
        if not mesh.shape_keys:
            obj.shape_key_add(name="Basis")

        # Create new shape key
        morph_key_name = f"{color_layer_name}_Morph"
        morph_key = obj.shape_key_add(name=morph_key_name)

        # Prepare data storage
        vertex_colors = {i: Vector((0, 0, 0)) for i in range(len(mesh.vertices))}
        vertex_counts = {i: 0 for i in range(len(mesh.vertices))}

        # Loop through loops to collect vertex color data
        color_data = vcol_layer.data
        for loop in mesh.loops:
            vert_index = loop.vertex_index
            color = color_data[loop.index].color  # Get (R, G, B, A)

            # Convert RGB to displacement offset
            offset = Vector((color[0] - 0.5, color[1] - 0.5, color[2] - 0.5))

            # Accumulate per vertex
            vertex_colors[vert_index] += offset
            vertex_counts[vert_index] += 1

        # Apply average displacement to each vertex
        for vert in mesh.vertices:
            if vertex_counts[vert.index] > 0:
                avg_offset = vertex_colors[vert.index] / vertex_counts[vert.index]
                new_position = vert.co + (avg_offset * 2 * displacement_value)
                morph_key.data[vert.index].co = new_position

        return True, color_layer_name, morph_key.name

# --------------------------------------------------------------------------------------------------------------

class ConvertTrisToQuadsOperator(bpy.types.Operator):
    """Convert triangles to quads while preserving UV boundaries"""
    bl_idname = "object.batch_tris_to_quads"
    bl_label = "Batch Convert Triangles to Quads"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Ensure at least one selected mesh exists"""
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        """Convert triangles to quads on all selected mesh objects"""
        converted_objects = 0

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # Switch to Edit Mode
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')

                # Select all faces
                bpy.ops.mesh.select_all(action='SELECT')

                # Run Tris to Quads with "Compare UVs" enabled
                bpy.ops.mesh.tris_convert_to_quads(uvs=True, face_threshold=180, shape_threshold=180)

                # Return to Object Mode
                bpy.ops.object.mode_set(mode='OBJECT')

                converted_objects += 1

        if converted_objects > 0:
            if converted_objects == 1:
                self.report({'INFO'}, f"Converted triangles to quads in '{context.active_object.name}'.")
            else:
                self.report({'INFO'}, f"Converted triangles to quads in {converted_objects} objects.")
        else:
            self.report({'WARNING'}, "No valid meshes with triangles found.")

        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------

class ArmatureMergeItem(bpy.types.PropertyGroup):
    """Helper to store armature names and selection states in the UI"""
    name: StringProperty() # type: ignore
    is_selected: BoolProperty(name="", default=False) # type: ignore

class MergeArmaturesOperator(bpy.types.Operator):
    """Merge multiple armatures into one and retarget meshes with new transfomrs (Must share bone names)"""
    bl_idname = "object.merge_armatures"
    bl_label = "Merge Armatures"
    bl_options = {'REGISTER', 'UNDO'}

# Source selection dropdown
    def enum_source(self, context):
        return [(o.name, o.name, f"Base: {o.name}") 
                for o in bpy.data.objects if o.type == 'ARMATURE']

    source_name: EnumProperty(
        name="Source Armature",
        description="This armature's skeleton and origin will be the foundation",
        items=enum_source
    ) # type: ignore

    sources: CollectionProperty(type=ArmatureMergeItem) # type: ignore

    @classmethod
    def poll(cls, context):
        # We need at least one armature in the scene to even try
        return any(o.type == 'ARMATURE' for o in bpy.data.objects)

    def invoke(self, context, event):
        # Clear the previous list to avoid ghost entries
        self.sources.clear()
        
        # Populate the list with all armatures except the active one (or just list all)
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                item = self.sources.add()
                item.name = obj.name
                # If it's selected in the viewport, check the box by default
                if obj in context.selected_objects:
                    item.is_selected = True
        
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        
        # 1. Source Selection
        row = layout.row()
        row.label(text="Source Armature", icon='ARMATURE_DATA')
        layout.prop(self, "source_name", text="")

        layout.separator()

        # 2. Target Selection
        box = layout.box()
        box.label(text="Armatures to Merge:", icon='ADD')
        
        col = box.column(align=True)
        for item in self.sources:
            # Hide the target from the source list so you don't merge into self
            if item.name == self.source_name:
                continue
            row = col.row()
            row.prop(item, "is_selected", text=item.name)

    def execute(self, context):
        # 1. Setup & Object Validation
        target_obj = bpy.data.objects.get(self.source_name)
        donor_objs = [bpy.data.objects.get(s.name) for s in self.sources 
                      if s.is_selected and s.name != self.source_name]
        
        # We collect all affected armatures to clean up later
        affected_armatures = [target_obj] + [d for d in donor_objs if d]

        if not target_obj:
            self.report({'ERROR'}, "Base armature not found.")
            return {'CANCELLED'}
        
        if not donor_objs:
            self.report({'WARNING'}, "No donor armatures selected.")
            return {'CANCELLED'}

        # 2. Create the New Merged Armature
        merged_data = target_obj.data.copy()
        merged_obj = target_obj.copy()
        merged_obj.data = merged_data
        merged_obj.name = "Armature (Merged)"
        context.collection.objects.link(merged_obj)
        
        total_bones = 0
        total_meshes = 0

        # 3. Process the Target Armature (Merge bones and retarget meshes)
        for donor_obj in donor_objs:
            if not donor_obj: continue

            # Align target to source
            stitch_name = self.find_stitch_bone(donor_obj, target_obj)
            c_mat = self.get_correction_matrix(donor_obj, target_obj, stitch_name)

            # Merge bones
            b_data = self.get_edit_data(donor_obj, c_mat)
            total_bones += self.perform_merge(merged_obj, b_data)

            # Retarget the new meshes
            total_meshes += self.retarget_meshes(donor_obj, merged_obj, c_mat)

        # 4. Process the Base (Retarget the foundation's own meshes)
        # For the base meshes, the correction matrix is just Identity (no movement)
        total_meshes += self.retarget_meshes(target_obj, merged_obj, Matrix.Identity(4))

        # 5. SURGICAL CLEANUP (Remove the old rigs)
        # We delete the data-blocks as well to prevent ".001" clutter later
        for arm_obj in affected_armatures:
            arm_data = arm_obj.data
            bpy.data.objects.remove(arm_obj, do_unlink=True)
            if arm_data.users == 0:
                bpy.data.armatures.remove(arm_data)

        self.report({'INFO'}, f"Success! Merged {total_bones} bones and aligned {total_meshes} meshes into '{merged_obj.name}'.")
        return {'FINISHED'}

    # --- INTERNAL HELPERS ---
    def find_stitch_bone(self, source, target):
        for b in source.data.bones:
            if b.name in target.data.bones:
                curr, is_root = b.parent, True
                while curr:
                    if curr.name in target.data.bones:
                        is_root = False
                        break
                    curr = curr.parent
                if is_root: return b.name
        return None

    def get_correction_matrix(self, source, target, bone_name):
        if not bone_name: return Matrix.Identity(4)
        s_m = source.matrix_world @ source.data.bones[bone_name].matrix_local
        t_m = target.matrix_world @ target.data.bones[bone_name].matrix_local
        return t_m @ s_m.inverted()

    def get_edit_data(self, obj, c_mat):
        # Briefly enter Edit Mode on source to grab original bone data
        data = {}
        old_mode = obj.mode
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        for eb in obj.data.edit_bones:
            data[eb.name] = {
                'head': c_mat @ (obj.matrix_world @ eb.head),
                'tail': c_mat @ (obj.matrix_world @ eb.tail),
                'roll': eb.roll,
                'parent': eb.parent.name if eb.parent else None,
                'use_connect': eb.use_connect
            }
        bpy.ops.object.mode_set(mode=old_mode)
        return data

    def perform_merge(self, target, data):
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.mode_set(mode='EDIT')
        ebs = target.data.edit_bones
        added = []
        t_inv = target.matrix_world.inverted()

        for name, d in data.items():
            if name not in ebs:
                nb = ebs.new(name)
                nb.head, nb.tail = t_inv @ d['head'], t_inv @ d['tail']
                nb.roll, nb.use_connect = d['roll'], d['use_connect']
                added.append(name)
        
        for name in added:
            p = data[name]['parent']
            if p and p in ebs: ebs[name].parent = ebs[p]
            
        bpy.ops.object.mode_set(mode='OBJECT')
        return len(added)

    def retarget_meshes(self, source, target, c_mat):
        count = 0
        # Iterate over all meshes in the file
        for obj in bpy.data.objects:
            if obj.type != 'MESH': continue
            
            # Check if this mesh is parented to the source OR has a modifier pointing to it
            is_parented = (obj.parent == source)
            arm_mod = next((m for m in obj.modifiers if m.type == 'ARMATURE' and m.object == source), None)
            
            if is_parented or arm_mod:
                # Store world position
                w_mat = obj.matrix_world.copy()
                
                # Switch parent to the new rig
                obj.parent = target
                
                # Apply the correction (for base meshes, c_mat is Identity, so they stay put)
                obj.matrix_world = c_mat @ w_mat
                
                # Update all Armature modifiers on this mesh
                for m in obj.modifiers:
                    if m.type == 'ARMATURE' and (m.object == source or m.object is None):
                        m.object = target
                count += 1
        return count
    
# --------------------------------------------------------------------------------------------------------------

def enum_armatures(self, context):
    objs = (context.scene.objects if context else bpy.data.objects)
    return [(o.name, o.name, "") for o in objs if o.type == 'ARMATURE']

def matrices_equals(mat1, mat2, epsilon=0.0001):
    # Element-wise comparison
    for i in range(4):
        for j in range(4):
            if abs(mat1[i][j] - mat2[i][j]) >= epsilon:
                return False
    return True

class RetargetArmaturesOperator(bpy.types.Operator):
    """Retarget one armature's set of bones to another (Must share bone names and manually apply new transforms afterwards)"""
    bl_idname = "object.retarget_armatures"
    bl_label = "Retarget Armatures"
    bl_options = {'REGISTER', 'UNDO'}

    source_name: bpy.props.EnumProperty(
        name="Source Armature",
        description="Armature to copy pose from",
        items=enum_armatures,
    ) # type: ignore
    source_name: bpy.props.EnumProperty(
        name="Target Armature",
        description="Armature to paste pose onto",
        items=enum_armatures,
    ) # type: ignore
    threshold: bpy.props.FloatProperty(
        name="Retarget Threshold",
        default=0.0001,
        min=0.0,
        precision=6,
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        """Ensure at least one selected armature exists"""
        return context.selected_objects and len([o for o in context.selected_objects if o.type == 'ARMATURE'])

    def invoke(self, context, event):
        # If exactly two armatures are selected, prefill them
        arms = [o for o in context.selected_objects if o.type == 'ARMATURE']
        if len(arms) == 2:
            self.source_name = arms[0].name
            self.source_name = arms[1].name
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = True

        col = layout.column(align=True)
        col.prop(self, "source_name", text="Source Armature")
        col.prop(self, "source_name", text="Target Armature")

        col.separator()
        col.prop(self, "threshold", text="Threshold")

    def execute(self, context):
        src = bpy.data.objects.get(self.source_name)
        tgt = bpy.data.objects.get(self.source_name)

        if not src or not tgt:
            self.report({'ERROR'}, "Invalid source/target armature.")
            return {'CANCELLED'}
        if src.type != 'ARMATURE' or tgt.type != 'ARMATURE':
            self.report({'ERROR'}, "Both must be armatures.")
            return {'CANCELLED'}
        if src == tgt:
            self.report({'ERROR'}, "Source and Target Armatures must be different!")
            return {'CANCELLED'}

        # Switch to Pose Mode on target
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = tgt
        bpy.ops.object.mode_set(mode='POSE')

        matched = 0
        skipped = 0

        bpy.ops.pose.visual_transform_apply()

        for tgt_bone in tgt.pose.bones:
            name = tgt_bone.name
            src_bone = src.pose.bones.get(name)
            if not src_bone:
                continue

            # Compare world-space matrices
            src_matrix = src.matrix_world @ src_bone.matrix
            tgt_matrix = tgt.matrix_world @ tgt_bone.matrix
            if matrices_equals(src_matrix, tgt_matrix, self.threshold):
                skipped += 1
                continue

            # Add constraints
            loc = tgt_bone.constraints.new(type='COPY_LOCATION')
            loc.name = "Copy Location"
            loc.target = src
            loc.subtarget = name

            rot = tgt_bone.constraints.new(type='COPY_ROTATION')
            rot.name = "Copy Rotation"
            rot.target = src
            rot.subtarget = name
            rot.target_space = 'POSE'
            rot.owner_space = 'POSE'

            scl = tgt_bone.constraints.new(type='COPY_SCALE')
            scl.name = "Copy Scale"
            scl.target = src
            scl.subtarget = name

            matched += 1

        # Apply and bake pose transforms
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.visual_transform_apply()

        # Remove the temporary constraints
        for bone in tgt.pose.bones:
            for c in list(bone.constraints):
                if c.type in {'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE'}:
                    bone.constraints.remove(c)

        self.report({'INFO'}, f"Applied transforms to {matched} bones. Skipped {skipped} bones.")
        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------

class MakeCollectionPerMesh(bpy.types.Operator):
    """Makes a collection per mesh in your scene with the same name"""
    bl_idname = "object.make_collection_per_mesh"
    bl_label = "Make Collection Per Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # Filter selection to only meshes to avoid logic errors with lights/cameras
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        # Track counts for the report at the end
        created_count = 0
        
        for obj in mesh_objects:
            col_name = obj.name
            
            # Check if a collection with this name already exists, if it does then we'll use it; otherwise we'll create a new one
            new_col = bpy.data.collections.get(col_name)
            if not new_col:
                new_col = bpy.data.collections.new(col_name)
                # Link the new collection to the scene's master collection (Scene Collection)
                context.scene.collection.children.link(new_col)
                created_count += 1
            
            # An object can be in multiple collections. To move it we link it to the new one and unlink it from all others.
            if obj.name not in new_col.objects:
                new_col.objects.link(obj)
            
            # Unlink from all other collections in the current scene
            for col in obj.users_collection:
                if col != new_col:
                    col.objects.unlink(obj)
        
        self.report({'INFO'}, f"Processed {len(mesh_objects)} objects. Created {created_count} new collections.")
        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------

class BatchAddMaterialsOperator(bpy.types.Operator):
    """Create a unique material with nodes for each selected object"""
    bl_idname = "object.batch_add_material"
    bl_label = "Batch Add Materials to Objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            # Only process objects that can actually hold materials (Meshes, Curves, etc.)
            if obj.type not in {'MESH', 'CURVE', 'SURFACE', 'METABALL', 'FONT'}:
                continue

            # 1. Create a new material named after the object
            mat_name = f"M_{obj.name}"
            new_mat = bpy.data.materials.new(name=mat_name)
            
            # 2. Enable Nodes
            new_mat.use_nodes = True
            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links
            nodes.clear()

            # 3. Create a basic node setup: Principled BSDF -> Output
            node_output = nodes.new(type='ShaderNodeOutputMaterial')
            node_output.location = (300, 0)

            node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
            node_principled.location = (0, 0)
            
            # Example: Assign a random color so you can visually see they are unique
            import random
            node_principled.inputs['Base Color'].default_value = (
                random.random(), 
                random.random(), 
                random.random(), 
                1.0
            )

            # 5. Link them
            links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

            # 6. Assign to object
            if obj.data.materials:
                # Replace the first slot if it exists
                obj.data.materials[0] = new_mat
            else:
                # Append if no slots exist
                obj.data.materials.append(new_mat)

        self.report({'INFO'}, f"Created {len(selected_objects)} unique materials.")
        return {'FINISHED'}
    
# --------------------------------------------------------------------------------------------------------------

# 1. Define your data in a clean dictionary
SHAPEKEY_PRESETS = {
# Apple ARKit Shape Key List
'APPLE_ARKIT': [
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
    "cheekPuff", "cheekSquintLeft", "cheekSquintRight", "eyeBlinkLeft", "eyeBlinkRight",
    "eyeLookDownLeft", "eyeLookDownRight", "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft",
    "eyeLookOutRight", "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
    "eyeWideLeft", "eyeWideRight", "jawForward", "jawLeft", "jawRight", "jawOpen",
    "mouthClose", "mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft", "mouthFrownRight",
    "mouthFunnel", "mouthLeft", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthPressLeft",
    "mouthPressRight", "mouthPucker", "mouthRight", "mouthRollLower", "mouthRollUpper",
    "mouthShrugLower", "mouthShrugUpper", "mouthSmileLeft", "mouthSmileRight", "mouthStretchLeft",
    "mouthStretchRight", "mouthUpperUpLeft", "mouthUpperUpRight", "noseSneerLeft", "noseSneerRight", "tongueOut"
],
}

class BatchAddEmptyShapeKeysOperator(bpy.types.Operator):
    """Add a batch of empty shape keys to selected objects"""
    bl_idname = "object.batch_add_empty_shapekeys"
    bl_label = "Add Batch Empty Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    # The Dropdown Property
    preset_type: bpy.props.EnumProperty(
        name="Shape Key Preset Set",
        items=[(key, key.replace('_', ' ').title(), f"Add {key} shapes") for key in SHAPEKEY_PRESETS.keys()],
        default='APPLE_ARKIT'
    ) # type: ignore

    def execute(self, context):
        selected = context.selected_objects
        if not selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        # Determine which list to use
        shape_list = SHAPEKEY_PRESETS.get(self.preset_type, [])
        
        if not shape_list:
            self.report({'ERROR'}, f"Preset {self.preset_type} not found.")
            return {'CANCELLED'}
        count_added = 0

        for obj in selected:
            if obj.type != 'MESH':
                continue
            
            # 1. Ensure Basis exists first
            if not obj.data.shape_keys:
                obj.shape_key_add(name="Basis")
            
            existing_keys = obj.data.shape_keys.key_blocks.keys()

            # 2. Add the shapes from the list
            for name in shape_list:
                if name not in existing_keys:
                    obj.shape_key_add(name=name)
                    count_added += 1

        self.report({'INFO'}, f"Added {count_added} empty shape keys across {len(selected)} objects.")
        return {'FINISHED'}

    def invoke(self, context, event):
        # This opens the small popup dialog to choose the preset
        return context.window_manager.invoke_props_dialog(self)
    
# --------------------------------------------------------------------------------------------------------------

class BatchCubicInterpolationConverterOperator(bpy.types.Operator):
    """Blender 4.5 and higher: Set all image textures in selected objects to Cubic interpolation"""
    bl_idname = "material.batch_cubic_interp_convert"
    bl_label = "Convert Textures' Interpolation to Cubic"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Basic poll: Must be in Object Mode and have at least one mesh selected
        return context.active_object is not None and context.active_object.type == 'MESH'

    def has_textures(self, obj):
        """Check if object has a material with at least one texture"""
        if not obj.material_slots:
            return False
            
        for slot in obj.material_slots:
            mat = slot.material
            if mat and mat.use_nodes:
                # Check if any node is an Image Texture
                if any(n.type == 'TEX_IMAGE' for n in mat.node_tree.nodes):
                    return True
        return False

    def execute(self, context):
        # 1. Filter selection for meshes that actually have materials and textures
        valid_objects = [o for o in context.selected_objects 
                         if o.type == 'MESH' and self.has_textures(o)]
            
        if not valid_objects:
            self.report({'WARNING'}, "No selected meshes have materials with image textures")
            return {'CANCELLED'}

        processed_materials = set()
        nodes_changed = 0

        # 2. Process only the valid objects
        for obj in valid_objects:
            for slot in obj.material_slots:
                mat = slot.material
                    
                if not mat or not mat.use_nodes or mat in processed_materials:
                    continue
                    
                # Update interpolation on all image texture nodes
                tex_nodes = [n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE']
                for node in tex_nodes:
                    node.interpolation = 'Cubic'
                    nodes_changed += 1
                    
                processed_materials.add(mat)

        self.report({'INFO'}, f"Set {nodes_changed} texture nodes to Cubic across {len(processed_materials)} materials.")
        return {'FINISHED'}

# --------------------------------------------------------------------------------------------------------------

classes = [
    DodyPanel,

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
    BatchAddVertexColorOperator,
    ProjectShapeKeyToVertexColorOperator,
    ProjectVertexColorToShapeKeyOperator,
    ConvertTrisToQuadsOperator,

    ArmatureMergeItem,
    MergeArmaturesOperator,
    RetargetArmaturesOperator,

    MakeCollectionPerMesh,
    BatchAddMaterialsOperator,
    BatchAddEmptyShapeKeysOperator,

    BatchCubicInterpolationConverterOperator,
]

# --------------------------------------------------------------------------------------------------------------