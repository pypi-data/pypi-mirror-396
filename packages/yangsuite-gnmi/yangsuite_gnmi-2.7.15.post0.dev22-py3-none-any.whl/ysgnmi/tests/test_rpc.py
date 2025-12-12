import unittest
import os
import json
import base64
from copy import deepcopy

from google.protobuf import json_format

from yangsuite.paths import set_base_path
from ysdevices import YSDeviceProfile
from ysgnmi import gnmi
from ysgnmi.gnmi_util import GnmiMessage, GnmiMessageConstructor

TESTDIR = os.path.join(os.path.dirname(__file__), 'data')
set_base_path(TESTDIR)

no_prefix_origin_oc_json_ietf_set_get = {
  'action': 'set',
  'device': 'ddmi-9500-2',
  'encoding': 'json_ietf',
  'get_type': 'ALL',
  'modules': {
      'openconfig-network-instance': {
          'configs': [
            {
              'edit-op': '',
              'datatype': 'leafref',
              'value': 'default',
              'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]' # noqa
            },
            {
                'edit-op': '',
                'datatype': 'string',
                'nodetype': 'leaf',
                'value': 'default',
                'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]/oc-netinst:config/oc-netinst:name' # noqa
            },
            {
                'edit-op': '',
                'datatype': 'leafref',
                'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]/oc-netinst:protocols/oc-netinst:protocol[identifier="oc-pol-types:OSPF"][name="100"]' # noqa
            },
            {
                'edit-op': '',
                'datatype': 'identityref',
                'nodetype': 'leaf',
                'value': 'oc-pol-types:OSPF',
                'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]/oc-netinst:protocols/oc-netinst:protocol[identifier="oc-pol-types:OSPF"][name="100"]/oc-netinst:config/oc-netinst:identifier' # noqa
            },
            {
                'edit-op': '',
                'datatype': 'string',
                'nodetype': 'leaf',
                'value': '100',
                'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]/oc-netinst:protocols/oc-netinst:protocol[identifier="oc-pol-types:OSPF"][name="100"]/oc-netinst:config/oc-netinst:name' # noqa
            },
            {
                'edit-op': '',
                'datatype': 'leafref',
                'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]/oc-netinst:protocols/oc-netinst:protocol[identifier="oc-pol-types:OSPF"][name="100"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[neighbor-address="1.1.1.1"]' # noqa
            },
            {
                'edit-op': '',
                'datatype': 'union',
                'nodetype': 'leaf',
                'value': '1.1.1.1',
                'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[name="default"]/oc-netinst:protocols/oc-netinst:protocol[identifier="oc-pol-types:OSPF"][name="100"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[neighbor-address="1.1.1.1"]/oc-netinst:config/oc-netinst:neighbor-address' # noqa
            }
          ],
          'namespace_modules': {
              'oc-netinst': 'openconfig-network-instance',
              'oc-pol-types': 'openconfig-policy-types'
          }
      }
  },
  'origin': 'openconfig',
  'platform': 'iosxe',
  'prefix': False,
  'run': False
}

no_prefix_origin_oc_json_ietf = {
  'update': [
    {
      'path': {
        'elem': [
          {
            'name': 'network-instances'
          },
          {
            'key': {
              'name': 'default'
            },
            'name': 'network-instance'
          },
          {
            'name': 'config'
          },
          {
            'name': 'name'
          }
        ],
        'origin': 'openconfig'
      }
    },
    {
      'path': {
        'elem': [
          {
            'name': 'network-instances'
          },
          {
            'key': {
              'name': 'default'
            },
            'name': 'network-instance'
          },
          {
            'name': 'protocols'
          },
          {
            'key': {
              'identifier': 'openconfig-policy-types:OSPF',
              'name': '100'
            },
            'name': 'protocol'
          },
          {
            'name': 'config'
          },
          {
            'name': 'identifier'
          }
        ],
        'origin': 'openconfig'
      }
    },
    {
      'path': {
        'elem': [
          {
            'name': 'network-instances'
          },
          {
            'key': {
              'name': 'default'
            },
            'name': 'network-instance'
          },
          {
            'name': 'protocols'
          },
          {
            'key': {
              'identifier': 'openconfig-policy-types:OSPF',
              'name': '100'
            },
            'name': 'protocol'
          },
          {
            'name': 'config'
          },
          {
            'name': 'name'
          }
        ],
        'origin': 'openconfig'
      }
    },
    {
      'path': {
        'elem': [
          {
            'name': 'network-instances'
          },
          {
            'key': {
              'name': 'default'
            },
            'name': 'network-instance'
          },
          {
            'name': 'protocols'
          },
          {
            'key': {
              'identifier': 'openconfig-policy-types:OSPF',
              'name': '100'
            },
            'name': 'protocol'
          },
          {
            'name': 'bgp'
          },
          {
            'name': 'neighbors'
          },
          {
            'key': {
              'neighbor-address': '1.1.1.1'
            },
            'name': 'neighbor'
          },
          {
            'name': 'config'
          },
          {
            'name': 'neighbor-address'
          }
        ],
        'origin': 'openconfig'
      }
    }
  ]
}

json_ietf_val_1 = 'default'

json_ietf_val_2 = 'openconfig-policy-types:OSPF'

json_ietf_val_3 = '1.1.1.1'


