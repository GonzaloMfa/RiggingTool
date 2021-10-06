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
        self.scrollWidth = 340
        self.initialiseModuleTab(tabWidth, tabHeight)

        cmds.tabLayout(self.UIElements["tabs"], e=True, tabLabelIndex=([1, "Modules"]))

        cmds.setParent(self.UIElements["topLevelColumn"])
        self.UIElements["lockPublishColumn"] = cmds.columnLayout(adj=True, columnAlign="center", rs=3)

        cmds.separator()

        self.UIElements["lockBtn"] = cmds.button(l="Lock", c=self.lock)

        cmds.separator()

        self.UIElements["publishBtn"] = cmds.button(l="Publish")

        cmds.separator()


        # Display window
        cmds.showWindow(self.UIElements["window"])

    def initialiseModuleTab(self, tabHeight, tabWidth):

        scrollHeight = tabHeight# temp value

        self.UIElements["moduleColumn"] = cmds.columnLayout(adj=True, rs=3)

        self.UIElements["moduleFrameLayout"] = cmds.frameLayout(h=scrollHeight+250, collapsable=False, borderVisible= False, labelVisible= False)

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

        self.UIElements["moduleName_row"] = cmds.rowLayout(nc=2, columnAttach=(1, "right",0), columnWidth=[(1, 80)], adjustableColumn=2)
        cmds.text(l="Module Name :")
        self.UIElements["moduleName"]= cmds.textField(enable=False, alwaysInvokeEnterCommandOnReturn=True)

        cmds.setParent(self.UIElements["moduleColumn"])
        columnWidth = (tabWidth - 20)/3
        self.UIElements["moduleButtons_rowColumn"] = cmds.rowColumnLayout(numberOfColumns=3,
                                                                          ro = [(1, "both",2),(2, "both",2),(3, "both",2)],
                                                                          columnAttach=[(1,"both",3), (2,"both",3), (3,"both",3)],
                                                                          columnWidth=[(1, columnWidth),(2, columnWidth),(3, columnWidth)])
        self.UIElements["rehookBtn"] = cmds.button(enable=False, label="Re-hook")
        self.UIElements["snapRootBtn"] = cmds.button(enable=False, label="Snap Root > Hook")
        self.UIElements["constrainRootBtn"] = cmds.button(enable=False, label="Constrain Root > Hook")

        self.UIElements["groupSelectedBtn"] = cmds.button(label="Group Selected")
        self.UIElements["ungroupBtn"] = cmds.button(enable=False, label="Ungroup")
        self.UIElements["mirrrorModuleBtn"] = cmds.button(enable=False, label="Mirror Module")

        cmds.text(l="")
        self.UIElements["deleteModuleBtn"] = cmds.button(enable=False, label="Delete Module")
        self.UIElements["symmetryMoveCheckBox"] = cmds.checkBox(enable=True, l="Symmetry Move")

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

    def lock(self, *args):
        result = cmds.confirmDialog(messageAlign="center", title="Lock Blueprints",
                                    message="The action of locking a character will convert the current blueprint modules"
                                            "to joints. \nThis action cannot be undone. \nModifications to the "
                                            "cannot be made after this point. \nDo you want to continue?",
                                    button=["Accept", "Cancel"], defaultButton="Accept", cancelButton="Cancel",
                                    dismissString="Cancel")
        if result != "Accept":
            return
        moduleInfo =[] # store (module, userSpecifiedName) pairs
        cmds.namespace(setNamespace=":")
        namespace = cmds.namespaceInfo(listOnlyNamespaces=True)

        # ensuring the namespaces contains a blueprint
        moduleNameInfo = utils.findAllModulesNames("Modules/Blueprint")

        validModules = moduleNameInfo[0]
        validModulesNames = moduleNameInfo[1]

        for n in namespace:
            splitString = n.partition("__")

            if splitString[1] != "":
                module = splitString[0]
                userSpecifiedName = splitString[2]

                if module in validModulesNames:
                    index = validModulesNames.index(module)
                    moduleInfo.append([validModules[index], userSpecifiedName])
        if len(moduleInfo) == 0:
            cmds.confirmDialog(messageAlign="center", title="Lock Blueprints",
                                        message="There appear to be no blueprint module "
                                                "\ninstances in the current scene. \nAbborting lock.",
                                        button=["Accept"], defaultButton="Accept")
            return
        moduleInstances = []

        for module in moduleInfo:
            mod = __import__("Modules.Blueprint.{}".format(module[0]), {}, {}, [module[0]])
            importlib.reload(mod)

            moduleClass = getattr(mod, mod.CLASS_NAME)
            moduleInst = moduleClass(userSpecifiedName=module[1])

            moduleInst.lock_phase1()