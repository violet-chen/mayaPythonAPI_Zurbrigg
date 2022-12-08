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
        target_position = om.MPoint(target_position) * world_matrix.inverse() # 将目标位置转换为局部空间下的数值
        target_position = om.MFloatVector(target_position) # 获取目标位置在局部空间下的floatVector

        input_handle = data_block.outputArrayValue(self.input) # 使用outputArray代替inputArray以避免重新计算（外网翻译）
        input_handle.jumpToElement(multi_index)
        input_element_handle = input_handle.outputValue()

        input_geom = input_element_handle.child(self.inputGeom).asMesh()
        mesh_fn = om.MFnMesh(input_geom)

        normals = om.MFloatVectorArray()  # 用来存取inputgeom的顶点的所有浮点法线
        mesh_fn.getVertexNormals(False, normals) # False的作用是不要average normal


        geo_iter.reset()
        while not geo_iter.isDone():
            # 顶点迭代器所获取的位置都是在局部空间下的位置
            pt_local = geo_iter.position()

            target_vector = target_position - om.MFloatVector(pt_local)

            distance = target_vector.length()

            if distance <= max_distance:

                normal = normals[geo_iter.index()] # 局部空间下的顶点的法线浮点向量

                angle = normal.angle(target_vector)  # 顶点的法线与顶点与目标点的向量之间的角度
                if angle <= AttractorDeformerNode.MAX_ANGLE:

                    offset = target_vector * ((max_distance-distance)/max_distance)

                    new_pt_local = pt_local + om.MVector(offset)  # 局部空间下的新顶点位置

                    geo_iter.setPosition(new_pt_local)

            geo_iter.next()

    def accessoryAttribute(self):
        """ 返回要辅助修改的属性 """
        return AttractorDeformerNode.target_position
    
    def accessoryNodeSetup(self, dag_modifier):
        """ dag_modifier用于执行节点创建和连接操作 """
        locator = dag_modifier.createNode("locator")

        locator_fn = om.MFnDependencyNode(locator)
        locator_translate_plug = locator_fn.findPlug("translate", False) # False意思是不需要networkplug，networkplug意思是在DG中建立连接的属性

        target_position_plug = om.MPlug(self.thisMObject(), AttractorDeformerNode.target_position)  # 获取变形器的target_position的plug
        dag_modifier.connect(locator_translate_plug, target_position_plug)

        # 将定位器得位置设置在output_geom的位置
        # 这里的output_geom指的是shape节点
        # parent指的是transform节点，因为只有transform节点才有xyz坐标
        output_geom_plug = om.MPlug(self.thisMObject(), self.outputGeom)
        mPlugArray2 = om.MPlugArray()
        output_geom_plug[0].connectedTo(mPlugArray2,False,True)
        output_geom_obj = mPlugArray2[0].node()
        output_geom_fn = om.MFnDagNode(output_geom_obj)
        parent_obj = output_geom_fn.parent(0)
        parent_fn = om.MFnDependencyNode(parent_obj)
        parent_translate_plug = parent_fn.findPlug("translate",False)
        parent_translate_x_handle = parent_translate_plug.child(0).asFloat()
        parent_translate_y_handle = parent_translate_plug.child(1).asFloat()
        parent_translate_z_handle = parent_translate_plug.child(2).asFloat()
    
        locator_translate_plug.child(0).setFloat(parent_translate_x_handle)
        locator_translate_plug.child(1).setFloat(parent_translate_y_handle)
        locator_translate_plug.child(2).setFloat(parent_translate_z_handle)

        

        
        
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

    cmds.evalDeferred('cmds.file("C:/Users/Administrator/Documents/maya/2018/plug-ins/test_scene/attractor_test.ma",o=True,f=True)')
    cmds.evalDeferred('cmds.select("pSphere1"); cmds.deformer(typ="attractordeformernode")')
    #cmds.evalDeferred('cmds.connectAttr("locator1.translate","attractordeformernode1.targetPosition",f=True)')