no_prefix_origin_oc_json_set_base_64 = {
  'update': [
    {
      'path': {
        'elem': [
          {
            'name': 'interfaces'
          },
          {
            'key': {
              'name': 'TenGigabitEthernet1/0/1'
              },
            'name': 'interface'
          },
          {
            'name': 'ethernet'
          },
          {
            'name': 'config'
          },
          {'name': 'enable-flow-control'}
        ],
        'origin': 'openconfig'
      },
      'val': {
        'jsonVal': 'dHJ1ZQ=='
      }
    }
  ]
}

json_val_one_leaf = True

no_prefix_no_origin_json_ietf_get = {
  'action': 'get',
  'device': 'ddmi-9500-2',
  'encoding': 'json_ietf',
  'modules': {
    'Cisco-IOS-XE-vlan-oper': {
      'configs': [
        {
          'datatype': 'uint16',
          'default': '',
          'nodetype': 'leaf',
          'xpath': '/vlan-ios-xe-oper:vlans/vlan-ios-xe-oper:vlan[id="100"]'
        },
        {
          'datatype': 'string',
          'default': '',
          'nodetype': 'leaf',
          'value': '',
          'xpath': '/vlan-ios-xe-oper:vlans/vlan-ios-xe-oper:vlan[id="100"]/vlan-ios-xe-oper:ports/vlan-ios-xe-oper:interface' # noqa
        },
        {
          'datatype': 'string',
          'default': '',
          'nodetype': 'leaf',
          'xpath': '/vlan-ios-xe-oper:vlans/vlan-ios-xe-oper:vlan[id="100"]/vlan-ios-xe-oper:vlan-interfaces[interface="TenGigabitEthernet1/0/1"]' # noqa
        },
        {
          'datatype': 'uint32',
          'default': '',
          'nodetype': 'leaf',
          'value': '',
          'xpath': '/vlan-ios-xe-oper:vlans/vlan-ios-xe-oper:vlan[id="100"]/vlan-ios-xe-oper:vlan-interfaces[interface="TenGigabitEthernet1/0/1"]/vlan-ios-xe-oper:subinterface' # noqa
        }
      ],
      'namespace_modules': {
        'cisco-semver': 'cisco-semver',
        'vlan-ios-xe-oper': 'Cisco-IOS-XE-vlan-oper'
      },
      'namespace_prefixes': {
        'cisco-semver': 'http://cisco.com/ns/yang/cisco-semver',
        'vlan-ios-xe-oper': 'http://cisco.com/ns/yang/Cisco-IOS-XE-vlan-oper'
      },
      'revision': '2019-05-01'}
    },
  'platform': 'iosxe',
  'run': False}

no_prefix_no_origin_json_ietf_get_dict = {
    'encoding': 'JSON_IETF',
    'path': [
        {'elem': [
            {'name': 'vlans'},
            {'key': {'id': '100'}, 'name': 'vlan'},
            {'name': 'ports'},
            {'name': 'interface'}
        ]},
        {'elem': [{'name': 'vlans'},
                  {'key': {'id': '100'}, 'name': 'vlan'},
                  {'key': {'interface': 'TenGigabitEthernet1/0/1'},
                  'name': 'vlan-interfaces'},
                  {'name': 'subinterface'}]}]
}

prefix_origin_rfc_json_ietf_subscribe = {
  'action': 'subscribe',
  'device': 'ddmi-9500-2',
  'encoding': 'json_ietf',
  'modules': {
      'Cisco-IOS-XE-lldp-oper': {
          'configs': [
              {
                  'datatype': 'string',
                  'default': '',
                  'name': '',
                  'nodetype': 'leaf',
                  'value': '',
                  'xpath': 'Cisco-IOS-XE-lldp-oper:lldp-entries/lldp-intf-details[if-name="TenGigabitEthernet1/0/1"]' # noqa
              }
          ],
          'namespace_modules': {
              'cisco-semver': 'cisco-semver',
              'lldp-ios-xe-oper': 'Cisco-IOS-XE-lldp-oper'
          },
          'namespace_prefixes': {
              'cisco-semver': 'http://cisco.com/ns/yang/cisco-semver',
              'lldp-ios-xe-oper': 'http://cisco.com/ns/yang/Cisco-IOS-XE-lldp-oper' # noqa
          },
          'revision': '2019-05-01'}},
  'origin': 'rfc7951',
  'platform': 'iosxe',
  'prefix': True,
  'run': False,
  'sample_interval': 20000000000,
  'request_mode': 'STREAM',
  'sub_mode': 'SAMPLE'}

prefix_origin_rfc_json_ietf_subscribe_dict = {
    'subscribe': {
        'encoding': 'JSON_IETF',
        'prefix': {'origin': 'rfc7951'},
        'subscription': [
            {
                'mode': 'SAMPLE',
                'path': {
                    'elem': [{'name': 'Cisco-IOS-XE-lldp-oper:lldp-entries'},
                             {'key': {'if-name': 'TenGigabitEthernet1/0/1'},
                              'name': 'lldp-intf-details'}]
                },
                'sampleInterval': '20000000000'}]
    }
}

