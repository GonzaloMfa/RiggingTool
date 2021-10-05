import maya.cmds as cmds
from functools import partial
import Modules.System.utils as utils
import importlib
importlib.reload(utils)

class Blueprint_UI:
    def __init__(self):
        # Store UI elements into a dictionary
        self.UIElements = {}
        if cmds.window("blueprint_UI_window", exists=True):
            cmds.deleteUI("blueprint_UI_window")


        windowWidth = 400
        windowHeight = 598

        self.UIElements["window"] = cmds.window("blueprint_UI_window", w= windowWidth, h= windowHeight, title= "GM21 Blueprint Module V.01", sizeable=False)
        self.UIElements["topLevelColumn"] = cmds.columnLayout(adjustableColumn=True , columnAlign ="center")

        # setup tabs
        tabHeight = 500
        self.UIElements["tabs"] = cmds.tabLayout(h=tabHeight, innerMarginWidth=5, innerMarginHeight=5)
        tabWidth = cmds.tabLayout(self.UIElements["tabs"], q=True, w=True)
        self.scrollWidth = 220
        self.initialiseModuleTab(tabWidth, tabHeight)

        cmds.tabLayout(self.UIElements["tabs"], e=True, tabLabelIndex=([1, "Modules"]))

        # Display window
        cmds.showWindow(self.UIElements["window"])

    def initialiseModuleTab(self, tabHeight, tabWidth):
        scrollHeight = tabHeight# temp value

        self.UIElements["moduleColumn"] = cmds.columnLayout(adj=True, rs=3)

        self.UIElements["moduleFrameLayout"] = cmds.frameLayout(h=150, collapsable=False, borderVisible= False, labelVisible= False)

        self.UIElements["moduleList_Scroll"] = cmds.scrollLayout(hst=0)

        self.UIElements["moduleList_column"] = cmds.columnLayout(columnWidth= tabWidth, adj=True, rs=2)

        # First separator
        cmds.separator()

        for modules in utils.findAllModules("Modules\Blueprint"):
            self.createModuleInstallButton(modules)
            cmds.setParent(self.UIElements["moduleList_column"])
            cmds.separator()
        cmds.setParent(self.UIElements["moduleColumn"])
        cmds.separator()

    def createModuleInstallButton(self, module):
        mod = __import__("Modules.Blueprint." + module,{}, {}, [module])
        importlib.reload(mod)

        title = mod.TITLE
        description = mod.DESCRIPTION
        icon = mod.ICON

        # Create UI
        buttonSize = 64
        row = cmds.rowLayout(numberOfColumns=2,h=100, columnWidth=([1, buttonSize]), adjustableColumn=2, columnAttach= ([1,"both",0],[2, "both", 5]))
        self.UIElements["module_button_{}".format(module)] = cmds.symbolButton(w=buttonSize, h=buttonSize, i=icon, command=partial(self.installModule,module))

        textColumn = cmds.columnLayout(columnAlign ="center")
        cmds.text(align="center", w=(self.scrollWidth + 10), l=title)

        cmds.scrollField(text=description, e=False, w=self.scrollWidth+50, wordWrap=True)

        cmds.setParent(self.UIElements["moduleList_column"])
        cmds.separator()
    def installModule(self, module, *args):
        basename = "instance_"
        cmds.namespace(setNamespace=":")
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True)

        for i in range(len(namespaces)):
            if namespaces[i].find("__") != -1:
                namespaces[i] = namespaces[i].partition("__")[2]

        newSuffix = utils.findHighestTrailingNumber(namespaces, basename)+1

        userSpecName = basename + str(newSuffix)


        mod = __import__("Modules.Blueprint." + module, {}, {}, [module])
        importlib.reload(mod)
        moduleClass =getattr(mod, mod.CLASS_NAME) # module reference with out parentesis
        moduleInstance = moduleClass(userSpecName)# module instance with parentesis
        moduleInstance.install()

        moduleTransform = mod.CLASS_NAME +"__"+userSpecName+":module_transform"
        cmds.select(moduleTransform, r=True)
        cmds.setToolTo("moveSuperContext")
