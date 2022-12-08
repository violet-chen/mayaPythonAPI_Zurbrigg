# coding: utf-8
import maya.api.OpenMaya as om
import maya.cmds as cmds

def maya_useNewAPI():
    """ 告知maya，使用的是maya api 2.0 """
    pass

def initializePlugin(plugin): 
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    om.MFnPlugin(plugin, vendor, version)  # 定义插件

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    pass

if __name__ == '__main__':
    """ 注册后，在maya脚本编辑器中的使用方法 """
    plugin_name = "empty_plugin.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