no_prefix_origin_oc_json_set = {
  'action': 'set',
  'device': 'ddmi-9500-2',
  'encoding': 'json',
  'modules': {
    'openconfig-interfaces': {
      'configs': [
        {
          'datatype': 'boolean',
          'default': 'false',
          'name': 'enable-flow-control',
          'nodetype': 'leaf',
          'value': 'true',
          'xpath': '/interfaces/interface[name="TenGigabitEthernet1/0/1"]/ethernet/config/enable-flow-control' # noqa
        }
      ],
      'namespace_modules': {
        'cisco': 'oc-xr-mapping',
        'ianaift': 'iana-if-type',
        'if': 'ietf-interfaces',
        'inet': 'ietf-inet-types',
        'ldp': 'openconfig-mpls-ldp',
        'oc-acl': 'openconfig-acl',
        'oc-aft': 'openconfig-aft',
        'oc-aftni': 'openconfig-aft-network-instance',
        'oc-aftt': 'openconfig-aft-types',
        'oc-bgp': 'openconfig-bgp',
        'oc-bgp-pol': 'openconfig-bgp-policy',
        'oc-bgp-types': 'openconfig-bgp-types',
        'oc-bgprib-types': 'openconfig-rib-bgp-types',
        'oc-eth': 'openconfig-if-ethernet',
        'oc-ext': 'openconfig-extensions',
        'oc-if': 'openconfig-interfaces',
        'oc-igmp': 'openconfig-igmp',
        'oc-igmp-types': 'openconfig-igmp-types',
        'oc-inet': 'openconfig-inet-types',
        'oc-ip': 'openconfig-if-ip',
        'oc-ip-ext': 'openconfig-if-ip-ext',
        'oc-isis': 'openconfig-isis',
        'oc-isis-lsdb-types': 'openconfig-isis-lsdb-types',
        'oc-isis-pol': 'openconfig-isis-policy',
        'oc-isis-types': 'openconfig-isis-types',
        'oc-lag': 'openconfig-if-aggregate',
        'oc-loc-rt': 'openconfig-local-routing',
        'oc-mpls': 'openconfig-mpls',
        'oc-mpls-sr': 'openconfig-mpls-sr',
        'oc-mplst': 'openconfig-mpls-types',
        'oc-netinst': 'openconfig-network-instance',
        'oc-netinst-devs': 'cisco-nx-openconfig-network-instance-deviations',
        'oc-ni-l3': 'openconfig-network-instance-l3',
        'oc-ni-pol': 'openconfig-network-instance-policy',
        'oc-ni-types': 'openconfig-network-instance-types',
        'oc-ospf-pol': 'openconfig-ospf-policy',
        'oc-ospf-types': 'openconfig-ospf-types',
        'oc-ospfv2': 'openconfig-ospfv2',
        'oc-pf': 'openconfig-policy-forwarding',
        'oc-pim': 'openconfig-pim',
        'oc-pim-types': 'openconfig-pim-types',
        'oc-pkt-match': 'openconfig-packet-match',
        'oc-pkt-match-types': 'openconfig-packet-match-types',
        'oc-pol-types': 'openconfig-policy-types',
        'oc-rib-bgp': 'openconfig-rib-bgp',
        'oc-rpol': 'openconfig-routing-policy',
        'oc-rsvp': 'openconfig-mpls-rsvp',
        'oc-sr': 'openconfig-segment-routing',
        'oc-sr-rsvp-ext': 'openconfig-rsvp-sr-ext',
        'oc-srt': 'openconfig-segment-routing-types',
        'oc-types': 'openconfig-types',
        'oc-vlan': 'openconfig-vlan',
        'oc-vlan-types': 'openconfig-vlan-types',
        'oc-yang': 'openconfig-yang-types',
        'yang': 'ietf-yang-types'
      },
      'namespace_prefixes': {
        'ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type',
        'ietf-if': 'urn:ietf:params:xml:ns:yang:ietf-interfaces',
        'if': 'urn:ietf:params:xml:ns:yang:ietf-interfaces',
        'ift': 'urn:ietf:params:xml:ns:yang:iana-if-type',
        'oc-eth': 'http://openconfig.net/yang/interfaces/ethernet',
        'oc-ext': 'http://openconfig.net/yang/openconfig-ext',
        'oc-if': 'http://openconfig.net/yang/interfaces',
        'oc-inet': 'http://openconfig.net/yang/types/inet',
        'oc-ip': 'http://openconfig.net/yang/interfaces/ip',
        'oc-ip-ext': 'http://openconfig.net/yang/interfaces/ip-ext',
        'oc-lag': 'http://openconfig.net/yang/interfaces/aggregate',
        'oc-types': 'http://openconfig.net/yang/openconfig-types',
        'oc-vlan': 'http://openconfig.net/yang/vlan',
        'oc-vlan-types': 'http://openconfig.net/yang/vlan-types',
        'oc-yang': 'http://openconfig.net/yang/types/yang',
        'xr': 'http://cisco.com/ns/yang/cisco-oc-xr-mapping'
      },
      'revision': '2019-11-19'
    }
  },
  'origin': 'openconfig',
  'platform': 'iosxe',
  'prefix': False,
  'run': False
}

raw_set_dict = {
  "update": [
    {
      "path": {
        "origin": "openconfig",
        "elem": [
          {
            "name": "network-instances"
          },
          {
            "name": "network-instance",
            "key": {
              "name": "default"
            }
          }
        ]
      },
      "val": {
        "jsonIetfVal": {
          "config": {
            "name": "default"
          },
          "protocols": {
            "protocol": {
              "identifier": "openconfig-policy-types:OSPF",
              "name": "100",
              "config": {
                "identifier": "openconfig-policy-types:OSPF",
                "name": "100"
              },
              "ospfv2": {
                "global": {
                  "config": {
                    "router-id": "5.5.5.5"
                  }
                }
              }
            }
          }
        }
      }
    }
  ]
}

