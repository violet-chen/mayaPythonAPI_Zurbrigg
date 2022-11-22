# coding: utf-8
import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    """ 告知maya，使用的是maya api 2.0 """
    pass


class HelloWorldCmd(om.MPxCommand):
    COMMAND_NAME = "HelloWorld"

    def __init__(self):
        super(HelloWorldCmd, self).__init__()

    def doIt(self, args):
        """ 执行的命令 """
        print("Hello, World!")

    @classmethod
    def creator(cls):
        """ 注册maya命令时使用的方法，用来得到类的实例 """
        return HelloWorldCmd()


def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件

    try:
        # 向maya注册一个新命令,第一个参数是命令的名字，第二个参数是类的实例
        plugin_fn.registerCommand(HelloWorldCmd.COMMAND_NAME, HelloWorldCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(HelloWorldCmd))  # 注册失败时输出


def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数 """
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterCommand(HelloWorldCmd.COMMAND_NAME)  # 取消注册新命令
    except:
        om.MGlobal.displayError("Failed to deregister command: {0}".format(HelloWorldCmd))  # 取消注册失败时输出


if __name__ == '__main__':
    plugin_name = "command_01_HelloWorld.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))
