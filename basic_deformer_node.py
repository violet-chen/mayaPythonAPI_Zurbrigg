# coding: utf-8
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import maya.cmds as cmds

class BasicDeformerNode(ommpx.MPxDeformerNode):

    TYPE_NAME = "basicdeformernode"
    TYPE_ID = om.MTypeId(0x0007F7FC)

    def __init__(self):
        super(BasicDeformerNode, self).__init__()

    def deform(self, data_block, geo_iter, matrix, multi_index):
        
        envelope = data_block.inputValue(self.envelope).asFloat() # 总权重

        if envelope == 0:
            return
        
        geo_iter.reset() # 重置迭代器
        while not geo_iter.isDone():

            if geo_iter.index() % 2 == 0:
                pt = geo_iter.position()
                # 局部空间
                # pt.x += (0.2*envelope)

                # 世界空间
                pt = pt * matrix * 0.1

                geo_iter.setPosition(pt)

            geo_iter.next()    
        
    @classmethod
    def creator(cls):
        return BasicDeformerNode()
    
    @classmethod
    def initialize(cls):
        pass

def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)  # 定义插件

    try:
        plugin_fn.registerNode(BasicDeformerNode.TYPE_NAME,
                               BasicDeformerNode.TYPE_ID,
                               BasicDeformerNode.creator,
                               BasicDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(BasicDeformerNode.TYPE_NAME))

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(BasicDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BasicDeformerNode.TYPE_NAME))

if __name__ == '__main__':
    cmds.file(new=True,f=True)
    plugin_name = "basic_deformer_node.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('cmds.file("C:/Users/Adiministrator/Destop/test.ma",o=True,f=True)')
    cmds.evalDeferred('cmds.select("nurbsPlane1"); cmds.deformer(typ="basicdeformernode")')