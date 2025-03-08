# --------
# IMPORTS
# --------

import bpy
import numpy as np
import mathutils

# -------------------
# PLUGIN INFORMATION
# -------------------

bl_info = {
    "name": "Dody's Shortcuts",
    "author": "Dodylectable",
    "version": (1, 0, 4),
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

        # =============
        # THE REMOVERS
        # =============

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
        row.operator("object.add_custom_vertex_color", text="Quickly Add Custom Vertex Colors")

        row = layout.row()
        row.operator("object.project_key_to_color", text="Project Shape Key to Vertex Color")

        row = layout.row()
        row.operator("object.project_color_to_key", text="Project Vertex Color to Shape Key")

        row = layout.row()
        row.operator("object.batch_tris_to_quads", text="Batch Convert Tris to Quads")

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
        vertex_colors = {i: mathutils.Vector((0, 0, 0)) for i in range(len(mesh.vertices))}
        vertex_counts = {i: 0 for i in range(len(mesh.vertices))}

        # Loop through loops to collect vertex color data
        color_data = vcol_layer.data
        for loop in mesh.loops:
            vert_index = loop.vertex_index
            color = color_data[loop.index].color  # Get (R, G, B, A)

            # Convert RGB to displacement offset
            offset = mathutils.Vector((color[0] - 0.5, color[1] - 0.5, color[2] - 0.5))

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
    ProjectShapeKeyToVertexColorOperator,
    ProjectVertexColorToShapeKeyOperator,
    ConvertTrisToQuadsOperator,
]