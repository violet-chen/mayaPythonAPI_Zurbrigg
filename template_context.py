# coding: utf-8
# 此插件只适用于maya2020及以上版本
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds
import os.path

def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass

class SimpleContext(omui.MPxContext):

    TITLE = "Simple Context"

    HELP_TEXT = "<insert help text here>"

    def __init__(self):
        super(SimpleContext, self).__init__()

        self.setTitleString(SimpleContext.TITLE)
        file_path = os.path.abspath(__file__).replace("\\", "/")
        self.setImage(file_path + "/icons/icon_windows.png", omui.MPxContext.kImage1) # 34*34像素
    
    def helpSlateHasChanged(self, event):
        self.setHelpString(SimpleContext.HELP_TEXT)

    def toolOnSetup(self, event):
        print("toolOnSetup")

    def toolOffCleanup(self):
        print("toolOffCleanup")
    
    def doPress(self, event, draw_manager, frame_context):
        mouse_button = event.mouseButton()

        if mouse_button == omui.MEvent.kLeftMouse:
            print("Left mouse button pressed")
        elif mouse_button == omui.MEvent.kMiddleMouse:
            print("Middle mouse button pressed")
    
    def doRelease(self, event, draw_manager, frame_context):
        print("Mouse button released")
    
    def doDrag(self, event, draw_manager, frame_context):
        print("Mouse drag")
    
    def compleateAction(self):
        print("Complete action (enter/return key pressed)")

class SimpleContextCmd(omui.MPxContextCommand):

        COMMAND_NAME = "rcSimpleCtx"

        def __init__(self):
            super(SimpleContextCmd, self).__init__()
        
        def makeObj(self):
            return SimpleContext()
        
        @classmethod
        def creator(cls):
            return SimpleContextCmd()

def initializePlugin(plugin): 
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    try:
        plugin_fn.registerContextCommand(SimpleContextCmd.COMMAND_NAME, SimpleContextCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register context command: {0}".format(SimpleContextCmd.COMMAND_NAME))

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterContextCommand(SimpleContextCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister context command: {0}".format(SimpleContextCmd.COMMAND_NAME))

if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    cmds.file(new=True,force=True)

    plugin_name = "template_context.py"  # 插件的文件名

    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('context = cmds.rcSimpleCtx(); cmds.setToolTo(context)')
