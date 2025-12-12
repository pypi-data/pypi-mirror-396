import traceback
import json
from google.protobuf import json_format
import base64
from yangsuite import get_logger, get_path
from ysyangtree import TaskHandler, TaskException

from ysdevices import YSDeviceProfile
from ysgnmi.gnmi_util import GnmiMessage
from ysgnmi.device_plugin import GnmiSession
from jinja2 import Template
import yaml
from copy import deepcopy

log = get_logger(__name__)

try:
    from ystestmgr.rpcverify import RpcVerify
except ImportError:
    class RpcVerify:
        def process_operational_state(data, returns={}):
            return data


class GnmiException(Exception):
    pass


ansible_template = """
# Ansible will need some basic information to make sure
# it can connect to the target device before attempting
# a gNMI message. Ansible will look in the same directory
# as the playbook file for ansible.cfg
#
# Nearly all parameters in ansible.cfg can be overridden
# with ansible-playbook command line flags.

# Example of basic ansible.cfg file
#
#[defaults]
#inventory = ./ansible_host
#host_key_checking = False

# Example of basic ansible_host file referred to in
# ansible.cfg inventory.
#
#[MY_HOST_NAME]
#IP_ADDRESS_HERE ansible_user=USERNAME_HERE ansible_password=PASSWORD_HERE
#
#[MY_HOST_NAME:vars]
#ansible_port=gNMI_PORTNUMBER_HERE
#ansible_connection=nokia.grpc.gnmi
#ansible_gnmi_encoding=JSON
# "testout" is optional but handy for debugging the script.
#
- name : {{ p_name }}
  gather_facts: false
  hosts: MY_HOST_NAME

  collections:
  - nokia.grpc

  tasks:
  - name: {{ t_name }}
    gnmi_{{ op }}:{% if prefix %}
        prefix: /{% endif %}{% if op == 'get' %}
        type: {{ get_type }}{% elif op == 'subscribe' %}
        mode: {{ request_mode }}{% else %}
        {{ cntnt | indent(width=8, first=False, blank=False) }}{% endif %}{% if op in ['get', 'subscribe'] %}{% for path in paths %}
        {% if op == 'subscribe' %}subscription:{% elif op == 'get' %}path:{% endif %}
        {% if op == 'subscribe' %}- path: {{ path }}{% elif op == 'get' %}- {{ path }}{% endif %}{% if op == 'subscribe' %}
          mode: {{ sub_mode }}{% endif %}{% if sample_interval %}
          sampleInterval: {{ sample_interval }}{% endif %}{% endfor %}{% endif %}
    register: testout
  - name: dump test output
    debug:
        msg:{% raw %} '{{ testout.output }}' {% endraw %}
 """  # noqa


def get_capabilities(user, devprofile):
    """Get the gNMI capabilities from the given device profile.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with

    Raises:
      grpc.RpcError: in case of connection error

    Returns:
      dict: Representation of :class:`CapabilityResponse` protobuf.
    """
    try:
        session = GnmiSession.get_session(devprofile, user)
        caps = session.capabilities()
        stop_session(user, devprofile)
        if not caps:
            session.log.error('No capabilities returned.')
            raise Exception('No capabilities returned.')
        return json_format.MessageToDict(caps)

    except Exception as exc:
        stop_session(user, devprofile)
        raise exc


