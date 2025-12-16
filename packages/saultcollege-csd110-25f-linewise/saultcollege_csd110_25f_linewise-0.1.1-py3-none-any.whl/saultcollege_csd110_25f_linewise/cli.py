import sys # Import sys to accept args from CLI
import os # import 'os' to check the existence of files, directories, and manipulate path

def help_message(): # Function to return a help message to user instructing how to use the progrm
    """
        Returns the usage help text for the `linewise` command-line tool

        Provides detailed description of how to use the program

        Returns (str): a string of documented text explaining how to use the program in a proper way
    """
    return """Usage: linewise <file> [options]

    <file> is a path to a text file

    Options:
        -h, --help:     Display this help message (all other options are ignored if this is present)
        Only one of the following may be set:
        --lines: Total number of lines
        --words: Total number of words
        --chars: Total number of characters

    Examples:

        $ linewise fileName.txt --lines
        The total number of lines of this file is: 2

        $ linewise fileName.txt --words
        The total number of lines of this file is: 45

        $ linewise fileName.txt --chars
        The total number of lines of this file is: 132

        $ linewise fileName.txt
        lines: 2
        words: 45
        chars: 132
    """
def parse_args(args): # Function to interpret and validate args
    """
    Parse and validate command-line arguments
    
    parameters: 
        args (list of str): given arguments by the terminal
            args MUST be a list of strings

    Return: 
        - path of the given files
        - mode of search
            mode is one of: "all", "lines", "words", "chars"
    """
    if len(args) == 0 or ("-h" in args) or ("--help" in args): # if don't have args or if user ask for help
        print(help_message())
        
        # Exiting with a non-zero status
        sys.exit(1)  
    
    files = []  # list of files
    
    # Obs: A set is like a list, but it can only contain unique values
    flags = set() # unordered collections of unique elements. Obs: Useful for validation purposes
    valid_flags = ["lines", "words", "chars"]

    for arg in args: # loop for go througth every argument
        if arg.startswith("-"): 
            # remove leading dashes from flag, e.g. --lines > lines
            flag = arg.strip("-")
            if flag not in valid_flags: # if not in valid_flag (list)
                print(f"Error: Flag must be one of '{valid_flags}'")
                sys.exit(1) # Exit
            # add to the set a single element that is not duplicate
            flags.add(flag)
        else:
            files.append(arg) # add to the end of the list (useful for dealing with multiple files)

    # VIRIFY FILES
    if len(files) == 0: # If no file path found 
        print("Error: You must provide a path to a text file.")
        print(help_message())
        sys.exit(1)

    if len(files) > 1: # if more then one file
        print("Error: This version accepts only one file at a time")
        sys.exit(1)

    # VERIFY FLAGS
    if len(flags) > 1: # if more then one flag
        print("Error: Only one flag may be set at a time")
        sys.exit(1)
    
    # The default search_type is "all" if none is specified
    mode = flags.pop() if len(flags) == 1 else "all"

    # Define path. Obs: search for file list
    path = files[0]

    # FILE VALIDATION (Not sure if needed)
    # if not os.path.exists(path): #Verify if its a valid path
    #     print("Error: File does not exist")
    #     sys.exit(1)
    
    # if not os.path.isfile(path): # Verify if its a valid file
    #     print("Path is not a regular file")
    #     sys.exit(1)

    return (path, mode)

def linewise(file_path, flag): # function that validates the path and read content in a safe way
    """
        Read a text file, validate given path and compute eather lines, words or characters.

        Parameters:
            file_path (str): Path to the text file
                file_path must be a string that refers to a file

            flag (str): flag to verify mode
                - "lines": total number of lines
                - "words": total number of words
                - "chars": total number of characters
                - "all": computing and returning all three metrics
                flag must be a string 

        Returns (dict / int):
            - if int: returns count of the selected mode
            - if dict: returns a dictionary containing all modes
    """
    # Verify if its valid a file/path or not
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError: # If file not found
        print("Error: File not found.")
        sys.exit(1)
    except IsADirectoryError: # If its not a file
        print("Error: You provided a directory instead of a file")
        sys.exit(1)
    except PermissionError: # If its a protected file
        print("Error: Permission denied when trying to read")
        sys.exit(1)
    except UnicodeDecodeError: # If its not valid content inside
        print("Error: This file cound not be read as UTF-8 text")
        sys.exit(1)
    except Exception as error: # If some other error occurred
        print("Error: Something went wrong")
        print("Details: ", error) # Sends the error message received to error
        sys.exit(1)

    # Check for given mode
    if flag == "lines":
        return count_lines(text)
    elif flag == "words":
        return count_words(text)
    elif flag == "chars":
        return count_char(text)
    else:
        lines = count_lines(text) 
        words = count_words(text)
        chars = count_char(text)

        # returns a dicionary
        return {"lines": lines, "words": words, "chars": chars}

def main():
    # Assign all arguments but first from the terminal
    args = sys.argv[1:] 

    # Assign respectively returned falues from parse_args()
    file_path, mode = parse_args(args)

     # Assign returned (int / dict) to result
    result = linewise(file_path, mode)

    if isinstance(result, dict): # Condition to verify if result its a dict
        # display to user a format search from result
        print(f"lines: {result['lines']}")
        print(f"words: {result['words']}")
        print(f"chars: {result['chars']}") 
    else: # if not dict
        # result is given as an integer 
        if mode == "lines": 
            print("The total number of lines is: " + str(result)) 
        elif mode == "words":
            print("The total number of words is: " + str(result))
        elif mode == "chars":
            print("The total number of characters is: " + str(result))

def count_lines(text):
    """
        Compute the amount of lines in the given string

        Parameters:
            text (str): String of text from an open file
            text must be a string

        splitlines():
            split lines from a given string

        len():
            compute the lenght of a given object

        Returns (int):
            count of lines present in this string

        Obs: Pure Function
    """
    return len(text.splitlines()) # split lines and count total
def count_words(text):
    """
    Compute the amount of words in the given string

        Parameters:
            text (str): String of text from an open file
            text must be a string

        splt():
            split words from a given string

        len():
            compute the lenght of a given object

        Returns (int):
            count of words present in this string

        Obs: Pure Function
    """
    return len(text.split()) # split words and count total
            
def count_char(text):
    """
    Compute the amount of characters in the given string

        Parameters:
            text (str): String of text from an open file
            text must be a string

        len():
            compute the lenght of a given object

        Returns (int):
            count of characters present in this string

        Obs: Pure Function
    """
    return len(text) # count total of characters (including spaces)