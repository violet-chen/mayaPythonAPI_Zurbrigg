# coding:utf-8
# 自定义一个变形器节点,通过调整ripple改变多边形的形状
import math

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx  # 制作自定义的东西时需要的模块
import sys  # 输出错误所需要的模块

nodeName = "RippleDeformer"  # 定义节点的名字
nodeId = OpenMaya.MTypeId(0x102fff)


class Ripple(OpenMayaMPx.MPxDeformerNode):
    """
    Commands ----> MPxCommand
    Custom   ----> MPxNode
    Deformer ----> MPxDeformerNode
    """
    # 创建MObject类型的输入输出
    mObj_Displace = OpenMaya.MObject()
    mObj_Amplitude = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIterator, matrix, geometryIndex):
        """
        变形器的核心参数
        :param dataBlock:数据块
        :param geoIterator: 迭代器，例如遍历一个几何体的所有顶点时用的到
        :param matrix: 矩阵   几何体的世界矩阵或受影响的网格
        :param geometryIndex: 几何索引，当使用多个几何体时，所有几何体都进入这个属性
        :return:
        """

        input = OpenMayaMPx.cvar.MPxGeometryFilter_input
        # 1. Attach a handle to input Array Attribute
        # 1. 为输入数组属性附加handle
        # 后来优化将inputArrayValue和inputValue都改为了output，可能是因为用output会自动检索最优路线吧
        dataHandleInputArray = dataBlock.outputArrayValue(input)
        # 2. Jump to particular element
        # 2. 跳转到特定元素
        dataHandleInputArray.jumpToElement(geometryIndex)
        # 3. Attach a handle to specific data block
        # 3. 将handle附加到特定的数据块
        dataHandleInputElement = dataHandleInputArray.outputValue()
        # 4. Reach to the child - inputGeom
        inputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
        dataHandleInputGeom = dataHandleInputElement.child(inputGeom)
        inMesh = dataHandleInputGeom.asMesh()
        # Envelope
        envelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope
        dataHandleEnvelope = dataBlock.inputValue(envelope)
        envelopeValue = dataHandleEnvelope.asFloat()
        # Amplitude
        dataHandleAmplitude = dataBlock.inputValue(Ripple.mObj_Amplitude)
        amplitudeValue = dataHandleAmplitude.asFloat()
        # Displace
        dataHandleDisplace = dataBlock.inputValue(Ripple.mObj_Displace)
        displaceValue = dataHandleDisplace.asFloat()

        mFloatVectorArray_normal = OpenMaya.MFloatVectorArray()  # 创建一个MFloatVectorArray的对象，getVertexNormals方法需要用到
        mFnMesh = OpenMaya.MFnMesh(inMesh)
        # 第一个参数是angleWeighted，如果angleWeighted设置为false，则返回环绕面法线的简单平均值。第三个参数是设置空间为对象空间
        mFnMesh.getVertexNormals(False, mFloatVectorArray_normal, OpenMaya.MSpace.kObject)

        mPointArray_meshVert = OpenMaya.MPointArray()  # 创建一个空的存放点的数组
        while not geoIterator.isDone():
            pointPosition = geoIterator.position()

            pointPosition.x = pointPosition.x + math.sin(geoIterator.index() + displaceValue) * amplitudeValue * \
                              mFloatVectorArray_normal[geoIterator.index()].x * envelopeValue
            pointPosition.y = pointPosition.y + math.sin(geoIterator.index() + displaceValue) * amplitudeValue * \
                              mFloatVectorArray_normal[geoIterator.index()].y * envelopeValue
            pointPosition.z = pointPosition.z + math.sin(geoIterator.index() + displaceValue) * amplitudeValue * \
                              mFloatVectorArray_normal[geoIterator.index()].z * envelopeValue
            # geoIterator.setPosition(pointPosition)
            mPointArray_meshVert.append(pointPosition)
            geoIterator.next()
        geoIterator.setAllPosiions(mPointArray_meshVert)


def deformerCreator():
    nodePtr = OpenMayaMPx.asMPxPtr(Ripple())
    return nodePtr


def nodeInitializer():
    """
    写功能前先将流程写下来，然后每完成一个流程就标记一下那个流程
    Create Attributes  创建属性 - check
    Attach Attributes 附加属性 - check
    Design Circuitry 设计电路图 - check
    """
    # 1. creating a function set for numeric attributes
    # 创建数字属性的函数集，因为我们的自定义属性是数字的，因此创建对应的函数集
    mFnAttr = OpenMaya.MFnNumericAttribute()

    # 2. create the attributes
    # # 创建AttributeValue属性，短名为AttrVal，数据类型为float，默认值为0.0，由自定义类中的mObj_Amplitude（MObject类型）来接收
    Ripple.mObj_Amplitude = mFnAttr.create("AmplitudeValue", "AmplitudeVal", OpenMaya.MFnNumericData.kFloat, 0.0)
    mFnAttr.setKeyable(1)
    mFnAttr.setMin(0.0)
    mFnAttr.setMax(1.0)

    Ripple.mObj_Displace = mFnAttr.create("DisplaceValue", "DispVal", OpenMaya.MFnNumericData.kFloat, 0.0)
    mFnAttr.setKeyable(1)
    mFnAttr.setMin(0.0)
    mFnAttr.setMax(10.0)

    # 3. Attaching the attributes to the Node
    Ripple.addAttribute(Ripple.mObj_Amplitude)
    Ripple.addAttribute(Ripple.mObj_Displace)

    '''
    SWIG - Simplified Wrapper Interface Generator 简化 包装器 接口 生成器   
    是允许开发人员使用脚本语言包装C++代码的工具,因为maya核心是由C++编写的
    Autodesk 为我们提供了一种使用swig使用这些属性的方法
    '''
    outputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

    # 4. Design circuitry
    Ripple.attributeAffects(Ripple.mObj_Amplitude, outputGeom)
    Ripple.attributeAffects(Ripple.mObj_Displace, outputGeom)


# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Violet", "1.0")  # maya准备mobject来创建一个针对Plugin的函数库,第二，三个参数为可选参数，分别代指编写人，版本号
    try:
        # 注册一个节点，第一个为节点名字，第二个为节点ID，第三个为创建节点指针的函数，第四个为节点初始化(定义节点的属性函数)，第五个为节点的分类（没有也不会报错，但是最好写上）
        mplugin.registerNode(nodeName, nodeId, deformerCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write("Failed to register node: " + nodeName)  # 如果注册失败就输出错误
        raise


# Uninitialize the scrip plug-in
def uninitializePlugin(mobject):  # 取消初始化
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(nodeId)  # 使用函数库中的取消注册命令，只需要命令的名字不需要指针
    except:
        sys.stderr.write("Failed to de-register node: " + nodeName)  # 失败就输出错误
        raise