def get_request(user, devprofile, request):
    """Send a gNMI GET request to the given device.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Passed through as kwargs of :class:`GetRequest`
        constructor.

    Raises:
      grpc.RpcError: in case of a connection error
      ValueError: if request contains invalid values

    Returns:
      dict: Representation of :class:`GetResponse` protobuf
    """
    gnmi_string = ''
    if 'raw' in request:
        try:
            session = GnmiSession.get_session(devprofile, user)
            GnmiMessage.run_get(session, request['raw'])
        except Exception:
            log.error(traceback.format_exc())
    else:
        try:
            if not request.get('modules'):
                return {'error': 'No data requested from model.'}

            msg_type = request.get('action')
            if not msg_type:
                raise GnmiException('ERROR: gNMI message type missing.')
            gmsg = GnmiMessage(msg_type, request)
            gmcs = gmsg.get_messages()

            if not gmcs:
                raise Exception('No message defined for GET.')
            for gmc in gmcs:
                gnmi_string += json_format.MessageToJson(gmc.payload)
                gnmi_string += '\n'
                if request.get('run'):
                    session = GnmiSession.get_session(devprofile, user)
                    GnmiMessage.run_get(session, gmc.payload)
            if not request.get('run'):
                if not gnmi_string:
                    raise Exception(
                        'Build GET failed.  Check YANG Suite logs for details.'
                    )
                return gnmi_string
        except GnmiException as exc:
            raise exc
        except Exception:
            log.error(traceback.format_exc())


def get_results(user, devprofile):
    """Retrieve active log messages.

    Args:
      devprofile (ysdevices.YSDeviceProfile): Device profile class.
      user (str): YANG suite username.

    Returns:
      collections.deque: Queue of active log messages.
    """
    session = GnmiSession.get_session(devprofile, user)
    if not session.connected:
        return
    notifier = session.active_notifications.get(session)
    if notifier:
        if notifier.is_alive():
            session.results.append('Waiting for notification')
            if notifier.time_delta \
                    and notifier.time_delta < notifier.stream_max:
                notifier.stop()
    return session.result_queue()


def set_request(user, devprofile, request):
    """Send a gNMI SET request to the given device.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Passed through as kwargs of :class:`SetRequest`
        constructor.

    Raises:
      grpc.RpcError: in case of a connection error
    """
    if 'raw' in request:
        try:
            session = GnmiSession.get_session(devprofile, user)
            GnmiMessage.run_set(session, request['raw'])
        except Exception:
            log.error(traceback.format_exc())
    else:
        try:
            gnmi_string = ''
            if not request.get('modules'):
                return {'error': 'No data requested from model.'}

            msg_type = request.get('action')
            if not msg_type:
                raise GnmiException('ERROR: gNMI message type missing.')
            gmsg = GnmiMessage(msg_type, request)
            gmcs = gmsg.get_messages()

            if not gmcs:
                raise Exception('No messages defined for SET.')
            for gmc in gmcs:
                if gmc.json_val:
                    gnmi_dict = json_format.MessageToDict(gmc.payload)
                    """
                    by default upd['val'] is encoded by google protobuf so
                    decode the protobuf value to original value

                    if base64 is selected, format will be
                    Ex:
                    "val": {
                        "jsonIetfVal": "Im5hbWUyIg=="
                    }
                    """
                    for upd in gnmi_dict.get('update', []):
                        if 'val' in upd:
                            key_ = 'jsonVal'
                            if 'jsonIetfVal' in upd['val']:
                                key_ = 'jsonIetfVal'
                            decoded = base64.b64decode(upd['val'][key_])
                            upd['val'][key_] = decoded.decode('utf-8')
                        else:
                            pass
                    # If replace operation added for specific nodes,
                    # replace the encoded value to actual value
                    if gnmi_dict.get('replace', {}):
                        for upd in gnmi_dict['replace']:
                            if 'val' in upd:
                                key_ = 'jsonVal'
                                if 'jsonIetfVal' in upd['val']:
                                    key_ = 'jsonIetfVal'
                                decoded = base64.b64decode(upd['val'][key_])
                                upd['val'][key_] = decoded.decode('utf-8')
                            else:
                                pass
                    gnmi_string += json.dumps(gnmi_dict, indent=2)
                else:
                    gnmi_string += json_format.MessageToJson(gmc.payload)
                gnmi_string += '\n'
                if request.get('run'):
                    session = GnmiSession.get_session(devprofile, user)
                    GnmiMessage.run_set(session, gmc.payload)
            if not request.get('run'):
                if not gnmi_string:
                    raise Exception(
                        'Build SET failed.  Check YANG Suite logs for details.'
                    )
                return gnmi_string
        except GnmiException as exc:
            raise exc
        except Exception:
            log.error(traceback.format_exc())


