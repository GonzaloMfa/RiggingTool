'''
    FIRST CLASS -> FIRST BLUEPRINT MODULE
    SIMPLE SEGMENT
'''
import maya.cmds as cmds
import os

import Modules.System.blueprint as blueprintMod
import importlib
importlib.reload(blueprintMod)
import os
CLASS_NAME = "SingleJointSegment"
TITLE = "Single Joint Segment"
DESCRIPTION = "Creates 2 joints, with controls for 1s joint`s orientation and rotation order. Ideal us: clavicle bones/shoulder"
ICON = os.environ["RIGGING_TOOL_ROOT"] + "/Icons/jointSegment.png"

class SingleJointSegment(blueprintMod.Blueprint):
    
    def __init__(self, userSpecifiedName):

        # joint info list
        jointInfo = [["root", [0.0, 0.0, 0.0]], ["end_joint", [4.0, 0.0, 0.0]]]
        blueprintMod.Blueprint.__init__(self, CLASS_NAME, userSpecifiedName, jointInfo)# overwritting blueprint constructor


    def install_custom(self, joints):
        self.createOrientationCtrl(joints[0], joints[1])