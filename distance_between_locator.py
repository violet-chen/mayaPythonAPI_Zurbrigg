# coding: utf-8
# 不适用于2018及以下版本
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr

import maya.cmds as cmds


def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass

class DistanceBetweenCmd(om.MPxCommand):

    COMMAND_NAME = "rcDistanceBetween"

    def __init__(self):
        super(DistanceBetweenCmd, self).__init__()
    
    def doIt(self, arg_list):
        try:
            arg_ab = om.MArgDatabase(self.syntax(), arg_list)
        except:
            self.displayError("Error parsing arguments")
            raise
        
        selection_list = arg_ab.getObjectList()
        if not selection_list.length() == 2:
            raise RuntimeError("Command requires two transform nodes")
        
        self.selected_objs = [selection_list.getDependNode(0), selection_list.getDependNode(1)]

        for selected_obj in self.selected_objs:
            if selected_obj.apiType() != om.MFn.kTransform:
                raise RuntimeError("One or more nodes is not a transform")
        
        self.dag_modifier = om.MDagModifier() # 创建MDagModifier对象，在doIt中完成注册(还未实现，在redoIt中实现)，用来修改Dag和DG

        self.transform_obj = self.dag_modifier.createNode("transform", om.MObject.kNullObj) # 这个命令创建一个transform节点，父节点为Null

        transform_name = "{0}1".format(DistanceBetweenLocator.TYPE_NAME)
        self.dag_modifier.renameNode(self.transform_obj, transform_name) 

        self.dest_obj = self.dag_modifier.createNode(DistanceBetweenLocator.TYPE_ID, self.transform_obj) # 创建DistanceBetweenLocator节点， 父节点为transform节点

        shape_name = "{0}Shape1".format(DistanceBetweenLocator.TYPE_NAME) # 注册时先这样命名，因为是子物体所以创建多个节点的话maya不会自动更改序号,需要在redoIt中修改注册的命名
        self.dag_modifier.renameNode(self.dest_obj, shape_name)

        dest_fn = om.MFnDependencyNode(self.dest_obj)
        
        # 将选择的两个物体的translate与自定义节点建立连接
        for i in range(2):
            src_fn = om.MFnDependencyNode(self.selected_objs[i])

            for coord in ['X', 'Y', 'Z']:
                src_plug = src_fn.findPlug("translate{0}".format(coord), False)
                dest_plug = dest_fn.findPlug("point{0}{1}".format(i + 1, coord), False)

                self.dag_modifier.connect(src_plug, dest_plug)

        self.redoIt()

        print("transform name: {0}".format(om.MFnDependencyNode(self.transform_obj).name()))

    def get_shape_name(self, transform_name):
        split_name = transform_name.split(DistanceBetweenLocator.TYPE_NAME)

        return "{0}Shape{1}".format(DistanceBetweenLocator.TYPE_NAME, split_name[1])

    def undoIt(self):
        self.dag_modifier.undoIt()

    def redoIt(self):
        self.dag_modifier.doIt()

        shape_fn = om.MFnDependencyNode(self.dest_obj)
        shape_fn.setName(self.get_shape_name(om.MFnDependencyNode(self.transform_obj).name()))

        print("shape name: {0}".format(om.MFnDependencyNode(self.dest_obj).name()))

    def isUndoable(self):
        return True

    @classmethod
    def creator(cls):
        return DistanceBetweenCmd()
    
    @classmethod
    def create_syntax(cls):
        syntax = om.MSyntax()

        # 设置要传递给命令的对象的类型和数量
        syntax.setObjectType(om.MSyntax.kSelectionList)
        # 如果设置为True，那么当命令行上没有提供对象时，Maya将传递当前选择。默认为False。
        syntax.useSelectionAsDefault(True)

        return syntax

