#!/bin/bash
#trunk branches test tags

pre=svn://139.199.167.29/codes/
name=$1
arr[0]=$pre/$name/ad
arr[1]=$pre/$name/cms
arr[2]=$pre/$name/server
arr[2]=$pre/$name/server/{}
echo $pre/trunk_$name

