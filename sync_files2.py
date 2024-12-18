import os
import argparse
from tqdm import tqdm
import filecmp
import shutil

class Synchronizer:
    def __init__(self,
                 source_dir:str,
                 destination_dir:str
                 ):
        self.source_dir=source_dir
        self.destination_dir=destination_dir
        self.pathes_to_sync=[]
        self.added_files=[]
        self.added_folders=[]
        self.deleted_files=[]
        self.deleted_folders=[]
        self.shallow=True
    
    def validate_dirs(self) -> bool:
        """
            Validates source and destination directories pathes.
        """
        if not os.path.exists(self.source_dir):
            print(f"\nError: Source directory '{self.source_dir}' does not exist.")
            return False
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)
            print(f"\nDestination directory '{self.destination_dir}' created.")
        # Check if source and destination directories are not the same
        if self.source_dir==self.destination_dir:
            print('\nError: Source and Destination directories shall be different.' )
            return False
        return True

    def get_pathes_to_sync(self):
        # Store names of all files and directories from the source directory
        for root, dirs, files in os.walk(self.source_dir):
            for directory in dirs:
                self.pathes_to_sync.append(os.path.join(root, directory))
            for file in files:
                self.pathes_to_sync.append(os.path.join(root, file))

    def sync_directories(self, delete:bool=False) -> dict:
        """
            Synchronize files between two directories.
            Returns dictionary with amout of copied folders and files
        """
        self.get_pathes_to_sync()
        # Iterating through files in the source directory (with progress bar)
        with tqdm(total=len(self.pathes_to_sync), desc="Syncing files", unit="file") as pbar:
            for source_path in self.pathes_to_sync:
                replica_path = os.path.join(self.destination_dir, os.path.relpath(source_path, self.destination_dir))

                # Path is a directory and it does not exist in the destination
                if os.path.isdir(source_path):
                    if not os.path.exists(replica_path):
                        os.makedirs(replica_path)
                        self.added_folders.append(replica_path)

                # Copy files from the source directory to the replica directory
                else:
                    # Check if the file exists in the replica directory and if it is different from the source file
                    if not os.path.exists(replica_path) or not filecmp.cmp(source_path, replica_path, shallow=self.shallow):
                        # Set the description of the progress bar and print the file being copied
                        pbar.set_description(f"Processing '{source_path}'")
                        print(f"\nCopying {source_path} to {replica_path}")

                        # Copy the file from the source directory to the replica directory
                        shutil.copy2(source_path, replica_path)
                        self.added_files.append(replica_path)
                pbar.update(1)





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

    sync=Synchronizer(source_dir=args.source_directory, destination_dir=args.destination_directory)
    if not sync.validate_dirs():
        exit(1)
    

        

    # Synchronize the directories
    sync_dict=sync_directories(args.source_directory, args.destination_directory, args.delete)
    if args.log:
        log_sync(args.destination_directory, sync_dict)
    print(f"\nSynchronization complete")
    print(f"\tAdded Folders: {len(sync_dict['added_folders'])},\tFiles: {len(sync_dict['added_files'])}")
    if args.delete:
        print(f"\tDeleted Folders: {len(sync_dict['deleted_folders'])},\tFiles: {len(sync_dict['deleted_files'])}")
