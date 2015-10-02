#!/bin/bash

rm -f ceph_disk.py  ceph_disk.pyc __init__.py
touch __init__.py
ln -s ${PWD}/../ceph-disk ceph_disk.py
sudo ./unittest.py $@
rm -f ceph_disk.py  ceph_disk.pyc __init__.py

