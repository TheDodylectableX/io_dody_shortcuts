# io_dody_shortcuts
### A simple [Blender 3.X/4.X+](https://blender.org) plugin I've written to quickly do some functions while modding, saves a lot of clicks.

# Features
- Dedicated Sidebar menu to house all the functions the plugin has
- Most functions work in bulk and report to the user specific information
- Context aware; They wouldn't work if the selected object isn't a mesh or lacks the data required to execute the functions

# Functions
### Removers
- Remove Vertex Groups
- Remove Modifiers
- Remove Shape Keys
- Remove UV Maps
- Remove Materials
- Remove Unused Vertex Groups *(Weights below 0.100 won't be deleted)*

### Utilities
- Check Shape Key Count
- Flip UV Maps Horizontally and Vertically (Works in batch)
- Quickly Add Custom Vertex Colors (Works in batch)
- Project Shape Key to Vertex Color and Vertex Color to Shape Key
- Batch Convert Tris to Quads

# Installation Instructions
1. Grab the latest release from the Releases page or download the repository's code as a ZIP file.
2. Go to your Blender's Preferences menu > Add-ons > Install and Navigate to where you've downloaded said release/repo code archive then select it for install, Once done; tick it and you should be ready to go!
