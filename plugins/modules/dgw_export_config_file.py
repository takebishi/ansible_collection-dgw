#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dgw_export_config_file
short_description: Export DeviceGateway Configuration File
description:
  - Export the configuration file from the Control Node and load it into the Managed Node.
version_added: 1.0.0
options:
  dgw_container_type:
    description:
      - Container type that DeviceGateway runs on.
    type: str
    choices:
      - docker
      - podman
    required: true
  dgw_container_name:
    description:
      - Container name that DeviceGateway runs on.
    type: str
    required: yes
  host_setting_fpath:
    description:
      - The configuration file path on the Managed Node to be set to DeviceGateway.
    type: str
    required: yes
author: "TAKEBISHI(@GitHubID)"
'''

EXAMPLES = r'''
- name: Make directory in Managed Node
  file:
    path: "/tmp/export"
    state: directory

- name: Copy config file to Managed Node
  copy:
    src: "~/mydir/export_dgw.dxg"
    dest: "/tmp/export/setting.dxg"

- name: Export Setting
  takebishi.dgw.dgw_export_config_file:
    dgw_container_type: "docker"
    dgw_container_name: "devicegateway"
    host_setting_fpath: "/tmp/export/setting.dxg"
'''

RETURN = r'''
msg:
  description: Detail set setting result message.
  returned: succsess
  type: str
errmsg:
  description: Detail error message.
  returned: failure
  type: str
