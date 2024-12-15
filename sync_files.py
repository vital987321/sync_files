import os
import shutil
import filecmp
import argparse
from tqdm import tqdm
from time import gmtime, strftime


def check_directories(src_dir:str, dst_dir:str) -> bool:
    """
        Validates source and destination directories pathes.
        Rerturns true of false.
    """
    if not os.path.exists(src_dir):
        print(f"\nError: Source directory '{src_dir}' does not exist.")
        return False
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(f"\nDestination directory '{dst_dir}' created.")
    # Check if source and destination directories are not the same
    if src_dir==dst_dir:
        print('\nError: Source and Destination directories shall be different.' )
        return False
    return True



def sync_directories(src_dir:str, dst_dir:str, delete:bool=False) -> dict:
    """
        Synchronize files between two directories.
        Returns dictionary with amout of copied folders and files
    """
    # Store names of all files and directories from the source directory
    files_to_sync:list = []
    added_files:list=[]
    added_folders:list=[]
    deleted_files:list=[]
    deleted_folders:list=[]
    for root, dirs, files in os.walk(src_dir):
        for directory in dirs:
            files_to_sync.append(os.path.join(root, directory))
        for file in files:
            files_to_sync.append(os.path.join(root, file))

    # Iterating through files in the source directory (with progress bar)
    with tqdm(total=len(files_to_sync), desc="Syncing files", unit="file") as pbar:
        for source_path in files_to_sync:
            replica_path = os.path.join(dst_dir, os.path.relpath(source_path, src_dir))

            # Path is a directory and it does not exist in the destination
            if os.path.isdir(source_path):
                if not os.path.exists(replica_path):
                    os.makedirs(replica_path)
                    added_folders.append(replica_path)
                    
            # Copy files from the source directory to the replica directory
            else:
                # Check if the file exists in the replica directory and if it is different from the source file
                if not os.path.exists(replica_path) or not filecmp.cmp(source_path, replica_path, shallow=True):
                    # Set the description of the progress bar and print the file being copied
                    pbar.set_description(f"Processing '{source_path}'")
                    print(f"\nCopying {source_path} to {replica_path}")

                    # Copy the file from the source directory to the replica directory
                    shutil.copy2(source_path, replica_path)
                    added_files.append(replica_path)
                    

            pbar.update(1)
    
    # Clean up files in the destination directory that are not in the source directory, if delete flag is set
    if delete:
        # Get a list of all files in the destination directory
        files_to_delete = []
        for root, dirs, files in os.walk(dst_dir):
            for directory in dirs:
                files_to_delete.append(os.path.join(root, directory))
            for file in files:
                files_to_delete.append(os.path.join(root, file))

        # Iterate over each file in the destination directory with a progress bar
        with tqdm(total=len(files_to_delete), desc="Deleting files", unit="file") as pbar:
            # Iterate over each file in the destination directory
            for replica_path in files_to_delete:
                # Check if the file exists in the source directory
                source_path = os.path.join(src_dir, os.path.relpath(replica_path, dst_dir))
                if not os.path.exists(source_path):
                    # Set the description of the progress bar
                    pbar.set_description(f"Processing '{replica_path}'")
                    print(f"\nDeleting {replica_path}")

                    # Check if the path is a directory and remove it
                    if os.path.isdir(replica_path):
                        shutil.rmtree(replica_path)
                        deleted_folders.append(replica_path)
                    else:
                        # Remove the file from the destination directory
                        os.remove(replica_path)
                        deleted_files.append(replica_path)

                # Update the progress bar
                pbar.update(1)
    return {'added_files':added_files,
            'added_folders':added_folders,
            'deleted_files':deleted_files,
            'deleted_folders':deleted_folders,
            }


def log_sync(dst_dir:str, sync_dict:dict)->None:
    """
        Creates Log file in the destination directory
    """
    with open(os.path.join(dst_dir, 'log.txt'), "w") as logfile:
        current_time=strftime("%Y-%m-%d %H:%M:%S", gmtime())
        logfile.write(f'Syncronization log  {current_time} \n')
        logfile.write(f"Added Folders: {len(sync_dict['added_folders'])},  Files: {len(sync_dict['added_files'])}\n")
        if(len(sync_dict['deleted_folders'])>0 or len(sync_dict['deleted_files'])>0):
            logfile.write(f"Deleted Folders: {len(sync_dict['deleted_folders'])},  Files: {len(sync_dict['deleted_files'])}\n")
        if len(sync_dict['added_folders'])>0:
            logfile.write('\n    ------Added Folders------    \n')
            for folder in sync_dict['added_folders']:
                logfile.write(f'{folder}\n')
        if len(sync_dict['added_files'])>0:
            logfile.write('\n    ------Added Files------    \n')    
            for file in sync_dict['added_files']:
                logfile.write(f'{file}\n')
        if len(sync_dict['deleted_folders'])>0:
            logfile.write('\n    ------Deleted Folders------    \n')
            for folder in sync_dict['deleted_folders']:
                logfile.write(f'{folder}\n')
        if len(sync_dict['deleted_files'])>0:
            logfile.write('\n    ------Deleted Files------    \n')
            for folder in sync_dict['deleted_files']:
                logfile.write(f'{folder}\n')



if __name__ == "__main__":
    """
        Main function to parse command line arguments and synchronize directories
    """
 
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Synchronize files between two directories.")
    parser.add_argument("source_directory", help="The source directory to synchronize from.")
    parser.add_argument("destination_directory", help="The destination directory to synchronize to.")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="Delete files and folders in destination that are not in source.")
    parser.add_argument("-l", "--log",  action="store_true",
                        help="Log results in the destination folder.")
    args = parser.parse_args()

    # If the delete flag is set, print a warning message
    if args.delete:
        print("\nExtraneous files in the destination will be deleted.")

    # Check the source and destination directories
    if not check_directories(args.source_directory, args.destination_directory):
        exit(1)

    # Synchronize the directories
    sync_dict=sync_directories(args.source_directory, args.destination_directory, args.delete)
    if args.log:
        log_sync(args.destination_directory, sync_dict)
    print(f"\nSynchronization complete")
    print(f"\tAdded Folders: {len(sync_dict['added_folders'])},\tFiles: {len(sync_dict['added_files'])}")
    if args.delete:
        print(f"\tDeleted Folders: {len(sync_dict['deleted_folders'])},\tFiles: {len(sync_dict['deleted_files'])}")

