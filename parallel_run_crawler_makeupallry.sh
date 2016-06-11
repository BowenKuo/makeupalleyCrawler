#!/bin/bash

if [ $# -ne 3 ]
then
	echo '[usage]' $0 'start_id end_id fold_num'
else
	start_id=$1
	end_id=$2
	fold=$3
	total_gap=`expr $1 - $2`
	interator_gap=`expr $total_gap / $fold`
	interator_gap=`expr $interator_gap / 30 `
	interator_gap=`expr $interator_gap + 1`
	interator_gap=`expr $interator_gap \* 30`
	top_id=$start_id

	for (( c=1 ; c<=$fold ; c++ ))
	do
		low_id=`expr $start_id - $c \* $interator_gap`
		nohup python crawl_makeupalley_normal.py $top_id $low_id  &> log_/startFrom+$top_id+to+$low_id.txt &
		top_id=`expr $start_id - $c \* $interator_gap - 1`
	done

    while [[ $(ps -L | tr -s " " | cut -d '' -f 5 | uniq | grep python) = *python* ]]; do
        sleep 2m
    done
    python email_notify.py $start_id $end_id

fi