'''


import sys
import os
import subprocess
import json
from time import sleep
from ansible_collections.takebishi.dgw.plugins.module_utils.dgw_define import DGW_PATH, DGW_SETTING_FPATH
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dgw_container_type=dict(required=True, type='str', choices=['docker', 'podman']),
            dgw_container_name=dict(required=True, type='str'),
            host_setting_fpath=dict(required=True, type='str'),
        ),
        supports_check_mode=False
    )
    dgw_container_type = module.params['dgw_container_type']
    container_name = module.params['dgw_container_name']
    host_setting_fpath = module.params['host_setting_fpath']

    # Check directory in host
    hostdirpath = os.path.dirname(host_setting_fpath)
    if not os.path.isfile(host_setting_fpath) or not os.path.exists(hostdirpath):
        module.fail_json(msg="", errmsg=f"Input setting file is not found. : {host_setting_fpath}")

    curr_setting_file = hostdirpath + "/currentsetting"
    dgw_changed = False
    dgw_msg = ''

    curr_setting_file_exists = False
    try:
        # Delete container config file
        cp = subprocess.run(f"{dgw_container_type} exec {container_name} rm {DGW_SETTING_FPATH}",
                            check=False, shell=True, capture_output=True, text=True)

        # 現在の設定を取得
        # Create get_setting file
        cp = subprocess.run(f"{dgw_container_type} exec {container_name} touch {DGW_PATH}/get_setting", check=False, shell=True, capture_output=True, text=True)
        if cp.returncode != 0:
            module.fail_json(msg="", errmsg=f"Create get_setting file ERROR: {cp.stderr}")

        # DGWからのファイル出力を待つ
        wait_sec = 0
        while wait_sec <= 10:
            sleep(1)
            wait_sec = wait_sec + 1
            # Check config is exist
            cp = subprocess.run(f"{dgw_container_type} exec {container_name} ls {DGW_SETTING_FPATH}",
                                check=False, shell=True, capture_output=True, text=True)
            if cp.returncode == 0:
                curr_setting_file_exists = True
                break

        if curr_setting_file_exists is False:
            # 設定ファイルが取得できなければ強制的に設定を反映する
            dgw_changed = True

    except subprocess.SubprocessError as e:
        module.fail_json(msg="", errmsg=f"{e.stderr}")
    except Exception as e:
        t, o, tb = sys.exc_info()
        module.fail_json(msg="", errmsg=f"{t}:{str(e)}")

    if curr_setting_file_exists is True:
        try:
            # Copy config file from container
            cp = subprocess.run(f"{dgw_container_type} cp {container_name}:{DGW_SETTING_FPATH} {curr_setting_file}",
                                check=False, shell=True, capture_output=True, text=True)
            if cp.returncode != 0:
                module.fail_json(msg="", errmsg=f"Copy config file from container ERROR: {cp.stderr}")

            # 設定を比較
            dgw_changed = is_different_setting(curr_setting_file, host_setting_fpath)

            # Delete temporary file
            os.remove(curr_setting_file)

            # Delete container config file
            cp = subprocess.run(f"{dgw_container_type} exec {container_name} rm {DGW_SETTING_FPATH}",
                                check=False, shell=True, capture_output=True, text=True)
            if cp.returncode != 0:
                module.fail_json(msg="", errmsg=f"Delete container config file ERROR: {cp.stderr}")

        except subprocess.SubprocessError as e:
            module.fail_json(msg="", errmsg=f"{e.stderr}")
        except DgwCompareError as e:
            t, o, tb = sys.exc_info()
            module.fail_json(msg="", errmsg=f"{t}:{str(e)}")
        except Exception as e:
            t, o, tb = sys.exc_info()
            module.fail_json(msg="", errmsg=f"{t}:{str(e)}")

    if dgw_changed is True:
        # 差分があれば設定反映
        try:
            # 古いファイルがあれば削除
            cp = subprocess.run(f"{dgw_container_type} exec {container_name} ls {DGW_PATH}/result.log", check=False, shell=True, capture_output=True, text=True)
            if cp.returncode == 0:
                cp = subprocess.run(f"{dgw_container_type} exec {container_name} rm {DGW_PATH}/result.log",
                                    check=False, shell=True, capture_output=True, text=True)
                if cp.returncode != 0:
                    module.fail_json(msg="", errmsg=f"Delete old result.log file ERROR: {cp.stderr}")

            # Copy config file to container
            cp = subprocess.run(f"{dgw_container_type} cp {host_setting_fpath} {container_name}:{DGW_SETTING_FPATH}",
                                check=False, shell=True, capture_output=True, text=True)
            if cp.returncode != 0:
                module.fail_json(msg="", errmsg=f"Copy config file to container ERROR: {cp.stderr}")

            # Create set_setting file
            cp = subprocess.run(f"{dgw_container_type} exec {container_name} touch {DGW_PATH}/set_setting",
                                check=False, shell=True, capture_output=True, text=True)
            if cp.returncode != 0:
                module.fail_json(msg="", errmsg=f"Create set_setting file ERROR: {cp.stderr}")

            # Check DGW result
            res_file_path = hostdirpath + "/result.log"
            if os.path.exists(res_file_path) is True:
                os.remove(res_file_path)

            # DGWからのresultを待つ
            wait_sec = 0
            while wait_sec <= 10:
                sleep(1)
                wait_sec = wait_sec + 1
                cp = subprocess.run(f"{dgw_container_type} cp {container_name}:{DGW_PATH}/result.log {res_file_path}",
                                    check=False, shell=True, capture_output=True, text=True)
                if cp.returncode == 0:
                    break

            if os.path.exists(res_file_path) is False:
                module.fail_json(msg="", errmsg="Cannot get DeviceGateway set setting result.")
            else:
                with open(res_file_path) as f:
                    s = f.read()
                if len(s) == 0:
                    module.fail_json(msg="", errmsg="Cannot get DeviceGateway set setting result.")
                elif "Completed importing." not in s:
                    module.fail_json(msg="", errmsg=f"DeviceGateway set setting result: {s}")
                dgw_msg = "DeviceGateway set setting result: " + s

        except subprocess.SubprocessError as e:
            module.fail_json(msg="", errmsg=f"{e.stderr}")
        except Exception as e:
            t, o, tb = sys.exc_info()
            module.fail_json(msg="", errmsg=f"{t}:{str(e)}")
    else:
        dgw_msg = "No Changes."

    module.exit_json(changed=dgw_changed, msg=dgw_msg)


def json_ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, json_ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(json_ordered(x) for x in obj)
    else:
        return obj


def is_different_setting(old, new):
    try:
        file = open(old, 'r', encoding="utf-8")
        old_obj = json.load(file)
        file.close()
        file = open(new, 'r', encoding="utf-8")
        new_obj = json.load(file)
        file.close()

        if json_ordered(old_obj) == json_ordered(new_obj):
            return False
        else:
            return True
    except Exception as e:
        t, o, tb = sys.exc_info()
        raise DgwCompareError(f"Cannot compare configure files.: {t}:{str(e)}")


class DgwCompareError(Exception):
    pass


if __name__ == '__main__':
    main()
