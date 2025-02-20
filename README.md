# TAKEBISHI DeviceGateway Ansible Collection

## Description

DeviceGateway Ansible Collection is a module for automating the configuration and management of DeviceGateway.

## Requirements

- Ansible >= 2.19.0
- Python >= 3.11

## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```
ansible-galaxy collection install takebishi.dgw
```

You can also include it in a requirements.yml file and install it with ansible-galaxy collection install -r requirements.yml, using the format:


```yaml
collections:
  - name: takebishi.dgw
```

Note that if you install any collections from Ansible Galaxy, they will not be upgraded automatically when you upgrade the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```
ansible-galaxy collection install takebishi.dgw --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version 1.0.0:

```
ansible-galaxy collection install takebishi.dgw:==1.0.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.


In addition to the above boilerplate, this section should include any additional details specific to your collection, and what to expect at each step and after installation. Be sure to include any information that supports the installation process, such as information about authentication and credentialing. 

## Use Cases

### Use Case 1 - Get configuration from DeviceGateway
```
---
- name: Get configuration file
  takebishi.dgw.import_config_file:
    dgw_container_type: docker
    dgw_container_name: devicegateway
    host_setting_fpath: /tmp/get_settings.txt
```

### Use Case 2 - Show parameter
```
- name: Get parameter
  takebishi.dgw.dgw_get_param:
    src: /tmp/get_settings.txt
    param_path: "Event.Item.event1.action.sleep1.setting.sleeptime.value"
  register: get_res

- name: Display parameter
  debug:
    msg: "value = {{get_res.param}}"
```

### Use Case 3 - Change the parameters and update DeviceGateway.
```
---
- name: Change parameter
  takebishi.dgw.dgw_change_param:
    src: /tmp/get_settings.txt
    dest: /tmp/changed_setting.dxg
    param_path: "Event.Item.event1.action.sleep1.setting.sleeptime.value"
    param: "800"

- name: Export config file
  takebishi.dgw.dgw_export_config_file:
    dgw_container_type: docker
    dgw_container_name: devicegateway
    host_setting_fpath: /tmp/changed_setting.dxg
```

## Testing

Tested with Ansible v2.19 and DeviceGateway (DGW-D20) Ver 3.5.0


## Support

For any support request, please reach out to [faweb](https://www.faweb.net/en/support/form/).


## Release Notes and Roadmap

Please see the [release notes](https://github.com/ssol-smartcs/takebishi.dgw/CHANGELOG.rst) for the latest updates to the DeviceGateway Ansible collection.


## Related Information

- [DeviceGateway](https://www.faweb.net/en/product/devicegateway)


## License Information

DeviceGateway Ansible Collection is licensed under the [GNU General Public License Version 3](https://www.gnu.org/licenses/gpl-3.0.html).
This software includes programs which are modified from Ansible.
For the full text, see the COPYING file.