import glob, os
path = raw_input("Enter a data path: ")
print glob.glob(os.path.join(path, "*.*"))
raw_input("Press Enter to exit")
