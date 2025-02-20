#!/bin/sh

trap '' 1
trap 'rm -f /tmp/running' 2 3 9 15

touch /tmp/running

ctrl_path=/tmp/dgw_request
mkdir -p ${ctrl_path}
chmod 777 ${ctrl_path}
cp ./setting.dxg /tmp > /dev/null 2>&1

while true
do
	if [[ ! -f /tmp/running ]]; then
		break
	fi
	
	if [[ -d ${ctrl_path} ]]; then
		if [[ -f ${ctrl_path}/get_setting ]]; then
			if [[ ! -f ${ctrl_path}/no_get_setting ]]; then
				cp /tmp/setting.dxg ${ctrl_path} > /dev/null 2>&1
				chmod 666 ${ctrl_path}/setting.dxg
			fi
			rm -f ${ctrl_path}/get_setting
		fi
		
		if [[ -f ${ctrl_path}/set_setting && -f ${ctrl_path}/setting.dxg ]]; then
			if [[ ! -f ${ctrl_path}/no_set_setting ]]; then
				sleep 1
				cp /tmp/setting.dxg ${ctrl_path}/_setting.dxg > /dev/null 2>&1
				if [[ -f ${ctrl_path}/test_empty ]]; then
					touch ${ctrl_path}/result.log > /dev/null 2>&1
				elif [[ -f ${ctrl_path}/test_error ]]; then
					cp ./result_error.log ${ctrl_path}/result.log > /dev/null 2>&1
				else
					cp ${ctrl_path}/setting.dxg /tmp > /dev/null 2>&1
					cp ./result_ok.log ${ctrl_path}/result.log > /dev/null 2>&1
				fi
			fi
			rm -f ${ctrl_path}/set_setting
		fi
		
		if [[ -f ${ctrl_path}/restart ]]; then
			sleep 1
			rm -f ${ctrl_path}/restart
		fi
	fi
	
	sleep 1
done