class DistanceBetweenLocator(omui.MPxLocatorNode):
    TYPE_NAME = "distanceBetweenLocator"
    TYPE_ID = om.MTypeId(0x0007F7FD)
    DRAW_CLASSIFICATION = "drawdb/geometry/distancebetweenlocator"
    DRAW_REGISTRANT_ID = "DistanceBetweenLocator"

    point1_obj = None
    point2_obj = None
    distance_obj = None

    min_distance_obj = None
    max_distance_obj = None
    color_ramp_obj = None

    curve_ramp_obj = None

    DEFAULT_POSITIONS = [0.0, 1.0] # 颜色渐变的位置,这里值从0到1的渐变
    DEFAULT_COLORS = [om.MColor([0.0, 0.0, 0.0]), om.MColor([1.0, 1.0, 1.0])] # 位置对应的颜色
    DEFAULT_INTERPS = [om.MRampAttribute.kLinear, om.MRampAttribute.kLinear]  # 位置对应的渐变方式

    CURVE_POSITIONS = [0.0, 0.5, 1.0] # 曲线点的位置，这里是0到0.5到1三个点
    CURVE_VALUES = [0.0, 1.0, 0.0] # 曲线点对应的值
    CURVE_INTERPS = [om.MRampAttribute.kSmooth, om.MRampAttribute.kSmooth, om.MRampAttribute.kSmooth]

    def __init__(self):
        super(DistanceBetweenLocator, self).__init__()

    def postConstructor(self):
        """ 节点初始化完以后的构造函数,设置节点的渐变属性 """
        color_ramp_attr = om.MRampAttribute(self.thisMObject(), self.color_ramp_obj)
        color_ramp_attr.addEntries(DistanceBetweenLocator.DEFAULT_POSITIONS, DistanceBetweenLocator.DEFAULT_COLORS, DistanceBetweenLocator.DEFAULT_INTERPS)

        curve_ramp_attr = om.MRampAttribute(self.thisMObject(), self.curve_ramp_obj)
        curve_ramp_attr.addEntries(DistanceBetweenLocator.CURVE_POSITIONS, DistanceBetweenLocator.CURVE_VALUES, DistanceBetweenLocator.CURVE_INTERPS)
    
    def compute(self, plug, data):
        point1 = om.MPoint(data.inputValue(self.point1_obj).asFloatVector()) # 得到MPoint对象
        point2 = om.MPoint(data.inputValue(self.point2_obj).asFloatVector())

        distance = point1.distanceTo(point2) # 使用MPoint的计算距离的方法

        data.outputValue(self.distance_obj).setDouble(distance)

        data.setClean(plug) # 使plug变成干净的状态

    @classmethod
    def creator(cls):
        return DistanceBetweenLocator()

    @classmethod
    def initialize(cls):
        numeric_attr = om.MFnNumericAttribute()

        cls.point1_obj = numeric_attr.createPoint("point1", "p1")
        numeric_attr.readable = False
        numeric_attr.keyable = True

        cls.point2_obj = numeric_attr.createPoint("point2", "p2")
        numeric_attr.readable = False
        numeric_attr.keyable = True

        cls.distance_obj = numeric_attr.create("distance", "dist", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.writable = False

        cls.min_distance_obj = numeric_attr.create("minDistance", "min", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.readable = False
        numeric_attr.keyable = True
        numeric_attr.setMin(0.0)

        cls.max_distance_obj = numeric_attr.create("maxDistance", "max", om.MFnNumericData.kDouble, 10.0)
        numeric_attr.readable = False
        numeric_attr.keyable = True
        numeric_attr.setMin(0.0)

        cls.color_ramp_obj = om.MRampAttribute.createColorRamp("colorRamp", "col")

        cls.curve_ramp_obj = om.MRampAttribute.createCurveRamp("curveRamp", "cuv")

        cls.addAttribute(cls.point1_obj)
        cls.addAttribute(cls.point2_obj)
        cls.addAttribute(cls.distance_obj)
        cls.addAttribute(cls.min_distance_obj)
        cls.addAttribute(cls.max_distance_obj)
        cls.addAttribute(cls.color_ramp_obj)
        cls.addAttribute(cls.curve_ramp_obj)

        cls.attributeAffects(cls.point1_obj, cls.distance_obj)
        cls.attributeAffects(cls.point2_obj, cls.distance_obj)

class DistanceBetweenUserData(om.MUserData):

    def __init__(self, deleteAfterUse = False):
        super(DistanceBetweenUserData, self).__init__(deleteAfterUse)

        self.distance = 0
        self.point1 = om.MPoint()
        self.point2 = om.MPoint()

class DistanceBetweenDrawOverride(omr.MPxDrawOverride):
    """ 负责在视口中绘制几何图形 """
    NAME = "DistanceBetweenDrawOverride"

    def __init__(self, obj):
        super(DistanceBetweenDrawOverride, self).__init__(obj, None, False) # 第一个参数是maya object,第二个参数是绘制是callback函数,第三个参数是默认为True,为True时将会将此标志位dirty状态，因此可以持续更新,建议为True,除非遇到了性能问题可以为False

    def refineSelectionPath(self, select_info, hit_item, path, components, obj_mask):
        """ 重新定义选择，使绘制的几何图形不能够被选中 """
        return False

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

        node_fn = om.MFnDependencyNode(obj_path.node())

        data.point1 = om.MPoint(node_fn.findPlug("point1X", False).asDouble(),
                                node_fn.findPlug("point1Y", False).asDouble(),
                                node_fn.findPlug("point1Z", False).asDouble())

        data.point2 = om.MPoint(node_fn.findPlug("point2X", False).asDouble(),
                                node_fn.findPlug("point2Y", False).asDouble(),
                                node_fn.findPlug("point2Z", False).asDouble())

        data.distance = node_fn.findPlug("distance", False).asDouble()

        min_distance = node_fn.findPlug("minDistance", False).asDouble()
        max_distance = node_fn.findPlug("maxDistance", False).asDouble()

        if min_distance < max_distance:
            ramp_position = (data.distance - min_distance) / (max_distance - min_distance) # 计算得到的距离与用户设定的最小距离与最大距离之间的占比
            ramp_position = min(max(0,ramp_position), 1.0) # 最小为0，最大为1
        else:
            ramp_position = 0.0
        # 通过颜色渐变方式设置颜色
        # color_ramp_plug = node_fn.findPlug("colorRamp", False)
        # color_ramp_attr = om.MRampAttribute(color_ramp_plug)

        # data.color = color_ramp_attr.getValueAtPosition(ramp_position) # 将颜色设置为渐变中的颜色
        
        # 通过曲线渐变方式设置颜色
        curve_ramp_plug = node_fn.findPlug("curveRamp", False)
        curve_ramp_attr = om.MRampAttribute(curve_ramp_plug)

        curve_ramp_value = curve_ramp_attr.getValueAtPosition(ramp_position)

        data.color = om.MColor([curve_ramp_value, curve_ramp_value, curve_ramp_value])
        
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
        
        draw_manager.setFontSize(14)
        draw_manager.setFontWeight(100)
        draw_manager.setColor(data.color)

        pos = om.MPoint((om.MVector(data.point1) + om.MVector(data.point2))/2.0) # 得到两点之间的重点
        text = "{0:.3f}".format(data.distance)

        draw_manager.text(pos, text, omr.MUIDrawManager.kCenter)
        draw_manager.line(data.point1,data.point2)

        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return DistanceBetweenDrawOverride(obj)


def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件
    # 注册命令
    try:
        plugin_fn.registerCommand(DistanceBetweenCmd.COMMAND_NAME,
                                  DistanceBetweenCmd.creator,
                                  DistanceBetweenCmd.create_syntax)
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(DistanceBetweenCmd.COMMAND_NAME))
    
    # 注册节点
    try:
        plugin_fn.registerNode(DistanceBetweenLocator.TYPE_NAME,
                               DistanceBetweenLocator.TYPE_ID,
                               DistanceBetweenLocator.creator,
                               DistanceBetweenLocator.initialize,
                               om.MPxNode.kLocatorNode,
                               DistanceBetweenLocator.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(DistanceBetweenLocator.TYPE_NAME))
    
    #注册绘制覆盖
    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(DistanceBetweenLocator.DRAW_CLASSIFICATION,
                                                      DistanceBetweenLocator.DRAW_REGISTRANT_ID,
                                                      DistanceBetweenDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(DistanceBetweenDrawOverride.NAME))


def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = om.MFnPlugin(plugin)

    # 取消注册绘画覆盖
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(DistanceBetweenLocator.DRAW_CLASSIFICATION,
                                                        DistanceBetweenLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(DistanceBetweenDrawOverride.NAME))
    # 取消注册节点
    try:
        plugin_fn.deregisterNode(DistanceBetweenLocator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(DistanceBetweenLocator.TYPE_NAME))
    # 取消注册命令
    try:
        plugin_fn.deregisterCommand(DistanceBetweenCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister command: {0}".format(DistanceBetweenCmd.COMMAND_NAME))

def rc_distance_between_test():
    cmds.setAttr("persp.translate", 3.5, 5.5, 10.0)
    cmds.setAttr("persp.rotate", -27.0, 19.0, 0.0)

    cube1 = cmds.polyCube()[0]
    cube2 = cmds.polyCube()[0]

    cmds.setAttr("{0}.translateX".format(cube1), -2.5)
    cmds.setAttr("{0}.translateX".format(cube2), 2.5)

    cmds.rcDistanceBetween(cube1, cube2)

if __name__ == '__main__':

    cmds.file(new=True, force=True)

    """ 注册后,在maya脚本编辑器中的使用方法 """
    plugin_name = "distance_between_locator.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('rc_distance_between_test()')
