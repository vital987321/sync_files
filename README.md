This tool allows you synchronize files between two folders.

INSTALLATION
Download sync_files.py and run.cmd

RUNNING THE SCRIPT
Run run.cmd or use command line with required parameters, for example:
python sync_files.py D:\Temp\sync_test\s D:\Temp\sync_test\d -d -l
or python sync_files.py D:\Temp\sync_test\s D:\Temp\sync_test\d
or python sync_files.py -h

PARAMETERS
 -h - help.
source_directory - The source directory to synchronize from.
destination_directory - The destination directory to synchronize to.
-d – [Optional] Delete files and folders in destination that are not in source. 
-l – [Optional]  Log results in the destination folder (file log.txt).