raw_get_dict = {
  "path": [
    {
      "origin": "openconfig",
      "elem": [
        {
          "name": "network-instances"
        },
        {
          "name": "network-instance",
          "key": {
            "name": "default"
          }
        },
        {
          "name": "protocols"
        },
        {
          "name": "protocol",
          "key": {
            "name": "100",
            "identifier": "openconfig-policy-types:OSPF"
          }
        },
        {
          "name": "ospfv2"
        },
        {
          "name": "global"
        },
        {
          "name": "config"
        },
        {
          "name": "router-id"
        }
      ]
    }
  ],
  "encoding": "JSON_IETF"
}

raw_subscribe_dict = {
  "subscribe": {
    "prefix": {
      "origin": "rfc7951"
    },
    "subscription": [
      {
        "path": {
          "elem": [
            {
              "name": "Cisco-IOS-XE-lldp-oper:lldp-entries"
            },
            {
              "name": "lldp-intf-details",
              "key": {
                "if-name": "TenGigabitEthernet1/0/1"
              }
            }
          ]
        },
        "mode": "SAMPLE",
        "sampleInterval": "20000000000"
      }
    ],
    "encoding": "JSON_IETF"
  }
}

prefix_origin_module_json_ietf_get = {
  'action': 'get',
  'base64': False,
  'device': None,
  'encoding': 'json_ietf',
  'get_type': 'ALL',
  'modules': {'openconfig-system': {'configs': [
   {'default': '',
    'nodetype': 'container',
    'xpath': '/oc-sys:system/oc-sys:grpc-server'}],
    'namespace_modules': {
        'oc-aaa': 'openconfig-aaa',
        'oc-aaa-types': 'openconfig-aaa-types',
        'oc-alarm-types': 'openconfig-alarm-types',
        'oc-alarms': 'openconfig-alarms',
        'oc-ext': 'openconfig-extensions',
        'oc-inet': 'openconfig-inet-types',
        'oc-log': 'openconfig-system-logging',
        'oc-opt-types': 'openconfig-transport-types',
        'oc-platform': 'openconfig-platform',
        'oc-platform-types': 'openconfig-platform-types',
        'oc-proc': 'openconfig-procmon',
        'oc-sys': 'openconfig-system',
        'oc-sys-mgmt': 'openconfig-system-management',
        'oc-sys-term': 'openconfig-system-terminal',
        'oc-sysdevs': 'cisco-xr-openconfig-system-deviations',
        'oc-types': 'openconfig-types',
        'oc-yang': 'openconfig-yang-types'},
    'namespace_prefixes': {
        'oc-aaa': 'http://openconfig.net/yang/aaa',
        'oc-aaa-types': 'http://openconfig.net/yang/aaa/types',
        'oc-alarm-types': 'http://openconfig.net/yang/alarms/types',
        'oc-alarms': 'http://openconfig.net/yang/alarms',
        'oc-ext': 'http://openconfig.net/yang/openconfig-ext',
        'oc-inet': 'http://openconfig.net/yang/types/inet',
        'oc-log': 'http://openconfig.net/yang/system/logging',
        'oc-platform': 'http://openconfig.net/yang/platform',
        'oc-proc': 'http://openconfig.net/yang/system/procmon',
        'oc-sys': 'http://openconfig.net/yang/system',
        'oc-sys-mgmt': 'http://openconfig.net/yang/system/management',
        'oc-sys-term': 'http://openconfig.net/yang/system/terminal',
        'oc-types': 'http://openconfig.net/yang/openconfig-types',
        'oc-yang': 'http://openconfig.net/yang/types/yang'},
    'revision': '2018-07-17'}},
  'origin': 'module',
  'prefix': True,
  'run': False}


prefix_origin_module_json_ietf = {
  "prefix": {
    "origin": "openconfig-system"
  },
  "path": [
    {
      "origin": "openconfig-system",
      "elem": [
        {
          "name": "system"
        },
        {
          "name": "grpc-server"
        }
      ]
    }
  ],
  "encoding": "JSON_IETF"
}

request_leaf_list = {
    'nodes': [
        {
            'datatype': 'identityref',
            'nodetype': 'leaf-list',
            'value': 'oc-types:IPV4',
            'xpath': '/oc-netinst:network-instances/\
              oc-netinst:network-instance[oc-netinst:name="test11"]/\
              oc-netinst:config/oc-netinst:enabled-address-families'
        }
    ],
    'namespace_modules': {
      'oc-netinst': 'openconfig-network-instance',
      'oc-types': 'openconfig-types'
    },
    'namespace_prefixes': {
      'oc-netinst': 'http://openconfig.net/yang/network-instances'
    }
}

set_container_leaf_list = {
    'nodes': [
        {
            'nodetype': 'container',
            'xpath': '/oc-netinst:network-instances/',
            'edit-op': 'update',
            'value': ''
        },
        {
            'datatype': 'leafref',
            'default': '',
            'key': True,
            'leafref_path': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="red11"]/oc-netinst:config/oc-netinst:name', # noqa
            'nodetype': 'leaf',
            'value': '',
            'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="red11"]' # noqa
        },
        {
            'nodetype': 'leaf',
            'datatype': 'string',
            'value': 'red11',
            'xpath': '/oc-netinst:network-instances/\
              oc-netinst:network-instance[oc-netinst:name="red11"]/\
              oc-netinst:config/oc-netinst:name',
        },
        {
            'nodetype': 'leaf-list',
            'datatype': 'identityref',
            'value': 'oc-types:IPV4',
            'xpath': '/oc-netinst:network-instances/\
              oc-netinst:network-instance[oc-netinst:name="red11"]/\
              oc-netinst:config/oc-netinst:enabled-address-families',
        },
        {
            'nodetype': 'leaf-list',
            'datatype': 'identityref',
            'value': 'oc-types:IPV6',
            'xpath': '/oc-netinst:network-instances/\
              oc-netinst:network-instance[oc-netinst:name="red11"]/\
              oc-netinst:config/oc-netinst:enabled-address-families',
        }
    ],
    'namespace_modules': {
      'oc-netinst': 'openconfig-network-instance',
      'oc-types': 'openconfig-types'
    },
    'namespace_prefixes': {
      'oc-netinst': 'http://openconfig.net/yang/network-instances'
    }
}

