#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dgw_change_param
short_description: Change DeviceGateway Configuration Parameter
description:
  - Make some changes to the original configuration and save it as a new configuration file.
version_added: 1.0.0
options:
  src:
    description:
      - Original configuration file path.
    type: str
    required: yes
  dest:
    description:
      - New configuration file path.
    type: str
    required: yes
  param_path:
    description:
      - The path to the parameter you want to change.
    type: str
    required: yes
  param:
    description:
      - Changed setting value.
    type: str
    required: yes
author:
  - TAKEBISHI(@GitHubID)
'''

EXAMPLES = r'''
- name: Parameter Change
  takebishi.dgw.dgw_change_param:
    src: "/tmp/export_original_settings.dxg"
    dest: "/tmp/export_new_settings.dxg"
    param_path: "DataSource.Device.AB1.group.folder1.group.bbb_tag.setting.name.value"
    param: "abc_tag"
  delegate_to: localhost
'''

RETURN = r'''
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
            dest=dict(required=True, type='str'),
            param_path=dict(required=True, type='str'),
            param=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )
    srcpath = module.params['src']
    dstpath = module.params['dest']
    param_path = module.params['param_path']
    param = module.params['param']

    try:
        # ファイルが存在しない場合は、異常終了
        if not os.path.exists(srcpath):
            module.fail_json(msg="", errmsg=f"{srcpath} not found")

        keys = param_path.split('.')
        last_key = keys.pop(-1)

        file = open(srcpath, 'r', encoding="utf-8")
        root_obj = json.load(file)
        file.close()
        obj = root_obj

        # 指定の階層のJSONオブジェクトを取得
        obj = find_object(keys, obj)

        if not (last_key in obj):
            module.fail_json(msg="", errmsg=f"Cannot find parameter key :'{last_key}'")
        obj[last_key] = param

    except json.JSONDecodeError as e:
        module.fail_json(msg="", errmsg=f"JSONDecodeError :{str(e)}")
    except DgwUtilError as e:
        module.fail_json(msg="", errmsg=f"DgwUtilError :{str(e)}")
    except Exception as e:
        t, o, tb = sys.exc_info()
        module.fail_json(msg="", errmsg=f"{t}:{str(e)}")

    try:
        json_string = json.dumps(root_obj)
        write_file = open(dstpath, 'w', encoding="utf-8")
        write_file.write(json_string)
        write_file.close()
    except Exception as e:
        t, o, tb = sys.exc_info()
        module.fail_json(msg="", errmsg=f"{t}:{str(e)}")

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
