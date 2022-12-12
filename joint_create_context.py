# coding: utf-8
# 此插件只适用于maya2020及以上版本
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds
import os

def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass

class JointCreateContext(omui.MPxContext):

    TITLE = "JointCreate Context"

    HELP_TEXT = ["Select first joint location",
                 "Select second joint location",
                 "Select final joint location",
                 "Press Enter to complete"]

    def __init__(self):
        super(JointCreateContext, self).__init__()

        self.setTitleString(JointCreateContext.TITLE)
        plugin_dir_path = os.path.dirname(cmds.pluginInfo("joint_create_context.py",p=True,q=True))  
        self.setImage(plugin_dir_path + "/icons/icon_windows.png", omui.MPxContext.kImage1) # 设置工具的图标

        self.state = 0 # 判断通过工具选择的对象的个数
        self.context_selection = om.MSelectionList() # 通过工具选择的对象的列表
    
    def helpStateHasChanged(self, event):
        self.update_help_string()
    
    def update_help_string(self):
        self.setHelpString(JointCreateContext.HELP_TEXT[self.state])

    def toolOnSetup(self, event):
        """ 工具加载时执行 """
        om.MGlobal.selectCommand(om.MSelectionList()) # 确保工具刚开始使用时是一个健康的选择状态
        self.reset_state()

    def toolOffCleanup(self):
        """ 取消工具加载时执行(在使用工具的同时创建模型maya会自动先取消加载工具再自动加载工具) """
        self.reset_state()
    
    def doRelease(self, event, draw_manager, frame_context):
        """ 松开键时执行 """
        if self.state >= 0 and self.state < 3:
            om.MGlobal.selectFromScreen(event.position[0], event.position[1],event.position[0],event.position[1],om.MGlobal.kReplaceList)

            active_selection = om.MGlobal.getActiveSelectionList()
            if active_selection.length() == 1:
                self.context_selection.merge(active_selection) # 使用merge方法防止重复的对象出现在context_selection中

            om.MGlobal.setActiveSelectionList(self.context_selection) # 更改当前选择的物体

            self.update_state
    
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

    def update_state(self):
        """ 更新状态 """
        self.state = self.context_selection.length()

        self.update_help_string()
    
    def reset_state(self):
        """ 重置状态 """
        om.MGlobal.setActiveSelectionList(om.MSelectionList())

        self.context_selection.clear()
        self.update_state

class JointCreateContextCmd(omui.MPxContextCommand):

        COMMAND_NAME = "rcJointCreateCtx"

        def __init__(self):
            super(JointCreateContextCmd, self).__init__()
        
        def makeObj(self):
            return JointCreateContext()
        
        @classmethod
        def creator(cls):
            return JointCreateContextCmd()

def initializePlugin(plugin): 
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    try:
        plugin_fn.registerContextCommand(JointCreateContextCmd.COMMAND_NAME, JointCreateContextCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register context command: {0}".format(JointCreateContextCmd.COMMAND_NAME))

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterContextCommand(JointCreateContextCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister context command: {0}".format(JointCreateContextCmd.COMMAND_NAME))

if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    cmds.file(new=True,force=True)

    plugin_name = "joint_create_context.py"  # 插件的文件名

    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('context = cmds.rcJointCreateCtx(); cmds.setToolTo(context)')