json_decoded_cont_leaf_list = {
  "update": [
    {
      "path": {
        "origin": "openconfig",
        "elem": [
          {
            "name": "network-instances"
          }
        ]
      }
    }
  ]
}

json_decoded_leaf_list = {
  "update": [
    {
      "path": {
        "origin": "openconfig",
        "elem": [
          {
            "name": "network-instances"
          },
          {
            "name": "network-instance",
            "key": {
              "name": "test11"
            }
          },
          {
            "name": "config"
          },
          {
            "name": "enabled-address-families"
          }
        ]
      }
    }
  ]
}

json_ietf_val_leaf_list = ["openconfig-types:IPV4"]

request_multiple_list = {
    'nodes': [
        {
            'datatype': 'uint32',
            'nodetype': 'leaf',
            'value': '10',
            'xpath': '/top:System/top:igmp-items/top:inst-items/top:dom-items/top:Dom-list[top:name="default"]/top:eventHist-items/top:EventHistory-list[top:type="nbm"]/top:size' # noqa
        },
        {
            'datatype': 'uint32',
            'nodetype': 'leaf',
            'value': '10',
            'xpath': '/top:System/top:igmp-items/top:inst-items/top:dom-items/top:Dom-list[top:name="default"]/top:eventHist-items/top:EventHistory-list[top:type="intfDebugs"]/top:size' # noqa
        }
    ],
    'namespace_modules': {
        'top': 'http://cisco.com/ns/yang/cisco-nx-os-device'
    },
    'namespace': {
        'top': 'http://cisco.com/ns/yang/cisco-nx-os-device'
    }
}


json_decoded_multiple_list = {
  'update': [
    {
      'path': {
        'elem': [
          {
            'name': 'System'
          },
          {
            'name': 'igmp-items'
          },
          {
            'name': 'inst-items'
          },
          {
            'name': 'dom-items'
          },
          {
            'name': 'Dom-list',
            'key': {
              'name': 'default'
            }
          },
          {
            'name': 'eventHist-items'
          },
          {
            'name': 'EventHistory-list',
            'key': {
              'type': 'nbm'
            }
          },
          {
            'name': 'size'
          }
        ]
      }
    },
    {
      'path': {
        'elem': [
          {
            'name': 'System'
          },
          {
            'name': 'igmp-items'
          },
          {
            'name': 'inst-items'
          },
          {
            'name': 'dom-items'
          },
          {
            'name': 'Dom-list',
            'key': {
              'name': 'default'
            }
          },
          {
            'name': 'eventHist-items'
          },
          {
            'name': 'EventHistory-list',
            'key': {
              'type': 'intfDebugs'
            }
          },
          {
            'name': 'size'
          }
        ]
      }
    }
  ]
}

json_val_decoded_multiple_list_1 = 10
json_val_decoded_multiple_list_2 = 10

format5 = {
    'encoding': 'JSON',
    'origin': ''
}

format6 = {
    'encoding': 'JSON_IETF',
    'origin': 'openconfig'
}


json_decoded_multiple_key_2 = {
  'update': [
      {
        'path': {
          'elem': [
              {
                'name': 'System'
              },
              {
                'name': 'mrib-items'
              },
              {
                'name': 'inst-items'
              },
              {
                'name': 'dom-items'
              },
              {
                'name': 'Dom-list',
                'key': {
                  'name': 'default'
                }
              },
              {
                'name': 'rpfselect-items'
              },
              {
                'name': 'RpfSelect-list',
                'key': {
                  'vrfName': '224.2.2.2/32',
                  'srcPfx': '224.1.1.1/32'
                }
              }
            ]
        }
       }
    ]
  }


request_multiple_list_2_keys = {
  'nodes': [
    {
      'edit-op': 'update',
      'datatype': '',
      'nodetype': 'leaf',
      'value': '',
      'xpath': '/top:System/top:mrib-items/top:inst-items/top:dom-items/top:Dom-list[top:name="default"]/\
        top:rpfselect-items/top:RpfSelect-list[top:vrfName="224.2.2.2/32"][top:srcPfx="224.1.1.1/32"]' # noqa
    },
    {
      'edit-op': 'update',
      'datatype': '',
      'value': 'test1',
      'nodetype': 'leaf',
      'xpath': '/top:System/top:mrib-items/top:inst-items/top:dom-items/top:Dom-list[top:name="default"]/\
        top:rpfselect-items/top:RpfSelect-list[top:vrfName="224.2.2.2/32"][top:srcPfx="224.1.1.1/32"]/\
          prop'  # noqa
    }
    ],
  'namespace_modules': {
      'top': 'http://cisco.com/ns/yang/cisco-nx-os-device'
    },
  'namespace': {
      'top': 'http://cisco.com/ns/yang/cisco-nx-os-device'
    }
}

