#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dgw_get_param
short_description: Get DeviceGateway Configuration Parameter
description:
  - Get the parameter value from configuration file.
version_added: 1.0.0
options:
  src:
    description:
      - Configuration file path.
    type: str
    required: yes
  param_path:
    description:
      - The path to the parameter you want to get.
    type: str
    required: yes
author: "TAKEBISHI(@GitHubID)"
'''

EXAMPLES = r'''
- name: Parameter Get
  takebishi.dgw.dgw_get_param:
    src: "/tmp/export_original_settings.dxg"
    param_path: "DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value"
  register: result
  delegate_to: localhost
- name: Display result
  debug:
    msg: "DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value => {{result.param}}"
  delegate_to: localhost
'''

RETURN = r'''
param:
  description: The parameter value corresponding to the specified key.
  returned: success
  type: str
errmsg:
  description: Detail error message.
  returned: failure
  type: str
'''


import os
import sys
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.takebishi.dgw.plugins.module_utils.dgw_util import find_object, DgwUtilError


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            param_path=dict(required=True, type='str'),
        ),
        supports_check_mode=False
    )
    filepath = module.params['src']
    param_path = module.params['param_path']

    try:
        # ファイルが存在しない場合は、異常終了
        if not os.path.exists(filepath):
            module.fail_json(msg="", errmsg="%s not found" % (filepath))

        keys = param_path.split('.')

        file = open(filepath, 'r', encoding="utf-8")
        obj = json.load(file)
        file.close()

        obj = find_object(keys, obj)

    except json.JSONDecodeError as e:
        module.fail_json(msg="", errmsg=f"JSONDecodeError :{str(e)}")
    except DgwUtilError as e:
        module.fail_json(msg="", errmsg=f"DgwUtilError :{str(e)}")
    except Exception as e:
        t, o, tb = sys.exc_info()
        module.fail_json(msg="", errmsg=f"{t}:{str(e)}")

    module.exit_json(param=str(obj))


if __name__ == '__main__':
    main()
