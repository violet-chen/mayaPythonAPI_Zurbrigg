# coding:utf-8
import maya.api.OpenMaya as om
selection_list = om.MGlobal.getActiveSelectionList()  # 获取当前选择的对象并为其创建列表
traversal_type = om.MItDag.kBreadthFirst # 遍历方式为广度优先（默认是深度优先）
filter_type = om.MFn.kMesh # 过滤器设置，只遍历kMesh类型
dag_iter = om.MItDag(traversal_type,filter_type) # 创建迭代器，并指定遍历方式和遍历类型

if not selection_list.isEmpty():
    
    dag_fn = om.MFnDagNode(selection_list.getDependNode(0))

    #print("Child:")
    for i in range(dag_fn.childCount()):
        child_obj = dag_fn.child(i)
        child_fn = om.MFnDagNode(child_obj)
        #print(child_fn.fullPathName())

    #print("Parent:")
    for i in range(dag_fn.parentCount()):
        parent_obj = dag_fn.parent(i)
        parent_fn = om.MFnDagNode(parent_obj)
        #print(parent_fn.fullPathName())

    # 如果场景中有选择的物体，那么就以选择的物体为迭代起始点
    dag_iter.reset(selection_list.getDependNode(0),traversal_type,filter_type) 
    while not dag_iter.isDone():
        # print(dag_iter.partialPathName()) # 输出短名
        # print(dag_iter.fullPathName()) # 输出长名
        # dag_path = dag_iter.getPath() # 获取dagpath对象
        # print(dag_path.fullPathName()) # 输出dagpath对象的长名

        # 迭代器遍历类型为kmesh，然后通过类型为kmesh的shape节点得到父节点transform的名字
        shape_obj = dag_iter.currentItem()
        dag_fn = om.MFnDagNode(shape_obj)
        dag_fn = om.MFnDagNode(shape_obj)
        for i in range(dag_fn.parentCount()):
            parent_fn = om.MFnDagNode(dag_fn.parent(i))
            print(parent_fn.fullPathName())

        dag_iter.next()