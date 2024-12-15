import os
import shutil
import filecmp
import argparse
from tqdm import tqdm


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
    files_added:int=0
    folders_added:int=0
    for root, dirs, files in os.walk(src_dir):
        for directory in dirs:
            files_to_sync.append(os.path.join(root, directory))
        for file in files:
            files_to_sync.append(os.path.join(root, file))

    # Iterating through files in the source directory (with progress bar)
    with tqdm(total=len(files_to_sync), desc="Syncing files", unit="file") as pbar:
        for source_path in files_to_sync:
            replica_path = os.path.join(dst_dir, os.path.relpath(source_path, src_dir))

            # Check if path is a directory and create it in the replica directory if it does not exist
            if os.path.isdir(source_path):
                if not os.path.exists(replica_path):
                    os.makedirs(replica_path)
                    folders_added+=1
            # Copy all files from the source directory to the replica directory
            else:
                # Check if the file exists in the replica directory and if it is different from the source file
                if not os.path.exists(replica_path) or not filecmp.cmp(source_path, replica_path, shallow=True):
                    # Set the description of the progress bar and print the file being copied
                    pbar.set_description(f"Processing '{source_path}'")
                    print(f"\nCopying {source_path} to {replica_path}")

                    # Copy the file from the source directory to the replica directory
                    shutil.copy2(source_path, replica_path)
                    files_added+=1

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
                    else:
                        # Remove the file from the destination directory
                        os.remove(replica_path)

                # Update the progress bar
                pbar.update(1)
    return {'files_added':files_added, 'folders_added':folders_added}


if __name__ == "__main__":
    """
        Main function to parse command line arguments and synchronize directories
    """
 
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Synchronize files between two directories.")
    parser.add_argument("source_directory", help="The source directory to synchronize from.")
    parser.add_argument("destination_directory", help="The destination directory to synchronize to.")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="Delete files in destination that are not in source.")
    args = parser.parse_args()

    # If the delete flag is set, print a warning message
    if args.delete:
        print("\nExtraneous files in the destination will be deleted.")

    # Check the source and destination directories
    if not check_directories(args.source_directory, args.destination_directory):
        exit(1)

    # Synchronize the directories
    sync=sync_directories(args.source_directory, args.destination_directory, args.delete)
    print(f"\nSynchronization complete. Added Folders: {sync['folders_added']},  Files: {sync['files_added']}")

