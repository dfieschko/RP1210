import os
import shutil

# copy ini files into windows dir on github. This is done so unit tests that need the files may pass

dest_path = os.environ["WINDIR"]

def run():
    inti_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    ini_files = os.listdir(inti_files_dir)

    for ini_file_name in ini_files:

        shutil.copyfile(os.path.join(inti_files_dir, ini_file_name), # copy ini file from ./files dir 
                        os.path.join(dest_path, ini_file_name)) # to windows dir

if __name__ == '__main__':
    run()