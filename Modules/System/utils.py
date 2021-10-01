def findAllModules(relativeDirectory):
    # Search the modules directory for all available mdules
    # Return a list of all module names (excluding the ".py" extension)
    allPyFiles = findAllFiles(relativeDirectory, ".py")

    returnModules = []
    for file in allPyFiles:
        if file != "__init__":
            returnModules.append(file)

    return returnModules

def findAllFiles(relativeDirectory, fileExtension):
    # search the relative directory for all files with the given extension
    # return a list of all file names, excluding the file extension

    import os
    fileDirectory = "D:/Maya2022/scripts/GM21_Rig/RiggingTool/" + relativeDirectory + "/"
    allFiles = os.listdir(fileDirectory)
    # refine all files, listing only those of the specified file extension
    returnFiles = []
    for f in allFiles:
        splitStr = str(f).rpartition(fileExtension)
        if not splitStr[1] == "" and splitStr[2]=="":
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
    return highestValue