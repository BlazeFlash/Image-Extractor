

#creating zip files and placing files in them and then deleting the previous folders
import os
import shutil
from pathlib import Path
import zipfile
disk_dir=Path("C:/imgs/")
zipped=zipfile.ZipFile('d:/newzip.zip','w')
for root, dirs, files in os.walk(disk_dir):
    for file in files:
        zipped.write(os.path.join(root, file))
shutil.rmtree(disk_dir)
zipped.close()    
