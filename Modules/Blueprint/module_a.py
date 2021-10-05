import maya.cmds as cmds

import Modules.System.utils as utils
import importlib
importlib.reload(utils)

CLASS_NAME = "ModuleA"

TITLE = "Module A"
DESCRIPTION = "Test description for module A"
ICON = "D:\Maya2022\scripts\GM21_Rig\RiggingTool\Icons\hand.png"

class ModuleA():
    def __init__(self, userSpecifiedName):
        self.moduleName = CLASS_NAME
        self.userSpecifiedName = userSpecifiedName

        self.moduleNameSpace = self.moduleName + "__" + self.userSpecifiedName

        print(self.moduleNameSpace)
        self.containerName = self.moduleNameSpace + ":module_container"

        # joint info list
        self.jointInfo = [["root", [0.0, 0.0, 0.0]], ["end_joint", [4.0, 0.0, 0.0]]]
    def install(self):
        '''
        in the install method we create all the functionality for the first module
        :return:
        '''
        cmds.namespace(setNamespace=":")
        cmds.namespace(add=self.moduleNameSpace)
        print("#######################################################################################################")
        print("############################################## MODULE A ###############################################")
        print("#######################################################################################################")
        # Creating a module group
        self.jointsGrp = cmds.createNode('transform', n="{}:joint_grp".format(self.moduleNameSpace))
        print("# Result: Creating joints grp -> {} #".format(self.jointsGrp))
        self.hierarchyRepGrp = cmds.createNode('transform', n="{}:hierarchyRepresentation_grp".format(self.moduleNameSpace))
        print("# Result: Creating joints grp -> {} #".format(self.jointsGrp))
        self.orientationCtrlGrp = cmds.createNode('transform', n="{}:orientationCtrl_grp".format(self.moduleNameSpace))
        print("# Result: Creating joints grp -> {} #".format(self.jointsGrp))

        self.moduleGrp = cmds.createNode('transform', n="{}:module_grp".format(self.moduleNameSpace))
        print("# Result: Creating module grp -> {} #".format(self.moduleGrp))
        cmds.parent([self.jointsGrp,self.hierarchyRepGrp, self.orientationCtrlGrp], self.moduleGrp)

        # Creating container for node editor
        cmds.container(name=self.containerName, addNode=self.moduleGrp, ihb=True)
        print("# Result: Creating module container -> {} #".format(self.containerName))
        cmds.select(clear=True)
        # creating joints
        index = 0
        joints = []
        for joint in self.jointInfo:
            # getting joints info from joint list Info
            jointName = joint[0]
            jointPos = joint[1]

            parentJoint = ""
            if index > 0:
                parentJoint = self.moduleNameSpace+":"+self.jointInfo[index-1][0]
                cmds.select(parentJoint, replace=True)
            jointNameFull = cmds.joint(n=self.moduleNameSpace+":"+jointName, p= jointPos)
            joints.append(jointNameFull)

            cmds.setAttr('{}.visibility'.format(jointNameFull),0)

            utils.addNodeToContainer(self.containerName, jointNameFull)
            cmds.container(self.containerName, edit=True, publishAndBind=['{}.rotate'.format(jointNameFull), '{}_R'.format(jointName)])
            cmds.container(self.containerName, edit=True, publishAndBind=['{}.rotateOrder'.format(jointNameFull), '{}_rotateOrder'.format(jointName)])


            if index > 0:
                cmds.joint(parentJoint, e=True,orientJoint='xyz', sao="yup")
            index += 1
        cmds.parent(joints[0], self.jointsGrp, absolute=True)

        self.initialiseModuleTransform(self.jointInfo[0][1])

        translationCtrls = []
        for joint in joints:
            translationCtrls.append(self.createTranslationControlAtJoint(joint))
            print("# Result: creating translation ctrls -> {} #".format(joint))
        rootjoint_pointConstraint = cmds.pointConstraint(translationCtrls[0], joints[0], mo=False, n='{}_pointConstraint'.format(joints[0]))
        utils.addNodeToContainer(self.containerName, rootjoint_pointConstraint[0])

        # setup stretchy joint segments
        for index in range(len(joints)-1):
            self.setupStretchyJointSegment(joints[index], joints[index+1])

        #  NON DEFAULT FUNCTIONALITY
        self.createOrientationCtrl(joints[0], joints[1])


        utils.forceSceneUpdate()
        cmds.lockNode(self.containerName, lock=True, lockUnpublished=True)
    def createTranslationControlAtJoint(self, joint):
        '''
        function that creates a translation ctrl for a given joint
        :param joint:
        :return:
        '''
        print("##########################################TRANSLATION CTRL#############################################")
        posControlFile = "D:/Maya2022/scripts/GM21_Rig/RiggingTool/ControlObjects/Blueprint/translation_control.ma"
        cmds.file(posControlFile, i=True)

        print("# Result: importing translation file -> {} #".format(posControlFile))

        container = cmds.rename("translation_ctrl_container", '{}_translation_ctrl_container'.format(joint))
        # Adding control container to the generic container
        utils.addNodeToContainer(self.containerName, container)
        # renaming file container and children
        for node in cmds.container(container, q=True, nodeList=True):
            cmds.rename(node, '{}_{}'.format(joint, node), ignoreShape=True)

        control = '{}_translation_ctrl'.format(joint)

        cmds.parent(control, self.moduleTransform, a=True)

        # getting joint pos
        jointPos = cmds.xform(joint, q=True, ws=True, t=True)

        cmds.xform(control, ws=True, a=True, t=jointPos)

        niceName = utils.stripLeadingNamespace(joint)[1]
        attrName = '{}_T'.format(niceName)

        cmds.container(container, e=True, publishAndBind=['{}.translate'.format(control), attrName])
        cmds.container(self.containerName, e=True, publishAndBind=['{}.{}'.format(container, attrName), attrName])
        return control

    def getTranslationControl(self, jointName):
        '''

        :param jointName:
        :return:
        '''
        return '{}_translation_ctrl'.format(jointName)

    def setupStretchyJointSegment(self, parentJoint, childJoint):
        '''

        :param parentJoint:
        :param childJoint:
        :return:
        '''
        parentTranslationCtrl = self.getTranslationControl(parentJoint)
        childTranslationCtrl = self.getTranslationControl(childJoint)

        poleVectorLocator = cmds.spaceLocator(n='{}_poleVectorLocator'.format(parentTranslationCtrl))[0]

        poleVectorLocatorGrp = cmds.group(poleVectorLocator, n='{}_parentConstraintGrp'.format(poleVectorLocator))
        cmds.parent(poleVectorLocatorGrp, self.moduleGrp, a=True)
        parentConstraint = cmds.parentConstraint(parentTranslationCtrl, poleVectorLocatorGrp, mo=False)[0]
        cmds.setAttr('{}.visibility'.format(poleVectorLocator),0)
        cmds.setAttr('{}.ty'.format(poleVectorLocator),0.5)

        ikNodes = utils.basic_stretchy_IK(parentJoint, childJoint, container=self.containerName, lockMinimumLength=False, poleVectorObject=poleVectorLocator)
        # getting Dic from basic_stretchy
        ikHandle = ikNodes["ikHandle"]
        rootLocator = ikNodes["rootLocator"]
        endLocator = ikNodes["endLocator"]

        childPointConstraint = cmds.pointConstraint(childTranslationCtrl, endLocator, mo=False, n='{}_pointConstraint'.format(endLocator))[0]

        utils.addNodeToContainer(self.containerName, [poleVectorLocatorGrp, parentConstraint, childPointConstraint], ihb=True)
        for node in [ikHandle, rootLocator, endLocator]:
            cmds.parent(node, self.jointsGrp, a=True)
            cmds.setAttr('{}.visibility'.format(node), 0)
        self.createHierarchyRepresentation(parentJoint, childJoint)
    def createHierarchyRepresentation(self, parentJoint, childJoint):
        nodes = self.createStretchyObject("/ControlObjects/Blueprint/hierarchy_representation.ma", "hierarchy_representation_container", "hierarchy_representation",
                                          parentJoint, childJoint)
        constrainedGrp = nodes[2]
        cmds.parent(constrainedGrp, self.hierarchyRepGrp, r=True)



    def createStretchyObject(self, objectRelativeFilePath, objectContainerName, objectName, parentJoint, childJoint):
        '''

        :param objectRelativeFilePath:
        :param objectContainerName:
        :param objectName:
        :param parentJoint:
        :param childJoint:
        :return:
        '''
        objectFile = "D:/Maya2022/scripts/GM21_Rig/RiggingTool/{}".format(objectRelativeFilePath)
        cmds.file(objectFile, i=True)

        objectContainer = cmds.rename(objectContainerName, '{}_{}'.format(parentJoint, objectContainerName))

        for node in cmds.container(objectContainer, q=True, nodeList=True):
            cmds.rename(node, '{}_{}'.format(parentJoint, node), ignoreShape=True)
        object = '{}_{}'.format(parentJoint, objectName)

        constrainedGrp = cmds.group(em=True, n='{}_parentConstraint_grp'.format(object))
        cmds.parent(object, constrainedGrp, a=True)

        parentConstraint = cmds.parentConstraint(parentJoint, constrainedGrp, mo=False)[0]

        cmds.connectAttr('{}.translateX'.format(childJoint),'{}.scaleX'.format(constrainedGrp))
        scaleConstraint = cmds.scaleConstraint(self.moduleTransform, constrainedGrp, skip=["x"],mo=False)[0]

        utils.addNodeToContainer(objectContainer, [constrainedGrp, parentConstraint, scaleConstraint], ihb=True)
        utils.addNodeToContainer(self.containerName, objectContainer)

        return(objectContainer, object, constrainedGrp)

    def initialiseModuleTransform(self, rootPos):
        '''

        :param rootPos:
        :return:
        '''
        ctrlGrpFile = "D:/Maya2022/scripts/GM21_Rig/RiggingTool/ControlObjects/Blueprint/controlGrp_ctrl.ma"
        cmds.file(ctrlGrpFile, i=True)

        self.moduleTransform = cmds.rename('controlGrp_ctrl', '{}:module_transform'.format(self.moduleNameSpace))

        cmds.xform(self.moduleTransform, ws=True, a=True, t=rootPos)
        utils.addNodeToContainer(self.containerName, self.moduleTransform, ihb=True)

        # Setup global scaling
        cmds.connectAttr('{}.scaleY'.format(self.moduleTransform), '{}.scaleX'.format(self.moduleTransform))
        cmds.connectAttr('{}.scaleY'.format(self.moduleTransform), '{}.scaleZ'.format(self.moduleTransform))

        cmds.aliasAttr("globalScale", '{}.scaleY'.format(self.moduleTransform))

        cmds.container(self.containerName, e=True, publishAndBind=['{}.translate'.format(self.moduleTransform), "moduleTransform_T"])
        cmds.container(self.containerName, e=True, publishAndBind=['{}.rotate'.format(self.moduleTransform), "moduleTransform_R"])
        cmds.container(self.containerName, e=True, publishAndBind=['{}.globalScale'.format(self.moduleTransform), "moduleTransform_globalScale"])

    def deleteHierarchyRepresentation(self, parentJoint):
        '''

        :param parentJoint:
        :return:
        '''
        hierarchyContainer = '{}_hierarchy_representation_container'.format(parentJoint)
        cmds.delete(hierarchyContainer)
    def createOrientationCtrl(self, parentJoint, childJoint):
        '''

        :param parentJoint:
        :param childJoint:
        :return:
        '''
        self.deleteHierarchyRepresentation(parentJoint)

        nodes = self.createStretchyObject("/ControlObjects/Blueprint/orientation_ctrl.ma", "orientation_ctrl_container", "orientation_ctrl", parentJoint, childJoint)
        orientationContainer = nodes[0]
        orientationControl = nodes[1]
        constrainedGrp = nodes[2]

        cmds.parent(constrainedGrp, self.orientationCtrlGrp, r=True)
        parentJointWithoutNamespace = utils.stripAllNamespaces(parentJoint)[1]
        attrName = '{}_orientation'.format(parentJointWithoutNamespace)
        cmds.container(orientationContainer, e=True, publishAndBind=['{}.rotateX'.format(orientationControl), attrName])
        cmds.container(self.containerName, e=True, publishAndBind=['{}.{}'.format(orientationContainer, attrName), attrName])

        return orientationControl
