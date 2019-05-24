import os
import hashlib

base = os.path.join('out', 'aggregated-file')
data_dir = 'data'
for publisher in os.listdir(data_dir):
    if publisher.startswith('.') or not os.path.isdir(os.path.join(data_dir, publisher)):
        continue
    for dataset in os.listdir(os.path.join(data_dir, publisher)):
        md5hash = hashlib.md5(open(os.path.join(data_dir, publisher, dataset)).read()).hexdigest()
        hashdir = os.path.join(md5hash[0], md5hash[1], md5hash[2], md5hash[3], md5hash)
        if os.path.exists(os.path.join('gitout','hash',hashdir)):
            try:
                os.makedirs(os.path.join(base, publisher))
            except OSError:
                pass
            os.symlink(os.path.join(os.getcwd(),'gitout','hash',hashdir), os.path.join(base, publisher, dataset))