json_val_decoded_multiple_key_2 = {'prop': 'test1'}

get_decimal = {
    'timestamp': '1663617852265767452',
    'update': [{'path': {
        'elem': [{'name': 'System'}, {'name': 'procsys-items'},
                 {'name': 'sysload-items'},
                {'name': 'loadAverage1m'}]},
                'val': {'decimalVal': 43.4}
                }]
}

set_edit_op_container = {
  'nodes': [
    {
      'datatype': 'leafref',
      'default': '',
      'key': True,
      'leafref_path': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:config/oc-netinst:name', # noqa
      'nodetype': 'leaf',
      'value': '',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]' # noqa
    },
    {
      'datatype': 'leafref',
      'default': '',
      'key': True,
      'leafref_path': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:config/oc-netinst:identifier', # noqa
      'nodetype': 'leaf',
      'value': '',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]' # noqa
    },
    {
      'datatype': 'leafref',
      'default': '',
      'key': True,
      'leafref_path': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:config/oc-netinst:name', # noqa
      'nodetype': 'leaf',
      'value': '',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]' # noqa
    },
    {
      'datatype': 'leafref',
      'default': '',
      'key': True,
      'leafref_path': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[oc-netinst:neighbor-address="122::2"]/oc-netinst:config/oc-netinst:neighbor-address', # noqa
      'nodetype': 'leaf',
      'value': '',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[oc-netinst:neighbor-address="122::2"]' # noqa
    },
    {
      'edit-op': 'replace',
      'nodetype': 'container',
      'value': '',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[oc-netinst:neighbor-address="122::2"]/oc-netinst:timers/oc-netinst:config' # noqa
    },
    {
      'datatype': 'decimal64',
      'default': '90',
      'nodetype': 'leaf',
      'value': '777',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[oc-netinst:neighbor-address="122::2"]/oc-netinst:timers/oc-netinst:config/oc-netinst:hold-time' # noqa
    },
    {
      'datatype': 'decimal64',
      'default': '30',
      'nodetype': 'leaf',
      'value': '77',
      'xpath': '/oc-netinst:network-instances/oc-netinst:network-instance[oc-netinst:name="DEFAULT"]/oc-netinst:protocols/oc-netinst:protocol[oc-netinst:identifier="BGP"][oc-netinst:name="default"]/oc-netinst:bgp/oc-netinst:neighbors/oc-netinst:neighbor[oc-netinst:neighbor-address="122::2"]/oc-netinst:timers/oc-netinst:config/oc-netinst:keepalive-interval' # noqa
    }
  ],
  'namespace_modules': {
      'oc-netinst': 'openconfig-network-instance',
  },
  'namespace_prefixes': {
      'oc-netinst': 'http://openconfig.net/yang/network-instances'
  }
}

set_edit_op_container_jdict = {
  'replace': [
    {
      'path': {
        'elem': [
          {
            'name': 'network-instances'
          },
          {
            'key': {'name': 'DEFAULT'},
            'name': 'network-instance'
          },
          {
            'name': 'protocols'
          },
          {
            'key': {'identifier': 'BGP', 'name': 'default'},
            'name': 'protocol'
          },
          {'name': 'bgp'},
          {'name': 'neighbors'},
          {
            'key': {'neighbor-address': '122::2'},
            'name': 'neighbor'
          },
          {'name': 'timers'},
          {'name': 'config'}
        ]
      }
    }
  ]
}

set_list_entries = {
  'nodes': [
    {
        'nodetype': 'container',
        'xpath': '/oc-sampling:sampling/oc-sflow:sflow',
        'edit-op': 'update',
        'value': ''
    },
    {
        'datatype': 'boolean',
        'default': '',
        'nodetype': 'leaf',
        'value': 'true',
        'xpath': '/oc-sampling:sampling/oc-sflow:sflow/oc-sflow:config/oc-sflow:enabled',
    },
    {
        'nodetype': 'leaf',
        'datatype': 'oc-inet:ipv4-address',
        'value': '4.4.4.4',
        'xpath': '/oc-sampling:sampling/oc-sflow:sflow/oc-sflow:config/oc-sflow:agent-id-ipv4',
    },
    {
        'nodetype': 'leaf',
        'datatype': 'oc-inet:ip-address',
        'value': '6.37.16.200',
        'xpath': '/oc-sampling:sampling/oc-sflow:sflow/oc-sflow:collectors/\
oc-sflow:collector[oc-sflow:address="6.37.16.200"]\
[oc-sflow:port="2055"]/oc-sflow:config/oc-sflow:address',
    },
    {
        'nodetype': 'leaf',
        'datatype': 'uint16',
        'value': '2055',
        'xpath': '/oc-sampling:sampling/oc-sflow:sflow/oc-sflow:collectors/\
oc-sflow:collector[oc-sflow:address="6.37.16.200"]\
[oc-sflow:port="2055"]/oc-sflow:config/oc-sflow:port',
    }
  ],
  'namespace_modules': {
    'oc-sampling': 'openconfig-sampling',
    'oc-sflow': 'openconfig-sampling-sflow'
  },
  'namespace_prefixes': {
    'oc-sampling': 'http://openconfig.net/yang/sampling'
  }
}

json_decoded_list_entries = {
  "update": [
    {
      "path": {
        "origin": "openconfig",
        "elem": [
          {
            "name": "sampling"
          },
          {
            "name": "openconfig-sampling-sflow:sflow"
          }
        ]
      },
    }
  ]
}


