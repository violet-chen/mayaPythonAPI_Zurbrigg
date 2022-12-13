# coding: utf-8
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr

import maya.cmds as cmds


def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass


class SimpleLocatorNode(omui.MPxLocatorNode):
    TYPE_NAME = "simplelocator"
    TYPE_ID = om.MTypeId(0x0007F7FE)
    DRAW_CLASSIFICATION = "drawdb/geometry/simplelocator"
    DRAW_REGISTRANT_ID = "SimpleLocatorNode"

    def __init__(self):
        super(SimpleLocatorNode, self).__init__()

    @classmethod
    def creator(cls):
        return SimpleLocatorNode()

    @classmethod
    def initialize(cls):
        numeric_attr = om.MFnNumericAttribute()

        cls.shape_index_obj = numeric_attr.create("shapeIndex", "si", om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(0)
        numeric_attr.setMax(2)

        cls.addAttribute(cls.shape_index_obj)

class SimpleLocatorUserData(om.MUserData):
    """ 创建MUserData类使其对象能够将数据在prepareForDraw与addUIDrawables之间相互传递  """
    def __init(self, deleteAfterUse = False):  # 设置为使用数据后不删除数据
        super(SimpleLocatorUserData, self).__init__(deleteAfterUse)

        self.shape_index = 0
        self.wireframe_color = om.MColor((1.0, 1.0, 1.0))  # 线框颜色

class SimpleLocatorDrawOverride(omr.MPxDrawOverride):
    NAME = "SimpleLocatorDrawOverride"

    def __init__(self, obj):
        super(SimpleLocatorDrawOverride, self).__init__(obj, None, True)  # 第一个参数是maya object,第二个参数是绘制是callback函数,第三个参数是默认为True,为True时将会将此标志位dirty状态，因此可以持续更新,建议为True,除非遇到了性能问题可以为False

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        """ 在使用绘制图形的方法之前,使用这个方法来将数据检索与缓存 """
        data = old_data
        if not data:
            data = SimpleLocatorUserData()

        locator_obj = obj_path.node()
        node_fn = om.MFnDependencyNode(locator_obj)

        data.shape_index = node_fn.findPlug("shapeIndex", False).asInt()

        display_status = omr.MGeometryUtilities.displayStatus(obj_path)
        if display_status == omr.MGeometryUtilities.kDormant:  
            data.wireframe_color = om.MColor((0.0, 0.1, 0.0)) # 当节点处于未选中状态时设置颜色为深绿色
        else:
            data.wireframe_color = omr.MGeometryUtilities.wireframeColor(obj_path)  # 其他状态按照maya的标准来设置线框颜色

        return data

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        """ 绘制图形的方法

        Args:
            obj_path (_type_): 指向正在绘制的对象的路径,这里是指locator节点
            draw_manager (_type_): 用于绘制简单的几何图形
            frame_context (_type_): 包含当前渲染框架的一些全局信息
            data (_type_): 用户创建的数据对象,存储缓存数据,类型为MUserDataObject
        """
        draw_manager.beginDrawable()

        draw_manager.setColor(data.wireframe_color)

        if data.shape_index == 0: # 绘制圆形
            draw_manager.circle(om.MPoint(0.0, 0.0, 0.0), om.MVector(0.0, 1.0, 0.0), 1, False)
        elif data.shape_index == 1: # 绘制矩形
            draw_manager.rect(om.MPoint(0.0, 0.0, 0.0), om.MVector(0.0, 0.0, 1.0), om.MVector(0.0, 1.0, 0.0), 1.0, 1.0, False)
        elif data.shape_index == 2: # 绘制三角形
            point_array = om.MPointArray([(-1.0, 0.0, -1.0), (0.0, 0.0, 1.0),(1.0, 0.0, -1.0),(-1.0, 0.0, -1.0)])
            draw_manager.lineStrip(point_array, False)

        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return SimpleLocatorDrawOverride(obj)


def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    try:
        plugin_fn.registerNode(SimpleLocatorNode.TYPE_NAME,
                               SimpleLocatorNode.TYPE_ID,
                               SimpleLocatorNode.creator,
                               SimpleLocatorNode.initialize,
                               om.MPxNode.kLocatorNode,
							   SimpleLocatorNode.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(SimpleLocatorNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(SimpleLocatorNode.DRAW_CLASSIFICATION,
                                                      SimpleLocatorNode.DRAW_REGISTRANT_ID,
                                                      SimpleLocatorDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(SimpleLocatorDrawOverride.NAME))


def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(SimpleLocatorNode.DRAW_CLASSIFICATION,
                                                        SimpleLocatorNode.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(SimpleLocatorDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(SimpleLocatorNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(SimpleLocatorNode.TYPE_NAME))


if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    cmds.file(new=True,f=True)

    plugin_name = "simple_locator_node.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("simplelocator")')
