#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dgw_import_config_file
short_description: Import DeviceGateway Configuration File
description:
  - Import the specified configuration file from the Managed Node as a development environment.
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
      - The output path on the Managed Node of the configuration file retrieved from the DeviceGateway.
    type: str
    required: yes
author: "TAKEBISHI(@GitHubID)"
'''

EXAMPLES = r'''
- name: Import Setting
  takebishi.dgw.dgw_import_config_file:
    dgw_container_type: "podman"
    dgw_container_name: "devicegateway"
    host_setting_fpath: "/tmp/import_test/setting.dxg"
  register: result

- name: Fetch config file
  fetch:
    src: "/tmp/import_test/setting.dxg"
    dest: "~/mydir/export_dgw.dxg"
    flat: true
'''

RETURN = r'''
errmsg:
  description: Detail error message.
  returned: failure
  type: str
'''


import sys
import os
import subprocess
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
    dgw_container_type = str(module.params['dgw_container_type'])
    container_name = module.params['dgw_container_name']
    host_setting_fpath = module.params['host_setting_fpath']

    try:
        # Create get_setting file
        cp = subprocess.run(f"{dgw_container_type} exec {container_name} touch {DGW_PATH}/get_setting", check=False, shell=True, capture_output=True, text=True)
        if cp.returncode != 0:
            module.fail_json(msg="", errmsg=f"Create get_setting file ERROR: {cp.stderr}")

        # Pause 2 seconds
        sleep(2)

        # Check directory in host
        dirpath = os.path.dirname(host_setting_fpath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # Copy config file from container
        cp = subprocess.run(f"{dgw_container_type} cp {container_name}:{DGW_SETTING_FPATH} {host_setting_fpath}",
                            check=False, shell=True, capture_output=True, text=True)
        if cp.returncode != 0:
            module.fail_json(msg="", errmsg=f"Copy config file from container ERROR: {cp.stderr}")

        # Delete container config file
        cp = subprocess.run(f"{dgw_container_type} exec {container_name} rm {DGW_SETTING_FPATH}", check=False, shell=True, capture_output=True, text=True)
        if cp.returncode != 0:
            module.fail_json(msg="", errmsg=f"Delete container config file ERROR: {cp.stderr}")

    except subprocess.SubprocessError as e:
        module.fail_json(msg="", errmsg=f"{e.stderr}")
    except Exception as e:
        t, o, tb = sys.exc_info()
        module.fail_json(msg="", errmsg=f"{t}:{str(e)}")

    module.exit_json()


if __name__ == '__main__':
    main()
