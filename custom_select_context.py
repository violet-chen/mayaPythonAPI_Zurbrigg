# coding: utf-8
# 此插件只适用于maya2020及以上版本
# 插件介绍: 使用context时按ctrl键框选只选择mesh,按ctrl+shift键时只选择light，不按只框选就全选择
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds
import os

def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass

class CustomSelectContext(omui.MPxContext):

    TITLE = "Custom Select Context"

    HELP_TEXT = "Ctrl to select only meshes. Ctrl+Shift to select only lights."

    def __init__(self):
        super(CustomSelectContext, self).__init__()

        self.setTitleString(CustomSelectContext.TITLE)
        plugin_dir_path = os.path.dirname(cmds.pluginInfo("custom_select_context.py",p=True,q=True))  
        self.setImage(plugin_dir_path + "/icons/icon_windows.png", omui.MPxContext.kImage1) # 设置工具的图标
        test_file_path = plugin_dir_path + "/test_scene/custom_select_context_test.ma"
    
    def helpStateHasChanged(self, event):
        """ 在左下角显示帮助 """
        self.setHelpString(CustomSelectContext.HELP_TEXT)

    def toolOnSetup(self, event):
        """ 工具加载时执行 """
        print("toolOnSetup")

    def toolOffCleanup(self):
        """ 取消工具加载时执行(在使用工具的同时创建模型maya会自动先取消加载工具再自动加载工具) """
        print("toolOffCleanup")
    
    def doPress(self, event, draw_manager, frame_context):
        """ 按下键时执行 """
        self.viewport_start_pos = event.position

        self.light_only = False # 用来判断是否只选择灯光类型
        self.meshes_only = False # 用来判断是否只选择mesh类型

        if event.isModifierControl():
            if event.isModifierShift():
                self.light_only = True  # 当ctrl和shift键同时按下时为True
            else:
                self.meshes_only = True  # 当ctrl键按下时为True
            
    def doRelease(self, event, draw_manager, frame_context):
        """ 松开键时执行 """
        self.viewport_end_pos = event.position

        initial_selection = om.MGlobal.getActiveSelectionList() # 获取场景中已经选择的对象的列表

        om.MGlobal.selectFromScreen(self.viewport_start_pos[0], self.viewport_start_pos[1],
                                    self.viewport_end_pos[0], self.viewport_end_pos[1],
                                    om.MGlobal.kReplaceList) # 根据矩形框选择矩形中的对象（这个命令所进行的选择不会进入undo堆栈，因此需要通过其他命令设置正常的堆栈）
        
        selection_list = om.MGlobal.getActiveSelectionList() # 获取通过矩形框选中的对象的列表

        if self.light_only or self.meshes_only:
            for i in reversed(range(selection_list.length())):
                obj = selection_list.getDependNode(i)
                shape = om.MFnDagNode(obj).child(0)

                if self.light_only and not shape.hasFn(om.MFn.kLight): # 如果shape节点是light类型
                    selection_list.remove(i)
                elif self.meshes_only and not shape.hasFn(om.MFn.kMesh): # 如果shape节点是mesh类型
                    selection_list.remove(i)

        om.MGlobal.setActiveSelectionList(initial_selection, om.MGlobal.kReplaceList) # 首先选择场景中之前已经选择的列表
        om.MGlobal.selectCommand(selection_list, om.MGlobal.kReplaceList)  # 通过调用内置的maya选择命令来选择，并且让maya负责维护堆栈
    
    def doDrag(self, event, draw_manager, frame_context):
        """ 按住鼠标左键并进行移动时执行 """
        self.viewport_end_pos = event.position

        self.draw_selection_rectangle(draw_manager,
                                      self.viewport_start_pos[0],self.viewport_start_pos[1],
                                      self.viewport_end_pos[0],self.viewport_start_pos[1],
                                      self.viewport_end_pos[0],self.viewport_end_pos[1],
                                      self.viewport_start_pos[0],self.viewport_end_pos[1])

    def draw_selection_rectangle(self, draw_manager, x0, y0, x1, y1, x2, y2, x3, y3):
        """ 根据鼠标拖拽的范围进行矩形绘制 """
        draw_manager.beginDrawable() # 开始绘制
        draw_manager.setLineWidth(1.0) # 设置绘制线的宽度
        draw_manager.setColor(om.MColor((1.0, 0.0, 0.0))) # 设置绘制的颜色（颜色数值是一个集合）

        draw_manager.line2d(om.MPoint(x0,y0),om.MPoint(x1,y1))
        draw_manager.line2d(om.MPoint(x1,y1),om.MPoint(x2,y2))
        draw_manager.line2d(om.MPoint(x2,y2),om.MPoint(x3,y3))
        draw_manager.line2d(om.MPoint(x3,y3),om.MPoint(x0,y0))

        draw_manager.endDrawable() # 结束绘制


class CustomSelectContextCmd(omui.MPxContextCommand):

        COMMAND_NAME = "rcCustomSelectCtx"

        def __init__(self):
            super(CustomSelectContextCmd, self).__init__()
        
        def makeObj(self):
            return CustomSelectContext()
        
        @classmethod
        def creator(cls):
            return CustomSelectContextCmd()

def initializePlugin(plugin): 
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    try:
        plugin_fn.registerContextCommand(CustomSelectContextCmd.COMMAND_NAME, CustomSelectContextCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register context command: {0}".format(CustomSelectContextCmd.COMMAND_NAME))

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterContextCommand(CustomSelectContextCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister context command: {0}".format(CustomSelectContextCmd.COMMAND_NAME))

if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    cmds.file(new=True,force=True)

    plugin_dir_path = os.path.dirname(cmds.pluginInfo("custom_select_context.py",p=True,q=True)) 
    test_file_path = plugin_dir_path + "/test_scene/custom_select_context_test.ma"

    plugin_name = "custom_select_context.py"  # 插件的文件名

    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('cmds.file(test_file_path,o=True,f=True)')
    cmds.evalDeferred('context = cmds.rcCustomSelectCtx(); cmds.setToolTo(context)')
