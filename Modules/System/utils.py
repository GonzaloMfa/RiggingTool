def findAllModules(relativeDirectory):
    # Search the modules directory for all available mdules
    # Return a list of all module names (excluding the ".py" extension)
    allPyFiles = findAllFiles(relativeDirectory, ".py")

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
        splitStr = [before, fileExtension, after]

    print(allFiles)