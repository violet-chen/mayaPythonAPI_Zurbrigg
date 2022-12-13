# coding: utf-8
# 不适用于2018及以下版本
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr

import maya.cmds as cmds


def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass


class DistanceBetweenLocator(omui.MPxLocatorNode):
    TYPE_NAME = "distanceBetweenLocator"
    TYPE_ID = om.MTypeId(0x0007F7FD)
    DRAW_CLASSIFICATION = "drawdb/geometry/distancebetweenlocator"
    DRAW_REGISTRANT_ID = "DistanceBetweenLocator"

    def __init__(self):
        super(DistanceBetweenLocator, self).__init__()

    @classmethod
    def creator(cls):
        return DistanceBetweenLocator()

    @classmethod
    def initialize(cls):
        pass

class DistanceBetweenUserData(om.MUserData):

    def __init(self, deleteAfterUse = False):
        super(DistanceBetweenUserData, self).__init__(deleteAfterUse)

        self.distance = 0

class DistanceBetweenDrawOverride(omr.MPxDrawOverride):
    """ 负责在视口中绘制几何图形 """
    NAME = "DistanceBetweenDrawOverride"

    def __init__(self, obj):
        super(DistanceBetweenDrawOverride, self).__init__(obj, None, False) # 第一个参数是maya object,第二个参数是绘制是callback函数,第三个参数是默认为True,为True时将会将此标志位dirty状态，因此可以持续更新,建议为True,除非遇到了性能问题可以为False

    def supportedDrawAPIs(self):
        """ 让maya知道支持哪个图形api,kAllDevices指的是使用OpenGL and Direct X 11"""
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        """ 表示使用addUIDrawables方法来绘制图形 """
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        """ 在使用绘制图形的方法之前,使用这个方法来将数据检索与缓存 """
        data = old_data
        if not data:
            data = DistanceBetweenUserData()

        data.distance = "??????"
        
        return data

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        """ 绘制图形的方法

        Args:
            obj_path (_type_): 指向正在绘制的对象的路径,这里是指locator节点
            draw_manager (_type_): 用于绘制简单的几何图形
            frame_context (_type_): 包含当前渲染框架的一些全局信息
            data (_type_): 用户创建的数据对象,存储缓存数据
        """
        draw_manager.beginDrawable()
        
        draw_manager.setFontSize(20)
        draw_manager.setFontWeight(100)
        draw_manager.text2d(om.MPoint(100, 100), "Distance: {0}".format(data.distance))

        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return DistanceBetweenDrawOverride(obj)


def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    try:
        plugin_fn.registerNode(DistanceBetweenLocator.TYPE_NAME,
                               DistanceBetweenLocator.TYPE_ID,
                               DistanceBetweenLocator.creator,
                               DistanceBetweenLocator.initialize,
                               om.MPxNode.kLocatorNode,
                               DistanceBetweenLocator.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(DistanceBetweenLocator.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(DistanceBetweenLocator.DRAW_CLASSIFICATION,
                                                      DistanceBetweenLocator.DRAW_REGISTRANT_ID,
                                                      DistanceBetweenDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(DistanceBetweenDrawOverride.NAME))


def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(DistanceBetweenLocator.DRAW_CLASSIFICATION,
                                                        DistanceBetweenLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(DistanceBetweenDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(DistanceBetweenLocator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(DistanceBetweenLocator.TYPE_NAME))

def rc_distance_between_test():
    cmds.setAttr("persp.translate", 3.5, 5.5, 10.0)
    cmds.setAttr("persp.rotate", -27.0, 19.0, 0.0)

    cube1 = cmds.polyCube()[0]
    cube2 = cmds.polyCube()[0]

    cmds.setAttr("{0}.translateX".format(cube1), -2.5)
    cmds.setAttr("{0}.translateX".format(cube2), 2.5)

    distance_locator = cmds.createNode("{0}".format(DistanceBetweenLocator.TYPE_NAME))
    cmds.select(distance_locator)


if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    plugin_name = "distance_between_locator.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('rc_distance_between_test()')
