bl_info = {
    "name": "Push Down All",
    "author": "Cory Petkovsek",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Dope Sheet > Action Editor > Sidebar > Push Down All",
    "description": "Automatically 'Pushes Down' all matching animations to NLA tracks.",
    "warning": "",
    "doc_url": "https://github.com/tinmanjuggernaut/blender-pushdownall",
    "tracker_url": "https://github.com/tinmanjuggernaut/blender-pushdownall/issues",
    "category": "Animation",
}

import bpy
import re


PROPERTIES = [
    ('pda_exclude',  bpy.props.StringProperty(name = "Exclude", default="")),
    ('pda_search',  bpy.props.StringProperty(name = "Search", default="")),
    ('pda_replace', bpy.props.StringProperty(name = "Replace", default="")),
]


class List:
  def __init__(self, name='List', data=[]):
    self.name = name
    self.data = data
    
    
class PushDownAllOperator(bpy.types.Operator):
    """Start processing"""
    bl_label = "Push Down All"
    bl_idname = "action.push_down_all"    

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.area.type = 'DOPESHEET_EDITOR'
        
        if context.scene.pda_search:
            print("Search query: ", context.scene.pda_search)
            print("Replace string: ", context.scene.pda_replace)

        for action in context.scene.animations.data:
            if context.scene.pda_search:
                (new_name, count) = re.subn(context.scene.pda_search, context.scene.pda_replace, action.name)
                if count > 0:
                    print("Renaming: " + action.name + " -> " + new_name )
                    action.name = new_name
            
            print("Pushing down: ", action.name)
            bpy.context.active_object.animation_data.action = action
            bpy.context.space_data.ui_mode = 'ACTION'
            bpy.ops.action.push_down()

        print("Pushed down %d animations." % len(context.scene.animations.data) )
            
        return {'FINISHED'}


class PushDownAllPanel(bpy.types.Panel):
    bl_label = "Push Down All"
    bl_idname = "ACTION_PT_PushDownAll"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        context.scene.animations.data.clear()
        layout = self.layout
        ex = re.compile('')     # Predefine re.Pattern type variables
        sr = ex
        count = 0

        ## Header
        
        row = layout.row()
        row.label(text = "Creates NLA tracks for all animations.")
        
        if not ( hasattr(bpy.context.active_object, "animation_data") and \
                 hasattr(bpy.context.active_object.animation_data, "action") ):
            box = layout.box()
            row = box.row()
            row.label(text = "Select object with animation data,")
            row = box.row()
            row.label(text = "then select any animation.")
            row = box.row()
            return

        row = layout.row()
        row.label(text = "Enter regular expressions:")

        ## Exclude

        box = layout.box()
        row = box.row()
        row.prop(context.scene, "pda_exclude")
                
        if context.scene.pda_exclude:
            try:
                ex = re.compile(context.scene.pda_exclude)
            except:
                ex_status = "Error: Invalid regex"
                row = box.row()
                row.label(text = ex_status)
                return

        for action in bpy.data.actions:
            if context.scene.pda_exclude and ex.search(action.name):
                count += 1
            else:
                context.scene.animations.data.append(action)

        if count>0:
            row = box.row()
            row.label(text = "Skipping %d animations" % count)

        row = box.row()
        row.label(text = "Will push down %d animations" % len(context.scene.animations.data))
        row = box.row()
        row = layout.row()

        ## Search & Replace

        box = layout.box()
        row = box.row()
        row.prop(context.scene, "pda_search")
        
        if context.scene.pda_search:
            try:
                sr = re.compile(context.scene.pda_search)
            except:
                sr_status = "Error: Invalid regex"         
                row = box.row()
                row.label(text = sr_status)
                return
                
        row = box.row()
        row.prop(context.scene, "pda_replace")

        if context.scene.pda_search:
            count = 0
            for action in context.scene.animations.data:
                if sr.search(action.name):
                    count += 1
            row = box.row()
            row.label(text = "Will rename %d animations" % count)
        row = box.row()

        ## Push Down Button
        
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.operator("action.push_down_all", icon = "NLA_PUSHDOWN")


def register():
    for (prop_name, prop_value) in PROPERTIES:
        setattr(bpy.types.Scene, prop_name, prop_value)
    
    bpy.types.Scene.animations = List()
    bpy.utils.register_class(PushDownAllPanel)
    bpy.utils.register_class(PushDownAllOperator)


def unregister():
    for (prop_name, _) in PROPERTIES:
        delattr(bpy.types.Scene, prop_name)

    del bpy.types.Scene.animations

    bpy.utils.unregister_class(PushDownAllPanel)
    bpy.utils.unregister_class(PushDownAllOperator)


if __name__ == "__main__":
    register()
