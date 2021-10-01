
CLASS_NAME = "ModuleA"

TITLE = "Module A"
DESCRIPTION = "Test description for module A"
ICON = "D:\Maya2022\scripts\GM21_Rig\RiggingTool\Icons\hand.png"

class ModuleA():
    def __init__(self):
        print("We're in the constructor")
    def install(self):
        print("Install " + CLASS_NAME)