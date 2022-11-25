# coding: utf-8
import maya.api.OpenMaya as om
import maya.cmds as cmds

def maya_useNewAPI():
    """ 这个函数告诉了maya这个插件生成,并且生成的对象使用maya python api 2.0 """
    pass

class RollingNode(om.MPxNode):
    TYPE_NAME = "rollingnode"
    TYPE_ID = om.MTypeId(0x0007F7F9)
    # 提前声明节点的属性
    distance_obj = None
    radius_obj = None
    rotation_obj = None

    def __init__(self):
        super(RollingNode, self).__init__()

    def compute(self, plug, data):
        """_summary_

        Args:
            plug (_type_): 当plug是dirty状态时,会传过来,要求更新
            data (_type_): data提供了读取和写入节点属性值的方法
        """
        if plug == RollingNode.rotation_obj:

            distance = data.inputValue(RollingNode.distance_obj).asDouble()
            radius = data.inputValue(RollingNode.radius_obj).asDouble()
            if radius==0:
                rotation = 0
            else:
                rotation = distance / radius

            rotation_data_handle = data.outputValue(RollingNode.rotation_obj)
            rotation_data_handle.setDouble(rotation)

            data.setClean(plug)

    @classmethod
    def creator(cls):
        return RollingNode()
    
    @classmethod
    def initialize(cls):
        numeric_attr = om.MFnNumericAttribute() # 创建一个针对数字属性的函数集

        cls.distance_obj = numeric_attr.create("distance", "dis", om.MFnNumericData.kDouble, 0.0)  # 属性长名，属性短名，属性数字类型，属性初始值
        numeric_attr.keyable = True # 设置属性可以key关键帧(这样属性就能出现在channel box中)
        numeric_attr.readable = False  #  设置属性没有输出引脚(其他属性不能读它)

        cls.radius_obj = numeric_attr.create("radius", "rad", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.keyable = True
        numeric_attr.readable = False

        unit_attr = om.MFnUnitAttribute()  # 创建一个针对单位属性的函数集

        cls.rotation_obj = unit_attr.create("rotation", "rot", om.MFnUnitAttribute.kAngle, 0.0)
        
        # unit_attr.writable = False #  设置属性没有输入引脚(其他属性不能直接写入它)
        
        # 添加属性
        cls.addAttribute(cls.distance_obj)
        cls.addAttribute(cls.radius_obj)
        cls.addAttribute(cls.rotation_obj)
        # 设置属性影响
        cls.attributeAffects(cls.distance_obj, cls.rotation_obj)
        cls.attributeAffects(cls.radius_obj, cls.rotation_obj)

def initializePlugin(plugin):
    """
    加载插件时执行此函数
    plugin: MObject用于使用MFnPlugin函数集注册插件
    """
    
    vendor = "RuiChen"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(RollingNode.TYPE_NAME,
                               RollingNode.TYPE_ID,
                               RollingNode.creator,
                               RollingNode.initialize,
                               om.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(RollingNode.TYPE_NAME))

def uninitializePlugin(plugin):
    """
    取消加载插件时执行此函数
    plugin: MObject用于使用MFnPlugin函数集取消注册插件
    """    
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(RollingNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(RollingNode.TYPE_NAME))

if __name__ == "__main__":
    """
    测试时使用
    """

    cmds.file(new=True, force=True)

    plugin_name = "rolling_node.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name)) # 取消加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))  # 加载插件
    
    cmds.evalDeferred('cmds.createNode("rollingnode")')

    #cmds.evalDeferred(cmds.file("D:/ZhangRuiChen/zrctest/test.ma",o=True,f=True))