import importlib

import maya.cmds as cmds
def findAllModules(relativeDirectory):
    # Search the modules directory for all available mdules
    # Return a list of all module names (excluding the ".py" extension)
    allPyFiles = findAllFiles(relativeDirectory, ".py")

    returnModules = []
    for file in allPyFiles:
        if file != "__init__":
            returnModules.append(file)
    return returnModules

def findAllModulesNames(relativeDirectory):
    validModules = findAllModules(relativeDirectory)

    validModulesName = []

    #packageFolder = relativeDirectory.partition("/Modules/")[2]
    #print(packageFolder)

    for m in validModules:
        print(m)
        mod = __import__("Modules.Blueprint." + m, {}, {}, [m])
        importlib.reload(mod)
        validModulesName.append(mod.CLASS_NAME)
    return(validModules, validModulesName)


def findAllFiles(relativeDirectory, fileExtension):
    # search the relative directory for all files with the given extension
    # return a list of all file names, excluding the file extension

    import os
    fileDirectory = os.environ["RIGGING_TOOL_ROOT"] +"/"+ relativeDirectory + "/"

    allFiles = os.listdir(fileDirectory)
    # refine all files, listing only those of the specified file extension
    returnFiles = []
    for f in allFiles:
        splitStr = str(f).rpartition(fileExtension)
        if not splitStr[1] == "" and splitStr[2] == "":
            returnFiles.append(splitStr[0])

    return returnFiles

def findHighestTrailingNumber(names, basename):
    import re
    highestValue = 0

    for n in names:
        if n.find(basename)==0:
            suffix = n.partition(basename)[2]
            if re.match("^[0-9]*$", suffix):
                numericalElement = int(suffix)
                if numericalElement > highestValue:
                    highestValue = numericalElement
    return highestValue
def stripLeadingNamespace(nodeName):
    '''

    :param nodeName:
    :return:
    '''
    if str(nodeName).find(":")==-1:
        return None
    splitString = str(nodeName).partition(":")
    return [splitString[0], splitString[2]]

def stripAllNamespaces(nodeName):
    '''

    :param nodeName:
    :return:
    '''
    if str(nodeName).find(":")==-1:
        return None
    splitString = str(nodeName).rpartition(":")
    return [splitString[0], splitString[2]]

