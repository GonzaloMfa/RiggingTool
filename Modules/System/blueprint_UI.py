import maya.cmds as cmds
import Modules.System.utils as utils
import importlib
importlib.reload(utils)

class Blueprint_UI:
    def __init__(self):
        # Store UI elements into a dictionary
        self.UIElements = {}
        try:
            if cmds.window("blueprint_UI_window", e=True):
                cmds.delete("blueprint_UI_window")
        except:
            pass
        windowWidth = 400
        windowHeight = 598

        self.UIElements["window"] = cmds.window("blueprint_UI_window", w= windowWidth, h= windowHeight, title= "GM21 Blueprint Module V.01", sizeable=False)
        self.UIElements["topLevelColumn"] = cmds.columnLayout(adjustableColumn=True , columnAlign ="center")

        # setup tabs
        tabHeight = 500
        self.UIElements["tabs"] = cmds.tabLayout(h= tabHeight, innerMarginWidth=5, innerMarginHeight=5)
        tabWidth = cmds.tabLayout(self.UIElements["tabs"], q=True, w=True)
        self.scrollWidth = tabWidth-40
        self.initialiseModuleTab(tabWidth, tabHeight)

        cmds.tabLayout(self.UIElements["tabs"], e=True, tabLabelIndex = ([1, "Modules"]))

        # Display window
        cmds.showWindow(self.UIElements["window"])

    def initialiseModuleTab(self, tabHeight, tabWidth):
        scrollHeight = tabHeight # temp value

        self.UIElements["moduleColumn"] = cmds.columnLayout(adj=True, rs=3)

        self.UIElements["moduleFrameLayout"] = cmds.frameLayout(h=scrollHeight, collapsable=False, borderVisible= False, labelVisible= False)

        self.UIElements["moduleList_Scroll"] = cmds.scrollLayout(hst=0)

        self.UIElements["moduleList_column"] = cmds.columnLayout(columnWidth = self.scrollWidth, adj=True, rs=2)

        # First separator
        cmds.separator()

        utils.findAllModules("Modules\Blueprint")