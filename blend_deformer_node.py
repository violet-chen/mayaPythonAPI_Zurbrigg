# coding: utf-8
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import maya.cmds as cmds

class BlendDeformerNode(ommpx.MPxDeformerNode):

    TYPE_NAME = "blenddeformernode"
    TYPE_ID = om.MTypeId(0x0007F7FD)

    def __init__(self):
        super(BlendDeformerNode, self).__init__()

    def deform(self, data_block, geo_iter, matrix, multi_index):
        """
            变形的逻辑
        Args:
            data_block (_type_): 数据块
            geo_iter (_type_): 针对geometry的顶点迭代器
            matrix (_type_): 世界空间的矩阵
            multi_index (_type_): _description_
        """
        # envelope是MPxDeformerNode类自带的属性
        envelope = data_block.inputValue(self.envelope).asFloat() # 获取控制整体权重值的值
        if envelope == 0:
            return    

        blend_weight = data_block.inputValue(self.blend_weight).asFloat() # 获取混合的权重值
        if blend_weight == 0:
            return

        target_mesh = data_block.inputValue(self.blend_mesh).asMesh()  # 获取目标mesh
        if target_mesh.isNull():
            return

        target_points = om.MPointArray() # 定义一个接受目标mesh所有点的数组

        target_mesh_fn = om.MFnMesh(target_mesh) # 定义一个目标mesh的函数集
        target_mesh_fn.getPoints(target_points) # 使用函数集的方法将点放入到点数组中

        global_weight = blend_weight * envelope  # 得到总的权重值

        geo_iter.reset() # 重置迭代器
        while not geo_iter.isDone():
            
            source_pt = geo_iter.position()
            target_pt = target_points[geo_iter.index()]

            final_pt = source_pt + ((target_pt - source_pt) * global_weight)

            geo_iter.setPosition(final_pt)
            
            geo_iter.next()    
        
    @classmethod
    def creator(cls):
        return BlendDeformerNode()
    
    @classmethod
    def initialize(cls):
        
        typed_attr = om.MFnTypedAttribute()
        cls.blend_mesh = typed_attr.create("blendMesh", "bMesh", om.MFnData.kMesh)

        numeric_attr = om.MFnNumericAttribute()
        cls.blend_weight = numeric_attr.create("blendWeight", "bWeight", om.MFnNumericData.kFloat, 0.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)

        cls.addAttribute(cls.blend_mesh)
        cls.addAttribute(cls.blend_weight)

        #变形器节点具有默认的outputGeom属性，因此我们没必要再创建一个输出的属性，我们可以直接利用这个默认的outputGemo属性
        output_geom = ommpx.cvar.MPxGeometryFilter_outputGeom  

        cls.attributeAffects(cls.blend_mesh, output_geom)
        cls.attributeAffects(cls.blend_weight,output_geom)

def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)  # 定义插件

    try:
        plugin_fn.registerNode(BlendDeformerNode.TYPE_NAME,
                               BlendDeformerNode.TYPE_ID,
                               BlendDeformerNode.creator,
                               BlendDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(BlendDeformerNode.TYPE_NAME))

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(BlendDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BlendDeformerNode.TYPE_NAME))

if __name__ == '__main__':
    cmds.file(new=True,f=True)
    plugin_name = "blend_deformer_node.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('cmds.file("D:/ZhangRuiChen/zrctest/blend_deformer_node_test.ma",o=True,f=True)')
    cmds.evalDeferred('cmds.select("sourceSphere"); cmds.deformer(typ="blenddeformernode")')
    cmds.evalDeferred('cmds.connectAttr("deformerTargetShape.outMesh", "blenddeformernode1.blendMesh", force=True)')