class TestGnmiTestRpc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    def test_prefix_origin_module_json_ietf(self):
        """GET set with prefix, orign module, and JSON_IETF."""
        r1 = deepcopy(prefix_origin_module_json_ietf_get)
        gmsg = GnmiMessage('get', r1)
        gmcs = gmsg.get_messages()
        for gmc in gmcs:
            jdict = json_format.MessageToDict(gmc.payload)
            self.assertEqual(jdict, prefix_origin_module_json_ietf)

    def test_set_oc_net_instance(self):
        """Verify a complex SET constructs json_val correct."""
        r1 = deepcopy(no_prefix_origin_oc_json_ietf_set_get)
        gmsg = GnmiMessage('set', r1)
        gmcs = gmsg.get_messages()
        for gmc in gmcs:
            jdict = json_format.MessageToDict(gmc.payload)
            jdict['update'][0].pop('val')
            jdict['update'][1].pop('val')
            jdict['update'][2].pop('val')
            jdict['update'][3].pop('val')
            self.assertEqual(jdict, no_prefix_origin_oc_json_ietf)
            self.assertEqual(gmc.json_val[0], json_ietf_val_1)
            self.assertEqual(gmc.json_val[1], json_ietf_val_2)
            self.assertEqual(gmc.json_val[3], json_ietf_val_3)

    def test_set_one_xpath(self):
        """Verify SET constructs json_val correct for one leaf node."""
        r4 = deepcopy(no_prefix_origin_oc_json_set)
        gmsg = GnmiMessage('set', r4)
        gmcs = gmsg.get_messages()
        for gmc in gmcs:
            self.assertEqual(
                json_format.MessageToDict(gmc.payload),
                no_prefix_origin_oc_json_set_base_64
            )
            self.assertEqual(gmc.json_val, json_val_one_leaf)

    def test_set_no_namespace_modules(self):
        """Verify SET constructs correct without namespace passed in."""
        r4 = deepcopy(no_prefix_origin_oc_json_set)
        r4['modules']['openconfig-interfaces'].pop('namespace_modules')
        gmsg = GnmiMessage('set', r4)
        gmcs = gmsg.get_messages()
        for gmc in gmcs:
            self.assertEqual(
                json_format.MessageToDict(gmc.payload),
                no_prefix_origin_oc_json_set_base_64
            )
            self.assertEqual(gmc.json_val, json_val_one_leaf)

    def test_get_2_paths(self):
        """Verify 2 paths are added to a GET (one with no list key)."""
        r2 = deepcopy(no_prefix_no_origin_json_ietf_get)
        gmsg = GnmiMessage('get', r2)
        gmcs = gmsg.get_messages()
        for gmc in gmcs:
            self.assertEqual(
                json_format.MessageToDict(gmc.payload),
                no_prefix_no_origin_json_ietf_get_dict
            )

    def test_subscribe_sample(self):
        """Verify subscribe message is constructed properly."""
        r3 = deepcopy(prefix_origin_rfc_json_ietf_subscribe)
        gmsg = GnmiMessage('subscribe', r3)
        gmcs = gmsg.get_messages()
        for gmc in gmcs:
            self.assertEqual(
                json_format.MessageToDict(gmc.payload),
                prefix_origin_rfc_json_ietf_subscribe_dict
            )

    def test_raw_set_base64(self):
        """Verify conversion of set dict to gNMI SetRequest."""
        raw_json = json.dumps(raw_set_dict)
        gnmi_msg = GnmiMessageConstructor.json_to_gnmi(
            'set', raw_json, **{'base64': True}
        )
        test_dict = json_format.MessageToDict(gnmi_msg)
        jval = base64.b64decode(test_dict['update'][0]['val']['jsonIetfVal'])
        jval = json.loads(base64.b64decode(jval).decode('utf-8'))
        test_dict['update'][0]['val']['jsonIetfVal'] = jval
        self.assertEqual(test_dict, raw_set_dict)

    def test_raw_set_json(self):
        """Verify conversion of set dict without base64 json_val."""
        raw_json = json.dumps(raw_set_dict)
        gnmi_msg = GnmiMessageConstructor.json_to_gnmi('set', raw_json)
        test_dict = json_format.MessageToDict(gnmi_msg)
        jval = gnmi_msg.update[0].val.json_ietf_val
        jval = json.loads(jval.decode('utf-8'))
        test_dict['update'][0]['val']['jsonIetfVal'] = jval
        self.assertEqual(test_dict, raw_set_dict)

    def test_raw_get(self):
        """Verify conversion of get dict to gNMI GetRequest."""
        raw_json = json.dumps(raw_get_dict)
        gnmi_msg = GnmiMessageConstructor.json_to_gnmi('get', raw_json)
        self.assertEqual(json_format.MessageToDict(gnmi_msg), raw_get_dict)

    def test_raw_subscribe(self):
        """Verify conversion of subscribe dict to gNMI SubscribeRequest."""
        raw_json = json.dumps(raw_subscribe_dict)
        gnmi_msg = GnmiMessageConstructor.json_to_gnmi('subscribe', raw_json)
        self.assertEqual(
            json_format.MessageToDict(gnmi_msg), raw_subscribe_dict
        )

    def test_set_edit_op_container(self):
        r5 = deepcopy(set_edit_op_container)
        gmc = GnmiMessageConstructor('set', r5, **format5)
        jdict = json_format.MessageToDict(gmc.payload)
        jdict['replace'][0].pop('val')
        self.assertEqual(jdict, set_edit_op_container_jdict)
        self.assertEqual(
          gmc.json_val, {'hold-time': 777.0, 'keepalive-interval': 77.0}
        )

    def test_set_multiple_list(self):
        """Verify a multiple entry list SET constructs json_val correct."""
        r5 = deepcopy(request_multiple_list)
        gmc = GnmiMessageConstructor('set', r5, **format5)
        jdict = json_format.MessageToDict(gmc.payload)
        jdict['update'][0].pop('val')
        jdict['update'][1].pop('val')
        self.assertEqual(jdict, json_decoded_multiple_list)
        self.assertEqual(gmc.json_val[0], json_val_decoded_multiple_list_1)
        self.assertEqual(gmc.json_val[1], json_val_decoded_multiple_list_2)

    def test_multiple_list_2(self):
        """Verify a multiple list with two keys constructs json_val correct."""
        r5 = deepcopy(request_multiple_list_2_keys)
        gmc = GnmiMessageConstructor('set', r5, **format5)
        jdict = json_format.MessageToDict(gmc.payload)
        jdict['update'][0].pop('val')
        self.assertEqual(jdict, json_decoded_multiple_key_2)
        self.assertEqual(gmc.json_val, json_val_decoded_multiple_key_2)

    def test_decimal_get(self):
        r6 = deepcopy(get_decimal)
        data = []
        GnmiMessage.decode_update(r6['update'], opfields=data)
        self.assertEqual(data[0]['value'],
                         get_decimal['update'][0]['val']['decimalVal'])

    def test_set_leaf_list(self):
        """Verify the leaf list entry in the SET request"""
        r7 = deepcopy(request_leaf_list)
        gmc = GnmiMessageConstructor('set', r7, **format6)
        jdict = json_format.MessageToDict(gmc.payload)
        jdict['update'][0].pop('val')
        self.assertEqual(jdict, json_decoded_leaf_list)
        self.assertEqual(gmc.json_val, json_ietf_val_leaf_list)

    def test_set_container_leaf_list(self):
        """Verify the json val with leaf-list entries"""
        r7 = deepcopy(set_container_leaf_list)
        gmc = GnmiMessageConstructor('set', r7, **format6)
        jdict = json_format.MessageToDict(gmc.payload)
        jdict['update'][0].pop('val')
        self.assertEqual(jdict, json_decoded_cont_leaf_list)
        self.assertEqual(
          gmc.json_val, {'network-instance':
                         {"name": "red11", "config": {"name": "red11",
                          "enabled-address-families": ["openconfig-types:IPV4",
                                                       "openconfig-types:IPV6"]}}})

    def test_set_list_entries(self):
        """Verify list entries enclosed within [] in jsonval"""
        raw_json = deepcopy(set_list_entries)
        gmc = GnmiMessageConstructor('set', raw_json, **format6)
        jdict = json_format.MessageToDict(gmc.payload)
        jdict['update'][0].pop('val')
        self.assertEqual(jdict, json_decoded_list_entries)
        self.assertEqual(
          gmc.json_val, {
              "openconfig-sampling-sflow:config": {
                  "openconfig-sampling-sflow:enabled": True,
                  "openconfig-sampling-sflow:agent-id-ipv4": "4.4.4.4"
              },
              "openconfig-sampling-sflow:collectors": {
                  "openconfig-sampling-sflow:collector": [
                      {
                          "openconfig-sampling-sflow:address": "6.37.16.200",
                          "openconfig-sampling-sflow:port": "2055",
                          "openconfig-sampling-sflow:config": {
                              "openconfig-sampling-sflow:address": "6.37.16.200",
                              "openconfig-sampling-sflow:port": 2055
                          }
                      }
                  ]
              }
          })


