
CLASS_NAME = "ModuleB"

TITLE = "Module B"
DESCRIPTION = "Test description for module B"
ICON = "D:\Maya2022\scripts\GM21_Rig\RiggingTool\Icons\power.png"



class ModuleB():
    def __init__(self):
        print("We're in the constructor")
    def install(self):
        print("Install " + CLASS_NAME)