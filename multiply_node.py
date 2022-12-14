# coding: utf-8
import maya.api.OpenMaya as om
import maya.cmds as cmds

def maya_useNewAPI():
    """ 这个函数告诉了maya这个插件生成,并且生成的对象使用maya python api 2.0 """
    pass

class MutiplyNode(om.MPxNode):
    TYPE_NAME = "multiplynode"
    TYPE_ID = om.MTypeId(0x0007F7F8)
    # 提前声明节点的属性
    multiplier_obj = None
    multiplicand_obj = None
    product_obj = None

    def __init__(self):
        super(MutiplyNode, self).__init__()

    def compute(self, plug, data):
        """_summary_

        Args:
            plug (_type_): 当plug是dirty状态时,会传过来,要求更新
            data (_type_): data提供了读取和写入节点属性值的方法
        """
        if plug == MutiplyNode.product_obj:

            multiplier = data.inputValue(MutiplyNode.multiplier_obj).asInt()  # 获取multiplier_obj对象的输入的属性值
            multiplicand = data.inputValue(MutiplyNode.multiplicand_obj).asDouble()  # 获取multiplicand_obj对象的输入的属性值
            product = multiplier * multiplicand 

            product_data_handle = data.outputValue(MutiplyNode.product_obj)  # 获取product_obj对象的输出数据
            product_data_handle.setDouble(product)  # 设置product_obj对象的输出数据

            data.setClean(plug) # 将plug设置为clean状态


    @classmethod
    def creator(cls):
        return MutiplyNode()
    
    @classmethod
    def initialize(cls):
        numeric_attr = om.MFnNumericAttribute() # 创建一个用来设置数字系列属性的对象

        cls.multiplier_obj = numeric_attr.create("multiplier", "mul", om.MFnNumericData.kInt, 2)  # 属性长名，属性短名，属性数字类型，属性初始值
        numeric_attr.keyable = True # 设置属性可以key关键帧(这样属性就能出现在channel box中)
        numeric_attr.readable = False  #  设置属性没有输出引脚(其他属性不能读它)

        cls.multiplicand_obj = numeric_attr.create("multiplicand", "mulc", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.keyable = True
        numeric_attr.readable = False

        cls.product_obj = numeric_attr.create("product", "prod", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.writable = False #  设置属性没有输入引脚(其他属性不能直接写入它)
        
        # 添加属性
        cls.addAttribute(cls.multiplier_obj)
        cls.addAttribute(cls.multiplicand_obj)
        cls.addAttribute(cls.product_obj)
        # 设置属性影响
        cls.attributeAffects(cls.multiplier_obj, cls.product_obj)
        cls.attributeAffects(cls.multiplicand_obj, cls.product_obj)

def initializePlugin(plugin):
    """
    加载插件时执行此函数
    plugin: MObject用于使用MFnPlugin函数集注册插件
    """
    
    vendor = "RuiChen"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(MutiplyNode.TYPE_NAME,
                               MutiplyNode.TYPE_ID,
                               MutiplyNode.creator,
                               MutiplyNode.initialize,
                               om.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(MutiplyNode.TYPE_NAME))

def uninitializePlugin(plugin):
    """
    取消加载插件时执行此函数
    plugin: MObject用于使用MFnPlugin函数集取消注册插件
    """    
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(MutiplyNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(MutiplyNode.TYPE_NAME))

if __name__ == "__main__":
    """
    测试时使用
    """

    cmds.file(new=True, force=True)

    plugin_name = "multiply_node.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
    
    cmds.evalDeferred('cmds.createNode("multiplynode")')