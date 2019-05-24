import os
import hashlib
import shutil

base = os.path.join('out', 'aggregated-file')
data_dir = 'data'
gitout_dir = os.path.join(os.getcwd(),'gitout')
for publisher in os.listdir(base):
    for dataset in os.listdir(os.path.join(base, publisher)):
        md5hash = hashlib.md5(open(os.path.join(data_dir, publisher, dataset)).read()).hexdigest()
        hashdir = os.path.join(md5hash[0], md5hash[1], md5hash[2], md5hash[3], md5hash)
        if not os.path.exists(os.path.join('gitout','hash',hashdir)):
            shutil.move(os.path.join(base, publisher, dataset), os.path.join(gitout_dir,'hash',hashdir))
            os.symlink(os.path.join(gitout_dir,'hash',hashdir), os.path.join(base, publisher, dataset))