def basic_stretchy_IK(rootJoint, endJoint, container=None, lockMinimumLength=True, poleVectorObject=None,scaleCorrectionAttr=None):
    '''

    :param rootJoint:
    :param endJoint:
    :param container:
    :param lockMinimumLength:
    :param poleVectorObject:
    :param scaleCorrectionAttr:
    :return:
    '''
    from math import fabs
    containedNodes = []

    totalOriginalLength = 0.0
    done = False
    parent = rootJoint
    childJoints = []
    while not done:
        children = cmds.listRelatives(parent, children=True)
        children = cmds.ls(children, type="joint")
        if len(children)==0:
            done=True
        else:
            child = children[0]
            childJoints.append(child)

            totalOriginalLength += fabs(cmds.getAttr('{}.translateX'.format(child)))

            parent = child
            if child == endJoint:
                done=True

    # Create RP IK on joint chain
    ikNodes = cmds.ikHandle(sj=rootJoint, ee=endJoint, sol="ikRPsolver", n='{}_ikHandle'.format(rootJoint))

    ikNodes[1] = cmds.rename(ikNodes[1], '{}_ikEffector'.format(rootJoint))
    ikEffector = ikNodes[1]
    ikHandle = ikNodes[0]
    print("# Result: creating ik Effector -> {} #".format(ikEffector))
    print("# Result: creating ik Handle -> {} #".format(ikHandle))

    cmds.setAttr('{}.visibility'.format(ikHandle), 0)

    containedNodes.extend(ikNodes)# extends introduce a list of objects to the list

    # create pole vector locator
    if poleVectorObject == None:
        poleVectorObject = cmds.spaceLocator(n='{}_poleVectorLocator'.format(ikHandle))[0]
        containedNodes.append(poleVectorObject)
        cmds.xform(poleVectorObject, ws=True, a=True, t=cmds.xform(rootJoint, ws=True, q=True, t=True))
        cmds.xform(poleVectorObject, ws=True, r=True, t=[0.0, 1.0, 0.0])
        cmds.setAttr('{}.visibility'.format(poleVectorObject), 0)
        print("# Result: creating pv object -> {} #".format(poleVectorObject))
    poleVectorConstraint = cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    containedNodes.append(poleVectorConstraint)
    print("# Result: creating pole vector Constraint -> {} #".format(poleVectorConstraint))

    # Create root and end locators
    rootLocator = cmds.spaceLocator(n='{}_rootPosLocator'.format(rootJoint))[0]
    rootLocator_pointConstraint = cmds.pointConstraint(rootJoint, rootLocator, mo=False, n= '{}_pointConstraint'.format(rootLocator))[0]
    print("# Result: creating root Locator -> {} #".format(rootLocator))
    endLocator = cmds.spaceLocator(n='{}_endPosLocator'.format(endJoint))[0]
    cmds.xform(endLocator, ws=True, a=True, t=cmds.xform(ikHandle, ws=True, q=True, t=True))
    ikHandle_pointConstraint = cmds.pointConstraint(endLocator, ikHandle, mo=False, n='{}_pointConstraint'.format(ikHandle))[0]
    print("# Result: creating end Locator -> {} #".format(endLocator))

    containedNodes.extend([rootLocator,endLocator, rootLocator_pointConstraint, ikHandle_pointConstraint])
    cmds.setAttr('{}.visibility'.format(rootLocator), 0)
    cmds.setAttr('{}.visibility'.format(endLocator), 0)

    # Grab distance between locators
    rootLocatorWithoutNamespace = stripAllNamespaces(rootLocator)[1]
    endLocatorWithoutNamespace = stripAllNamespaces(endLocator)[1]

    moduleNamespace = stripAllNamespaces(rootJoint)[0]
    distNode = cmds.shadingNode("distanceBetween", asUtility=True, n='{}:distBetween_{}_{}'.format(moduleNamespace, rootLocatorWithoutNamespace, endLocatorWithoutNamespace))
    containedNodes.append(distNode)

    cmds.connectAttr('{}Shape.worldPosition[0]'.format(rootLocator), '{}.point1'.format(distNode))
    cmds.connectAttr('{}Shape.worldPosition[0]'.format(endLocator), '{}.point2'.format(distNode))

    scaleAttr = '{}.distance'.format(distNode)

    # Divide distance by total original length = scale factor
    scaleFactor = cmds.shadingNode('multiplyDivide', asUtility=True, n='{}_scaleFactor'.format(ikHandle))
    containedNodes.append(scaleFactor)

    cmds.setAttr('{}.operation'.format(scaleFactor), 2)# Divide
    cmds.connectAttr(scaleAttr, '{}.input1X'.format(scaleFactor))
    cmds.setAttr('{}.input2X'.format(scaleFactor), totalOriginalLength)

    translationDriver = '{}.outputX'.format(scaleFactor)

    # Connect joints to stretchy calculations
    for joint in childJoints:
        multNode = cmds.shadingNode('multiplyDivide', asUtility=True, n='{}_scaleMult'.format(joint))
        containedNodes.append(multNode)
        cmds.setAttr('{}.input1X'.format(multNode), cmds.getAttr('{}.translateX'.format(joint)))
        cmds.connectAttr(translationDriver, '{}.input2X'.format(multNode))
        cmds.connectAttr('{}.outputX'.format(multNode), '{}.translateX'.format(joint))


    if container !=None:
        addNodeToContainer(container, containedNodes, ihb=True)
    returnDict = {}
    returnDict["ikHandle"] = ikHandle
    returnDict["ikEffector"] = ikEffector
    returnDict["rootLocator"] = rootLocator
    returnDict["endLocator"] = endLocator
    returnDict["poleVectorObject"] = poleVectorObject
    returnDict["ikHandle_pointConstraint"] = ikHandle_pointConstraint
    returnDict["rootLocator_pointConstraint"] = rootLocator_pointConstraint



    return returnDict

def forceSceneUpdate():
    cmds.setToolTo("moveSuperContext")
    nodes = cmds.ls()
    for node in nodes:
        cmds.select(node, replace=True)

    cmds.select(cl=True)
    cmds.setToolTo("selectSuperContext")
def addNodeToContainer(container, nodesIn, ihb=False, includeShapes=False, force=False):
    '''

    :param container:
    :param nodesIn:
    :param ihb:
    :param includeShapes:
    :param force:
    :return:
    '''
    import typing

    nodes = []

    if type(nodesIn) is typing.List:
        nodes = list(nodesIn)
    else:
        nodes = [nodesIn]

    conversionNodes =[]
    for node in nodes:
        node_conversionNodes = cmds.listConnections(node, s=True, destination=True)
        node_conversionNodes = cmds.ls(node_conversionNodes, type='unitConversion')

        conversionNodes.extend(node_conversionNodes)

    nodes.extend(conversionNodes)
    cmds.container(container, e=True, addNode=nodes[0], ihb=ihb, includeShapes=includeShapes, force=force)
