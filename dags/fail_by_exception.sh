count=0
d="[0-9]"
while read line
do
	if [[ $line =~ ^$d{4}-$d{2}-$d{2}" "$d{2}":"$d{2}":"$d{2}(.)+" Error "(.)+$ ]] 
	then 
		count=$(($count + 1))
	else
		if [[ $line =~ .*Exception.* ]] 
		then 
			count=$(($count + 1))
		fi
		if [[ $line =~ ^"error: "(.)+$ ]] 
		then 
			count=$(($count + 1))
		fi
	fi
	
	echo "$line"
done

if [ $count -ne 0 ]
then
	echo "Failed by Exception"
	exit 1
else
	exit 0
fi
