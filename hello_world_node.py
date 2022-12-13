# coding: utf-8
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr

import maya.cmds as cmds


def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass


class HelloWorldNode(omui.MPxLocatorNode):
    TYPE_NAME = "helloworld"
    TYPE_ID = om.MTypeId(0x0007f7f7)
    DRAW_CLASSIFICATION = "drawdb/geometry/helloworld"
    DRAW_REGISTRANT_ID = "HelloWorldNode"

    def __init__(self):
        super(HelloWorldNode, self).__init__()

    @classmethod
    def creator(cls):
        return HelloWorldNode()

    @classmethod
    def initialize(cls):
        pass


class HelloWorldDrawOverride(omr.MPxDrawOverride):
    """ 负责在视口中绘制几何图形 """
    NAME = "HelloWorldDrawOverride"

    def __init__(self, obj):
        super(HelloWorldDrawOverride, self).__init__(obj, None, False) # 第一个参数是maya object,第二个参数是绘制是callback函数,第三个参数是默认为True,为True时将会将此标志位dirty状态，因此可以持续更新,建议为True,除非遇到了性能问题可以为False

    def supportedDrawAPIs(self):
        """ 让maya知道支持哪个图形api,kAllDevices指的是使用OpenGL and Direct X 11"""
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        """ 表示使用addUIDrawables方法来绘制图形 """
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        """ 在使用绘制图形的方法之前,使用这个方法来将数据检索与缓存 """
        pass

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        """ 绘制图形的方法

        Args:
            obj_path (_type_): 指向正在绘制的对象的路径,这里是指locator节点
            draw_manager (_type_): 用于绘制简单的几何图形
            frame_context (_type_): 包含当前渲染框架的一些全局信息
            data (_type_): 用户创建的数据对象,存储缓存数据
        """
        draw_manager.beginDrawable()
        draw_manager.text2d(om.MPoint(100, 100), "Hello World")
        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return HelloWorldDrawOverride(obj)


def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    try:
        plugin_fn.registerNode(HelloWorldNode.TYPE_NAME,
                               HelloWorldNode.TYPE_ID,
                               HelloWorldNode.creator,
                               HelloWorldNode.initialize,
                               om.MPxNode.kLocatorNode,
                               HelloWorldNode.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(HelloWorldNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,
                                                      HelloWorldNode.DRAW_REGISTRANT_ID,
                                                      HelloWorldDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(HelloWorldDrawOverride.NAME))


def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,
                                                        HelloWorldNode.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(HelloWorldDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(HelloWorldNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(HelloWorldNode.TYPE_NAME))


if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    plugin_name = "hello_world_node.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name)) # 在main函数中需要通过cmds.evalDeferred包装确保一行一行的执行
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("helloworld")')
