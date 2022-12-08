# coding: utf-8
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import maya.cmds as cmds

class AttractorDeformerNode(ommpx.MPxDeformerNode):

    TYPE_NAME = "attractordeformernode"
    TYPE_ID = om.MTypeId(0x0007F7FE)

    MAX_ANGLE = 0.5 * 3.14159265 # 90度

    def __init__(self):
        super(AttractorDeformerNode, self).__init__()

    def deform(self, data_block, geo_iter, world_matrix, multi_index):
        """
            变形的逻辑
        Args:
            data_block (_type_): 数据块
            geo_iter (_type_): 针对geometry的顶点迭代器
            matrix (_type_): 世界空间的矩阵
            multi_index (_type_): geom_index
        """
        # envelope是MPxDeformerNode类自带的属性
        envelope = data_block.inputValue(self.envelope).asFloat() # 获取控制整体权重值的值
        if envelope == 0:
            return    
        
        max_distance = data_block.inputValue(AttractorDeformerNode.max_distance).asFloat()
        if max_distance == 0:
            return

        target_position = data_block.inputValue(AttractorDeformerNode.target_position).asFloatVector()

        input_handle = data_block.outputArrayValue(self.input) # 使用outputArray代替inputArray以避免重新计算（外网翻译）
        input_handle.jumpToElement(multi_index)
        input_element_handle = input_handle.outputValue()

        input_geom = input_element_handle.child(self.inputGeom).asMesh()
        mesh_fn = om.MFnMesh(input_geom)

        normals = om.MFloatVectorArray()  # 用来存取inputgeom的顶点的所有浮点法线
        mesh_fn.getVertexNormals(False, normals) # False的作用是不要average normal

        inverse_world_matrix = world_matrix.inverse()

        geo_iter.reset()
        while not geo_iter.isDone():
            pt_local = geo_iter.position()
            pt_world = pt_local * world_matrix

            target_vector = target_position - om.MFloatVector(pt_world)

            distance = target_vector.length()

            if distance <= max_distance:

                normal = om.MVector(normals[geo_iter.index()]) * world_matrix # 世界空间下的顶点的法线向量
                normal = om.MFloatVector(normal)

                angle = normal.angle(target_vector)  # 顶点的法线与顶点与目标点的向量之间的角度
                if angle <= AttractorDeformerNode.MAX_ANGLE:

                    offset = target_vector * ((max_distance-distance)/max_distance)

                    new_pt_world = pt_world + om.MVector(offset)
                    new_pt_local = new_pt_world * inverse_world_matrix  # 局部空间下的新顶点位置

                    geo_iter.setPosition(new_pt_local)

            geo_iter.next()

    @classmethod
    def creator(cls):
        return AttractorDeformerNode()
    
    @classmethod
    def initialize(cls):
        
        numeric_attr = om.MFnNumericAttribute()
        cls.max_distance = numeric_attr.create("maximumDistance", "maxDist", om.MFnNumericData.kFloat, 1.0)
        numeric_attr.setKeyable(True)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(2.0)

        cls.target_position = numeric_attr.createPoint("targetPosition", "targetPos")
        numeric_attr.setKeyable(True)

        cls.addAttribute(cls.max_distance)
        cls.addAttribute(cls.target_position)

        #变形器节点具有默认的outputGeom属性，因此我们没必要再创建一个输出的属性，我们可以直接利用这个默认的outputGemo属性
        output_geom = ommpx.cvar.MPxGeometryFilter_outputGeom  

        cls.attributeAffects(cls.max_distance, output_geom)
        cls.attributeAffects(cls.target_position,output_geom)

def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)  # 定义插件

    try:
        plugin_fn.registerNode(AttractorDeformerNode.TYPE_NAME,
                               AttractorDeformerNode.TYPE_ID,
                               AttractorDeformerNode.creator,
                               AttractorDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(AttractorDeformerNode.TYPE_NAME))
    
    cmds.makePaintable(AttractorDeformerNode.TYPE_NAME, "weights", attrType="multiFloat", shapeMode = "deformer") # 使其能绘制权重

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    cmds.makePaintable(AttractorDeformerNode.TYPE_NAME, "weights",remove=True) # 移除使其能绘制权重
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(AttractorDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(AttractorDeformerNode.TYPE_NAME))
    
if __name__ == '__main__':
    cmds.file(new=True,f=True)
    plugin_name = "attractor_deformer_node.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.file("D:/ZhangRuiChen/zrctest/attractor_test.ma",o=True,f=True)')
    cmds.evalDeferred('cmds.select("pSphere1"); cmds.deformer(typ="attractordeformernode")')
    cmds.evalDeferred('cmds.connectAttr("locatorShape1.worldPosition[0]","attractordeformernode1.targetPosition",f=True)')