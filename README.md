# io_dody_shortcuts
### A simple [Blender 3.X/4.X+](https://blender.org) plugin I've written to quickly do some functions while modding, saves a lot of clicks.

# Features
- Dedicated Sidebar menu to house all the functions the plugin has, Usage is easy and self-explanatory.
- Most functions work in bulk *(will be marked with an asterisk)* and report relevant information to the user.
- Context Aware: They wouldn't work if the selected object isn't a mesh or lacks the data required to execute the functions.

# Functions
### Removers
- Remove Vertex Groups*
- Remove Unused Vertex Groups* *(Only empty VGs will be deleted)*
- Remove Modifiers*
- Remove Vertex Colors*
- Remove Shape Keys*
- Remove Unused Shape Keys*
- Remove UV Maps*
- Remove Materials*
- Remove Unused Materials*

### Utilities
- Check Mesh Shape Key Count
- Flip UV Maps Horizontally and Vertically*
- Project Shape Key to Vertex Color and Vertex Color to Shape Key
- Batch Convert Mesh Tris to Quads*
- Merge Armatures*
- Retarget Armatures
- Make Collections Per Meshes*
- Batch Convert Texture Interpolations to Cubic* *(Blender 4.5 and higher only!)*
- Apply All Modifiers (with option to whether apply or not apply Armature modifiers)

### Adders
- Add Vertex Colors*
- Add Materials*
- Add Empty Shape Keys* *(From an existing set, For example Apple ARKit)*

# Installation Instructions
1. Grab the latest release from the Releases page or download the repository's code as a ZIP file.
2. Go to your Blender's Preferences menu > Add-ons > Install and Navigate to where you've downloaded said release/repo code archive then select it for install, Once done; tick it and you should be ready to go!
