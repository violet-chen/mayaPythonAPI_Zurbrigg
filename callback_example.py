# coding: utf-8
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds

def maya_useNewAPI():
    """ 告知maya,使用的是maya api 2.0 """
    pass

callback_ids = [] # 定义全局变量存放callback_id

def on_new_scene(client_data):
    """ 当新场景加载时调用,client_data为调用这个函数时传递的参数(可以为None) """
    print("New Scene opened")

def on_time_changed(client_data):
    """ 当时间轴发生改变时调用 """
    print("Time changed: {0}".format(oma.MAnimControl.currentTime().asUnits(om.MTime.uiUnit()))) # 输出当前时间轴的帧数

def on_selection_changed(client_data):
    """ 当选择发生改变时调用 """
    print("Selection changed")

def before_import(client_data):
    """ 导入前执行 """
    print("Import pre-processing")

def after_import(client_data):
    """ 导入后执行 """
    print("Import post-processing")

def on_viewport_changed(model_panel,*args):
    """ 在指定的视口面板处切换相机时调用 """
    print("Camera changed in model panel {0}".format(model_panel))

def on_playing_back_state_changed(is_playing, client_data):
    """ 当使用播放键预览拍屏时调用 """
    print("Playing state changed: {0}".format(is_playing))

def on_timer_fired(elapsed_time, previous_execution_time, client_data):
    """ 
    定时器调用此函数,每经过设定的秒数就调用一次这个函数
    Args:
        elapsed_time (float): 设定的秒数
        previous_execution_time (_type_): 以前的运行的时间，为了防止此函数还没执行完就再次被调用
        client_data (_type_): 用户自定义的参数,可以不传递
    """
    print("Timer fired")

def initializePlugin(plugin): 
    """ 插件加载时执行这个函数"""
    global callback_ids # 调用全局变量
    vendor = "RuiChen"  # 插件制作人的名字
    version = "1.0.0"  # 插件的版本
    # 注册回调，参数为事件类型名，回调函数，还有第三个参数可选（传递给回调函数的参数），返回值为回调函数id
    callback_ids.append(om.MEventMessage.addEventCallback("NewSceneOpened", on_new_scene)) 
    #callback_ids.append(om.MEventMessage.addEventCallback("timeChanged", on_time_changed))
    callback_ids.append(om.MEventMessage.addEventCallback("SelectionChanged", on_selection_changed))

    callback_ids.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeImport, before_import))
    callback_ids.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterImport, after_import))

    callback_ids.append(om.MConditionMessage.addConditionCallback("playingBack", on_playing_back_state_changed))
    
    callback_ids.append(omui.MUiMessage.addCameraChangedCallback("modelPanel4", on_viewport_changed))

    callback_ids.append(om.MTimerMessage.addTimerCallback(2.5, on_timer_fired))

    om.MFnPlugin(plugin, vendor, version)  # 定义插件

def uninitializePlugin(plugin):
    """ 插件取消加载时执行这个函数"""
    global callback_ids
    om.MEventMessage.removeCallbacks(callback_ids)
    callback_ids = []

if __name__ == '__main__':
    """ 注册后,在maya脚本编辑器中的使用方法 """
    plugin_name = "callback_example.py"  # 插件的文件名
    # 如果插件加载了就先取消加载插件
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    # 如果插件没有加载就加载插件
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))