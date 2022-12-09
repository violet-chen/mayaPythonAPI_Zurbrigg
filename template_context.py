# coding: utf-8
# 此插件只适用于maya2020及以上版本
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds
import os

def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass

class SimpleContext(omui.MPxContext):

    TITLE = "Simple Context"

    HELP_TEXT = "<insert help text here>"

    def __init__(self):
        super(SimpleContext, self).__init__()

        self.setTitleString(SimpleContext.TITLE)
        plugin_dir_path = os.path.dirname(cmds.pluginInfo("template_context.py",p=True,q=True))  
        self.setImage(plugin_dir_path + "/icons/icon_windows.png", omui.MPxContext.kImage1) # 设置工具的图标
    
    def helpSlateHasChanged(self, event):
        self.setHelpString(SimpleContext.HELP_TEXT)

    def toolOnSetup(self, event):
        """ 工具加载时执行 """
        print("toolOnSetup")

    def toolOffCleanup(self):
        """ 取消工具加载时执行(在使用工具的同时创建模型maya会自动先取消加载工具再自动加载工具) """
        print("toolOffCleanup")
    
    def doPress(self, event, draw_manager, frame_context):
        """ 按下键时执行 """
        mouse_button = event.mouseButton()  # 获取鼠标的按键

        if mouse_button == omui.MEvent.kLeftMouse:
            # 如果按下鼠标左键执行
            print("Left mouse button pressed") 
        elif mouse_button == omui.MEvent.kMiddleMouse:
            # 如果按下鼠标中键执行
            print("Middle mouse button pressed")
    
    def doRelease(self, event, draw_manager, frame_context):
        """ 松开键时执行 """
        print("Mouse button released")
    
    def doDrag(self, event, draw_manager, frame_context):
        """ 按住鼠标左键并进行移动时执行 """
        print("Mouse drag")
    
    def completeAction(self):
        """ 按下enter键时执行 """
        print("Complete action (enter/return key pressed)")
    
    def deleteAction(self):
        """ 按下delete键或者backspace键时执行 """
        print("Delete action (backspace/delete key pressed)")
    
    def abortAction(self):
        """ 按下esc键时执行 """
        print("Abort action (escape key pressed)")

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
