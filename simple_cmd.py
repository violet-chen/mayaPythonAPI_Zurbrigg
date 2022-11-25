# coding: utf-8
import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass


class SimpleCmd(om.MPxCommand):
    COMMAND_NAME = "SimpleCmd"
    # 定义命令的标志
    TRANSLATE_FLAG = ["-t", "-translate", (om.MSyntax.kDouble,om.MSyntax.kDouble,om.MSyntax.kDouble)]
    VERSION_FLAG = ["-v", "-version"]

    def __init__(self):
        super(SimpleCmd, self).__init__()

        self.undoable = False  # 初始设置命令不能撤回

    def doIt(self, arg_list):
        """ 
        doIt 通常用来进行执行redoIt的初始设置以及检查
        doIt 在使用命令时只调用一次
        """

        try:
            arg_db = om.MArgDatabase(self.syntax(), arg_list) # 创建对象解析语法与参数
        except:
            self.displayError("Error parsing arguments")
            raise
        
        selection_list = arg_db.getObjectList()

        self.selected_obj = selection_list.getDependNode(0)
        # om.MFn为所有API类型提供常量的静态类
        # om.MSpace 提供坐标空间常量的静态类。
        if self.selected_obj.apiType() != om.MFn.kTransform:
            raise RuntimeError("This command requires a transform node")
        
        self.edit = arg_db.isEdit
        self.query = arg_db.isQuery

        self.translate = arg_db.isFlagSet(SimpleCmd.TRANSLATE_FLAG[0]) # 判断语法中是否有这个flag
        if self.translate:
            transform_fn = om.MFnTransform(self.selected_obj)
            self.orig_translation = transform_fn.translation(om.MSpace.kTransform)  

            if self.edit:
                self.new_translation = [arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0],0),
                                        arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0],1),
                                        arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0],2)]
                self.undoable = True

        self.version = arg_db.isFlagSet(SimpleCmd.VERSION_FLAG[0])

        self.redoIt()

    def undoIt(self):
        transform_fn = om.MFnTransform(self.selected_obj)
        transform_fn.setTranslation(om.MVector(self.orig_translation),om.MSpace.kTransform)

    def redoIt(self):
        transform_fn = om.MFnTransform(self.selected_obj)

        if self.query:
            if self.translate:
                self.setResult(self.orig_translation)
            else:
                raise RuntimeError("Flag does not support query")
        
        elif self.edit:
            if self.translate:
                transform_fn.setTranslation(om.MVector(self.new_translation),om.MSpace.kTransform)
            else:
                raise RuntimeError("Flag does not support edit")
        
        elif self.version:
            self.setResult("1.0.0")
        else:
            self.setResult(transform_fn.name())

    def isUndoable(self):
        return self.undoable

    @classmethod
    def creator(cls):
        """ 注册maya命令时使用的方法，用来得到类的实例 """
        return SimpleCmd()

    @classmethod
    def create_syntax(cls):

        syntax = om.MSyntax()

        syntax.enableEdit = True
        syntax.enableQuery = True

        syntax.addFlag(*cls.TRANSLATE_FLAG) # 这里*的意思是解包，相当于将列表的中括号去掉
        syntax.addFlag(*cls.VERSION_FLAG)

        # 设置要传递给命令的对象的类型和数量
        syntax.setObjectType(om.MSyntax.kSelectionList, 1, 1) 
        # 如果设置为True，那么当命令行上没有提供对象时，Maya将传递当前选择。默认为False。
        syntax.useSelectionAsDefault(True)

        return syntax


def initializePlugin(plugin):
    """ 插件加载时执行这个函数"""
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本

    plugin_fn = om.MFnPlugin(plugin, vendor, version)  # 定义插件

    try:
        # 向maya注册一个新命令,第一个参数是命令的名字，第二个参数是类的实例, 第三个参数是命令的语法
        plugin_fn.registerCommand(SimpleCmd.COMMAND_NAME, SimpleCmd.creator, SimpleCmd.create_syntax)
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(SimpleCmd.COMMAND_NAME))  # 注册失败时输出


def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数 """
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterCommand(SimpleCmd.COMMAND_NAME)  # 取消注册新命令
    except:
        om.MGlobal.displayError("Failed to deregister command: {0}".format(SimpleCmd.COMMAND_NAME))  # 取消注册失败时输出


if __name__ == '__main__':
    cmds.file(new=True, force=True)

    plugin_name = "simple_cmd.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.polyCube()')