import os
import argparse
from tqdm import tqdm
import filecmp
import shutil
from time import gmtime, strftime

class Synchronizer:
    def __init__(self,
                 source_dir:str,
                 destination_dir:str,
                 delete:bool,
                 log:bool
                 ):
        self.source_dir=source_dir
        self.destination_dir=destination_dir
        self.source_pathes=[]
        self.destination_pathes=[]
        self.added_files=[]
        self.added_folders=[]
        self.deleted_files=[]
        self.deleted_folders=[]
        self.shallow=True
        self.deletion=delete
        self.loging_results=log
    
    def validate_dirs(self) -> bool:
        """ Validates source and destination directories pathes. """
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

    def get_source_pathes(self):
        """ Stores names of all files and directories from the source directory"""
        for root, dirs, files in os.walk(self.source_dir):
            for directory in dirs:
                self.source_pathes.append(os.path.join(root, directory))
            for file in files:
                self.source_pathes.append(os.path.join(root, file))
    
    def get_destination_pathes(self):
        """ Stores names of all files and directories from the destination directory """
        for root, dirs, files in os.walk(self.destination_dir):
            for directory in dirs:
                self.destination_pathes.append(os.path.join(root, directory))
            for file in files:
                self.destination_pathes.append(os.path.join(root, file))

    def sync_directories(self) -> dict:
        """
            Synchronizes files and folders in destination directory to match source directory.
            Does not delete files and folders in the destination directory, if they are missing in the sourse directory.
        """
        self.get_source_pathes()
        # Iterating through files in the source directory (with progress bar)
        with tqdm(total=len(self.source_pathes), desc="Syncing files", unit="file") as pbar:
            for source_path in self.source_pathes:
                replica_path = os.path.join(self.destination_dir, os.path.relpath(source_path, self.source_dir))

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

    def delete_missing_files(self):
        """
            Deletes files and folders in the destination directory, if they are missing in the sourse directory.
        """
        if not self.deletion:
            return None
        self.get_destination_pathes()
        with tqdm(total=len(self.destination_pathes), desc="Deleting files", unit="file") as pbar:
            # Iterate over each file in the destination directory
            for replica_path in self.destination_pathes:
                # Check if the file exists in the source directory
                source_path = os.path.join(self.source_dir, os.path.relpath(replica_path, self.destination_dir))
                if not os.path.exists(source_path):
                    # Set the description of the progress bar
                    pbar.set_description(f"Processing '{replica_path}'")
                    print(f"\nDeleting {replica_path}")

                    # Check if the path is a directory and remove it
                    if os.path.isdir(replica_path):
                        shutil.rmtree(replica_path)
                        self.deleted_folders.append(replica_path)
                    else:
                        # Remove the file from the destination directory
                        os.remove(replica_path)
                        self.deleted_files.append(replica_path)

                # Update the progress bar
                pbar.update(1)

    def log_results(self):
        """
        Creates Log file in the destination directory
        """
        with open(os.path.join(self.destination_dir, 'log.txt'), "w") as logfile:
            log_time=strftime("%Y-%m-%d %H:%M:%S", gmtime())
            logfile.write(f'Syncronization log  {log_time} \n')
            logfile.write(f"Added Folders: {len(self.added_folders)},  Files: {len(self.added_files)}\n")
            if(len(self.deleted_folders)>0 or len(self.deleted_files)>0):
                logfile.write(f"Deleted Folders: {len(self.deleted_folders)},  Files: {len(self.deleted_files)}\n")
            if len(self.added_folders)>0:
                logfile.write('\n    ------Added Folders------    \n')
                for folder in self.added_folders:
                    logfile.write(f'{folder}\n')
            if len(self.added_files)>0:
                logfile.write('\n    ------Added Files------    \n')    
                for file in self.added_files:
                    logfile.write(f'{file}\n')
            if len(self.deleted_folders)>0:
                logfile.write('\n    ------Deleted Folders------    \n')
                for folder in self.deleted_folders:
                    logfile.write(f'{folder}\n')
            if len(self.deleted_files)>0:
                logfile.write('\n    ------Deleted Files------    \n')
                for folder in self.deleted_files:
                    logfile.write(f'{folder}\n')
    
    def print_summary(self):
        """ Prints small summary notes to console."""
        print(f"\nSynchronization complete")
        print(f"\tAdded Folders: {len(self.added_folders)},\tFiles: {len(self.added_files)}")
        if self.deletion:
            print(f"\tDeleted Folders: {len(self.deleted_folders)},\tFiles: {len(self.deleted_files)}")

    def run_task(self):
        """ Tracks the main logic of the process"""
        if not self.validate_dirs():
            return None
        self.sync_directories()
        if self.deletion:
            self.delete_missing_files()
        if self.loging_results:
            self.log_results()
        self.print_summary()


def parse_arguments():
    """ Parses command line arguments """
    parser = argparse.ArgumentParser(description="Synchronize files between two directories.")
    parser.add_argument("source_directory", help="The source directory to synchronize from.")
    parser.add_argument("destination_directory", help="The destination directory to synchronize to.")
    parser.add_argument("-d", "--delete", action="store_true",
                        help="Delete files and folders in destination that are not in source.")
    parser.add_argument("-l", "--log",  action="store_true",
                        help="Log results in the destination folder.")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    """
        Main function to start synchronizing directories
    """
    args=parse_arguments()
    sync=Synchronizer(source_dir=args.source_directory, destination_dir=args.destination_directory, delete=args.delete, log=args.log)
    sync.run_task()
    