def subscribe_request(user, devprofile, request):
    """Send a gNMI Subscribe request to the given device.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Passed through as kwargs of :class:`SetRequest`
        constructor.

    Raises:
      grpc.RpcError: in case of a connection error
    """
    if 'raw' in request:
        try:
            session = GnmiSession.get_session(devprofile, user)
            GnmiMessage.run_subscribe(session, request['raw'], request)
        except Exception:
            log.error(traceback.format_exc())
    else:
        gnmi_string = ''
        try:
            if not request.get('modules'):
                return {'error': 'No data requested from model.'}

            msg_type = request.get('action')
            if not msg_type:
                raise GnmiException('ERROR: gNMI message type missing.')
            sample_interval = request.get('sample_interval')
            if sample_interval:
                sample_interval = int(1e9) * int(sample_interval)
                request['sample_interval'] = sample_interval
            else:
                request['sample_interval'] = int(1e9) * 10
            gmsg = GnmiMessage(msg_type, request)
            gmcs = gmsg.get_messages()

            if not gmcs:
                raise Exception('No message defined for SUBSCRIBE.')
            for gmc in gmcs:
                gnmi_string += json_format.MessageToJson(gmc.payload)
                gnmi_string += '\n'
                if request.get('run'):
                    session = GnmiSession.get_session(devprofile, user)
                    GnmiMessage.run_subscribe(session, gmc.payload, request)
            if not request.get('run'):
                if not gnmi_string:
                    raise Exception(
                        'Build SUBSCRIBE failed.  Check YANG Suite logs '
                        'for details.'
                    )
                return gnmi_string
        except GnmiException as exc:
            raise exc
        except Exception:
            log.error(traceback.format_exc())


def stop_session(user, devprofile):
    """Stop subscribe threads, close channel, and remove session instance.

    Args:
      user (str): YANG Suite username.
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with.
    """
    if isinstance(devprofile, YSDeviceProfile):
        device = devprofile.base.profile_name
    else:
        device = str(devprofile)
    log.info("Stopping session {0}:{1}".format(user, device))
    GnmiSession.close(user, devprofile)


def show_gnmi_replay(request):
    """Return replay metadata formatted for gNMI protocol.

    Args:
      request (dict): Replay name and category.

    Raises:
      tasks.TaskException: in case of replay retreival error

    Returns:
      dict: Representation of :class:`GetResponse`, :class:`SetResponse`
    """
    # TODO: need variables from device or may fail on xpath
    request_dict = {}
    user = request.get('user')
    replay_name = request.get('replay')
    category = request.get('category')
    path = get_path('replays_dir', user=user)
    try:
        replay = TaskHandler.get_replay(path, category, replay_name)
        replay1 = deepcopy(replay)
        segments = replay['segments']
        gmcs = None
        gnmi_string = ''
        for segment in segments:
            segment['yang'].update(segment['yang']['format'])
            segment['yang'].pop('format', None)
            op = 'get'
            if segment['yang']['proto-op'] == 'edit-config':
                op = 'set'
            elif segment['yang']['proto-op'] == 'get-config':
                op = 'get'
            elif segment['yang']['proto-op']:
                op = segment['yang']['proto-op']
            gmsg = GnmiMessage(op, segment['yang'])
            gmcs = gmsg.get_messages()
        if not gmcs:
            raise Exception('No message defined for GET.')
        for gmc in gmcs:
            gnmi_dict = json_format.MessageToDict(gmc.payload)
            if op == 'set':
                for upd in gnmi_dict.get('update', []) +\
                 gnmi_dict.get('replace', []):
                    if 'val' in upd:
                        key_ = 'jsonVal'
                        if 'jsonIetfVal' in upd['val']:
                            key_ = 'jsonIetfVal'
                        decoded = base64.b64decode(upd['val'][key_])
                        upd['val'][key_] = decoded.decode('utf-8')
            gnmi_string += json.dumps(gnmi_dict, indent=2)
        request_dict['replay'] = gnmi_string
        request_dict['task'] = replay1

        # TODO: construct from replay

    except Exception as exe:
        log.error("Failed to generate gNMI replay %s", replay_name)
        log.debug(traceback.format_exc())
        raise TaskException("Failed to generate gNMI replay {0}\n{1}".format(
                replay_name,
                str(exe)
            )
        )

    return request_dict


