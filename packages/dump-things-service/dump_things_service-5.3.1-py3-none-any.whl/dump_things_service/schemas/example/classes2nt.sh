#!/usr/bin/env bash

for i in $(ls -1 *.yaml)
do
  class=$(echo $i|cut -d - -f 1)
  linkml-convert -C $class -s ../grants.yaml -t ttl $i|python ../ttl2nt.py
done 2>/dev/null
