import sys
import os


def usage():
    """ Show usage message for this script. and exit.
    
    This function is called when the user provides invalid
    command line arguments.

    Or when the user requests help.

    """
    print ("Usage: dirstats <directory_path>")
    print ("Example: dirsats .")
    sys.exit(1)


def format_size(bytes_value):

    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 ** 2:
        return f"{bytes_value // 1024:.2f} KB"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value // (1024 ** 2)} MB"
    else:
        return f"{bytes_value // (1024 ** 3)} GB"
    


def analyze_directory(path):
    """ 
    Analyze the contents of a directory. This function
    returns a list of strings, one for each item in the directory.
    
    """
    
    result = []


    try:
    #Lists all items in the directory
        items = os.listdir(path)
    except Exception as e:
        print(f"Error: Cannot open directory '{path}' - {e}")
        return result
    

    #Iterate through directory contents
    for name in items:
        
        full_path = os.path.join(path, name)

        if os.path.isdir(full_path):
            result.append (f"{name} - directory")
       
        #check if the item is a file
        elif os.path.isfile(full_path):
            
                try:
                    total_size = os.path.getsize(full_path)
                    readable = format_size(total_size)
                    result.append(f"{name} - {readable} file")
                except Exception: 
                    result.append(f"{name} - file (size unavailable)")
    return result
    
def main():
    if len(sys.argv) <2:
        usage()

    if sys.argv[1] in ("--help", "h"):
        usage()

    path = sys.argv[1]

    print (f"dirstats {path}")
    
    entries = analyze_directory(path)

    for line in entries: 
        print(line)

     

if __name__ == "__main__":
    main()


