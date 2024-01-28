from   typing              import List, Tuple
from   py_linq             import Enumerable
import pathlib
import github_action_utils

def checkEncoding(file:pathlib.Path, encoding:str) -> bool:
    """
    Check if the file is encoded with the specified encoding.

    Parameters
    ----------
    file : pathlib.Path
        The file to check.
    encoding : str
        The encoding to check.

    Returns
    -------
    bool
        True if the file is encoded with the specified encoding, False otherwise.
    """
    try:
        file.open(encoding=encoding).close()
        return True
    except UnicodeDecodeError:
        return False

def getLineEnding(line:bytes) -> str:
    if(line.endswith(b"\r\n")):
        return "crlf"
    elif(line.endswith(b"\r")):
        return "cr"
    elif(line.endswith(b"\n")):
        return "lf"
    else:
        return ""

def checkLineEnding(file:pathlib.Path, lineEnding:str) -> bool:
    """
    Check if the file uses the specified line ending.

    Parameters
    ----------
    file : pathlib.Path
        The file to check.
    lineEnding : str
        The line ending to check, support cr, lf, crlf.

    Returns
    -------
    bool
        True if the file uses the specified line ending, False otherwise.
    """
    with file.open("rb") as f:
        for line in f:
            actualLineEnding = getLineEnding(line)
            if(actualLineEnding != "" and actualLineEnding != lineEnding):
                return False
    return True

def main():
    globPattern:str = github_action_utils.get_user_input("glob") or "**/*"
    lineEnding:str  = (github_action_utils.get_user_input("line-ending") or "").lower()
    encoding:str    = github_action_utils.get_user_input("encoding") or ""

    if(lineEnding.lower() not in ["", "cr", "lf", "crlf"]):
        print(f"unsupported line ending: {lineEnding}, only support cr, lf, crlf")
        return 1

    # Get the list of files that match the glob pattern
    files:List[pathlib.Path] = list(pathlib.Path(".").glob(globPattern))

    passed:bool = True
    # Check the encoding
    if(encoding!=""):
        wrongEncodingFiles = Enumerable(files)\
            .where(lambda file: not checkEncoding(file, encoding))\
            .to_list()
        if(len(wrongEncodingFiles)>0):
            print(f"The following files aren't encoded with {encoding}:")
            Enumerable(wrongEncodingFiles).for_each(lambda file: print(f"  {file}"))
            print("")
            passed = False

    # Check line ending
    if(lineEnding != ""):
        wrongLineEndingFiles = Enumerable(files)\
            .where(lambda file: not checkLineEnding(file, lineEnding))\
            .to_list()
        if(len(wrongLineEndingFiles)>0):
            print(f"The following files don't use {lineEnding} line ending:")
            Enumerable(wrongLineEndingFiles).for_each(lambda file: print(f"  {file}"))
            print("")
            passed = False
    
    return 0 if passed else 1

if __name__ == "__main__":
    main()