def run_gnmi_replay(user, devprofile, request):
    """Run a replay over gNMI protocol.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Replay name and category.

    Raises:
      grpc.RpcError: in case of a connection error

    Returns:
      dict: Representation of :class:`GetResponse`, :class:`SetResponse`
    """
    user = request.get('user', '')
    response = {}

    gen_request = show_gnmi_replay(request)
    if gen_request['action'] == 'set':
        response = set_request(devprofile, user, gen_request['request'])
    elif gen_request['action'] == 'get':
        response = set_request(devprofile, user, gen_request['request'])
    else:
        raise TypeError(
                'gNMI "{0}" not supported.'.format(gen_request['action'])
            )

    return str(response)


def gen_ansible_api(request):
    result = {'rpc': 'Failed to generate gNMI RPC'}
    tplt = Template(ansible_template)
    rpcs = request

    proto_op_dict = {'get': 'get',
                     'set': 'config',
                     'subscribe': 'subscribe',
                     'capabilities': 'capabilities',
                     '': 'get',
                     }
    op = request.get('action', '')
    proto_op = proto_op_dict[op]
    p_name = request.get('p_name')
    t_name = request.get('t_name')
    prefix = request.get('prefix')
    encoding = request.get('encoding')
    origin = request.get('origin')
    rpcs['op'] = proto_op
    rpcs['p_name'] = p_name
    rpcs['t_name'] = t_name
    rpcs['prefix'] = prefix
    rpcs['encoding'] = encoding
    rpcs['origin'] = origin
    rpcs['get_type'] = request.get('get_type')
    rpcs['request_mode'] = request.get('request_mode')
    rpcs['sub_mode'] = request.get('sub_mode')
    sample_interval = request.get('sample_interval')
    if sample_interval:
        sample_interval = int(1e9) * int(sample_interval)
        request['sample_interval'] = sample_interval
    cntnt_list = {}

    if 'cfgd' in request:
        if request.get('string_rpc', True):
            # TODO
            raise ValueError('Cannot edit RPC for Ansible playbook.')
        else:
            cntnt_list_item = []
            for elem_item in request['cfgd']:
                path = remove_prefix(elem_item.get('xpath', ''))
                path = path.replace('"', '')
                if op == 'set':
                    if elem_item.get('edit-op', False):
                        opr = elem_item.get('edit-op')
                    else:
                        opr = 'update'
                    val = elem_item.get('value', '')

                    if not cntnt_list.get(opr, False):
                        cntnt_list[opr] = []
                    dict_val = {'path': path, 'val': val}
                    cntnt_list[opr].append(dict_val)
                else:
                    cntnt_list_item.append(path)
            if op in ['get', 'subscribe']:
                rpcs['paths'] = cntnt_list_item

            rpcs['cntnt'] = yaml.safe_dump(cntnt_list,
                                           default_flow_style=False,
                                           sort_keys=False)

    else:
        rpcs['cntnt'] = "Invalid Data"

    result['rpc'] = tplt.render(rpcs)
    return result


def remove_prefix(xp):
    new_ps = ''
    p_segs = xp.split('/')

    if p_segs[0] == '':
        p_segs = p_segs[1:]
        for ps in p_segs:
            if len(ps.split(':')) > 1:
                new_ps += '/' + ps.split(':')[1]
            else:
                new_ps += '/' + ps
        new_ps = new_ps[1:]
    return new_ps