class TestGnmiTestShim(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.devprofile = YSDeviceProfile.get('mydevice')

    def test_set_api(self):
        """Verify get request is correct through get_request API."""
        r1 = deepcopy(no_prefix_origin_oc_json_ietf_set_get)
        resp = gnmi.set_request('test', self.devprofile, r1)
        jdict = json.loads(resp)
        val0 = jdict['update'][0].pop('val')
        val1 = jdict['update'][1].pop('val')
        jdict['update'][2].pop('val')
        val3 = jdict['update'][3].pop('val')
        self.assertEqual(jdict, no_prefix_origin_oc_json_ietf)
        self.assertEqual(val0['jsonIetfVal'].replace('"', ''), json_ietf_val_1)
        self.assertEqual(val1['jsonIetfVal'].replace('"', ''), json_ietf_val_2)
        self.assertEqual(val3['jsonIetfVal'].replace('"', ''), json_ietf_val_3)

    def test_get_api(self):
        """Verify a complex SET is correct through set_request API."""
        r2 = deepcopy(no_prefix_no_origin_json_ietf_get)
        resp = gnmi.get_request('test', self.devprofile, r2)
        jdict2 = json.loads(resp)
        self.assertEqual(jdict2, no_prefix_no_origin_json_ietf_get_dict)

    def test_subscibe_api(self):
        """Verify a subscribe request is correct through subscribe API."""
        r3 = deepcopy(prefix_origin_rfc_json_ietf_subscribe)
        r3['sample_interval'] = 20
        resp = gnmi.subscribe_request('test', self.devprofile, r3)
        jdict3 = json.loads(resp)
        self.assertEqual(jdict3, prefix_origin_rfc_json_ietf_subscribe_dict)
