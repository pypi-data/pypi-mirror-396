import traceback
import os
import ssl
import sys
import pdb
import time
import json
import logging
from datetime import datetime
from threading import Thread, Event
from collections import OrderedDict, deque
from pprint import pformat

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from yang.connector import proto
import grpc

from yangsuite import get_logger, get_path
from ysdevices import YSDeviceProtocolPlugin, YSDeviceProfile


log = get_logger()
gnmi_device_log = logging.getLogger('gnmi_device')


class GnmiPlugin(YSDeviceProtocolPlugin):
    """Device profile extensions for gNMI."""

    label = "gNMI"
    key = 'gnmi'

    @classmethod
    def data_format(cls):
        result = OrderedDict()
        result['enabled'] = {
            'label': 'Device supports gNMI',
            'type': 'boolean',
            'default': False,
        }
        result['platform'] = {
            'label': 'Platform',
            'type': 'enum',
            'choices': [
                ('iosxe', 'IOS XE'),
                ('iosxr', 'IOS XR'),
                ('iosnx', 'IOS NX'),
            ],
            'required': True,
            'default': 'iosxe',
        }
        result['port'] = {
            'label': 'gNMI insecure port',
            'type': 'int',
            'description': 'Port number the device listens on',
            'min': 1,
            'max': 65535,
            'default': 50052,
            'required': True,
        }
        result['secure_port'] = {
            'label': 'gNMI secure port',
            'type': 'int',
            'description': 'Port number the device listens on',
            'min': 1,
            'max': 65535,
            'default': 9339,
            'required': True,
        }
        result['secure'] = {
            'label': 'Use TLS Certificate',
            'type': 'boolean',
            'default': False,
        }
        result['secure_override'] = {
            'label': 'TLS host override',
            'type': 'string',
            'description': 'Set to CN of certificate (hostname requires DNS).',
            'minLength': 1,
        }
        return result

    @classmethod
    def check_reachability(cls, devprofile):
        """Check whether the described device speaks gNMI.

        Returns:
          tuple: ('gNMI', result, message)
        """
        session = None
        try:
            ys_data = devprofile.dict().get('yangsuite', {})
            user = ys_data.get('user', '')
            session = GnmiSession(devprofile.base.profile_name, user)
        except Exception as exc:
            return ('gNMI', False, str(exc))
        try:
            caps = session.capabilities()
            if not caps:
                port_may_be = ''
                secure_port = ''
                if devprofile.gnmi.platform == 'iosxe':
                    if devprofile.gnmi.secure:
                        secure_port = 'secure '
                        if devprofile.gnmi.secure_port != 9339:
                            port_may_be = 9339
                    elif devprofile.gnmi.port != 50052:
                        port_may_be = 50052
                elif devprofile.gnmi.platform == 'iosnx':
                    if devprofile.gnmi.secure:
                        secure_port = 'secure '
                        if devprofile.gnmi.secure_port != 50051:
                            port_may_be = 50051
                    elif devprofile.gnmi.port != 50051:
                        port_may_be = 50051
                if port_may_be:
                    msg = 'Try setting {0}port to {1}.'.format(
                        secure_port,
                        port_may_be
                    )
                    raise Exception(msg)
                raise Exception('No capabilities returned.')
            return ('gNMI', True, "success")
        except Exception as exc:
            msg = ''
            log.error(traceback.format_exc())
            if hasattr(exc, 'details'):
                msg = exc.details()
            else:
                msg = str(exc)
            return ('gNMI', False, msg)
        finally:
            if session:
                try:
                    session.log.info('Stopping session {0}:{1}'.format(
                        user, devprofile.base.profile_name
                    ))
                    GnmiSession.destroy(devprofile)
                except Exception:
                    pass


class GnmiLogHandler(logging.Handler):

    @property
    def gnmi_session(self):
        return self._gnmi_session

    @gnmi_session.setter
    def gnmi_session(self, session):
        self._gnmi_session = session

    def emit(self, record):
        self.gnmi_session.results.append(record.msg)


class ForkedPdb(pdb.Pdb):
    """A pdb subclass for debugging GnmiNotification.

    Usage: ForkedPdb().set_trace()
    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin


class GnmiNotification(Thread):
    """Thread listening for event notifications from the device."""

    def __init__(self, response, **request):
        Thread.__init__(self)
        self._stop_event = Event()
        self.log = request.get('log')
        if self.log is None:
            self.log = logging.getLogger(__name__)
            self.log.setLevel(logging.DEBUG)
        self.request = request
        self.mode = request.get('request_mode')
        self.responses = response
        self.returns = request.get('returns')
        self.response_verify = request.get('verifier')
        self.decode_response = request.get('decode')
        self.namespace = request.get('namespace', {})
        self.sub_mode = request.get('sub_mode')
        self.encoding = request.get('encoding')
        self.sample_interval = request.get('sample_interval')
        self.stream_max = request.get('stream_max', 0)
        self.time_delta = 0
        self.result = None

    def process_opfields(self, response):
        """Decode response and verify result.

        Decoder callback returns desired format of response.
        Verify callback returns verification of expected results.

        Args:
          response (proto.gnmi_pb2.Notification): Contains updates that
              have changes since last timestamp.
        """
        try:
            json_dicts, opfields = self.decode_response(
                response, self.namespace
            )
            if len(json_dicts):
                for json_dict in json_dicts:
                    if json_dict:
                        msg = 'JSON Decoded\n' + '=' * 12 + '\n' + json.dumps(
                            json_dict, indent=2
                        )
                        self.log.info(msg)
            if opfields:
                msg = 'Xpath/Value\n' + '=' * 11 + '\n' + pformat(opfields)
                self.log.info(msg)
            if opfields:
                self.result = self.response_verify(
                    opfields, self.returns.copy()
                )
        except Exception as exc:
            self.log.error(str(exc))
        finally:
            if self.mode in ['ONCE', 'POLL']:
                self.log.info(f'Subscribe {self.mode} processed')
                self.stop()

    def run(self):
        """Check for inbound notifications."""
        t1 = datetime.now()
        self.log.info('Subscribe notification active')
        try:
            while True:
                for response in self.responses:
                    if response.HasField('sync_response'):
                        self.log.info('Subscribe sync_response')
                    if response.HasField('update'):
                        self.log.info(response)
                        self.log.info('Processing returns...')
                        self.process_opfields(response)

                if self.stopped():
                    self.time_delta = self.stream_max
                    self.log.info("Terminating notification thread")
                    break
                if self.stream_max:
                    t2 = datetime.now()
                    td = t2 - t1
                    self.time_delta = td.seconds
                    if td.seconds > self.stream_max:
                        self.log.info("Notification thread is done")
                        self.stop()
                        break
                time.sleep(.25)

        except Exception as exc:
            msg = ''
            if hasattr(exc, 'details'):
                msg += 'details: ' + exc.details()
            if hasattr(exc, 'debug_error_string'):
                msg += exc.debug_error_string()
            if not msg:
                msg = str(exc)
            self.result = msg

    def stop(self):
        self.log.info("Stopping notification stream")
        self._stop_event.set()

    def stopped(self):
        if self._stop_event.is_set():
            self.log.info("Notification stream is stopped")
        return self._stop_event.is_set()


class CiscoAuthPlugin(grpc.AuthMetadataPlugin):
    """A plugin which adds username/password metadata to each call."""

    def __init__(self, username, password):
        super(CiscoAuthPlugin, self).__init__()
        self.username = username
        self.password = password

    def __call__(self, context, callback):
        callback(
            [("username", self.username), ("password", self.password)],
            None
        )


class GnmiSession:
    """Session handling for gNMI connections."""

    instances = {}
    active_notifications = {}

    def __init__(self, key, user, custom_log=None):
        root = None
        chain = None
        private_key = None
        self.channel = None
        self.results = deque()
        self.metadata = None

        self.key = key
        self.dev_profile = YSDeviceProfile.get(key)
        self.secure = self.dev_profile.gnmi.secure

        if custom_log:
            self.log = custom_log
        else:
            self.log = gnmi_device_log
            self.log.setLevel(logging.INFO)
            gnmi_log_handler = GnmiLogHandler()
            gnmi_log_handler.gnmi_session = self
            gnmi_log_handler.setLevel(logging.INFO)
            log.addHandler(gnmi_log_handler)
            self.log.addHandler(gnmi_log_handler)

        self.timeout = self.dev_profile.base.timeout

        if self.secure:
            port = self.dev_profile.gnmi.secure_port
        else:
            port = self.dev_profile.gnmi.port
        target = '{0}:{1}'.format(
            self.dev_profile.base.address,
            port
        )
        options = [('grpc.max_receive_message_length', -1)]

        user_device_path = get_path('user_devices_dir', user=user)
        if self.dev_profile.gnmi.secure:
            root = self.dev_profile.base.dict().get('certificate')
            if root:
                rootfile = os.path.join(
                    user_device_path,
                    self.dev_profile.base.profile_name,
                    root
                )
                if os.path.isfile(rootfile):
                    root = open(rootfile, 'rb').read()
                else:
                    self.log.error(
                        'Root certificate file not found. {0}'.format(
                            rootfile
                        )
                    )
                    root = None
            else:
                # IOS XR has this choice
                root = self._get_cert_from_target(
                    self.dev_profile.base.address,
                    self.dev_profile.gnmi.secure_port,
                )
                if not root:
                    root = None
            chain = self.dev_profile.base.dict().get('clientcert')
            if not chain:
                chain = self.dev_profile.base.dict().get('devicekey')
            if chain:
                chainfile = os.path.join(
                    user_device_path,
                    self.dev_profile.base.profile_name,
                    chain
                )
                if os.path.isfile(chainfile):
                    chain = open(chainfile, 'rb').read()
                else:
                    log.error('Client certificate file not found. {0}'.format(
                        chainfile
                    ))
                    chain = None
            else:
                chain = None
            private_key = self.dev_profile.base.dict().get('clientkey')
            if private_key:
                privatefile = os.path.join(
                    user_device_path,
                    self.dev_profile.base.profile_name,
                    private_key
                )
                if os.path.isfile(privatefile):
                    private_key = open(privatefile, 'rb').read()
                else:
                    log.error('Client key file not found. {0}'.format(
                        privatefile
                    ))
            else:
                private_key = None

            if root:
                if private_key is None or chain is None:
                    # Need key and chain set together or it will crash.
                    private_key = chain = None

            if any([root, private_key, chain]):
                if self.dev_profile.gnmi.secure_override:
                    self.log.info('Host override secure channel')
                    override_name = self._get_cn_from_cert(
                        root,
                        self.dev_profile.gnmi.secure_override
                    )
                    options.append(
                        (
                            'grpc.ssl_target_name_override',
                            override_name
                        ),
                    )
                self.log.info("Connecting secure channel")
                channel_ssl_creds = grpc.ssl_channel_credentials(
                    root, private_key, chain
                )
                ssl_metadata = grpc.metadata_call_credentials(
                    CiscoAuthPlugin(
                        self.dev_profile.base.username,
                        self.dev_profile.base.password
                    )
                )
                channel_creds = grpc.composite_channel_credentials(
                    channel_ssl_creds, ssl_metadata
                )
                self.channel = grpc.secure_channel(
                    target, channel_creds, options
                )
            else:
                self.log.error('No root, client, or key for secure channel')
                raise ValueError('No root, client, or key for secure channel')
        else:
            self.channel = grpc.insecure_channel(target, options)
            self.metadata = [
                ("username", self.dev_profile.base.username),
                ("password", self.dev_profile.base.password),
            ]
            self.log.info("Connecting insecure channel")

        self.service = proto.gnmi_pb2_grpc.gNMIStub(self.channel)

    def _get_cn_from_cert(self, cert_pem, name=''):
        """Attempts to derive the CN from a supplied certficate.
        Defaults to first found if multiple CNs identified.
        """
        cert_cn = None
        cert_parsed = x509.load_pem_x509_certificate(
            cert_pem,
            default_backend()
        )
        cert_cns = cert_parsed.subject.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME
        )
        if len(cert_cns) > 0:
            if len(cert_cns) > 1:
                log.warning('Multiple CNs found for certificate.')
                cert_cn = name
            else:
                cert_cn = cert_cns[0].value
            log.debug("Using %s as certificate CN.", cert_cn)
        else:
            if name:
                log.warning('No CN found for certificate, using "{0}"'.format(
                    name
                ))
                return name
            else:
                log.warning('No CN found for certificate')
        return cert_cn

    def _get_cert_from_target(self, address, port):
        root = ssl.get_server_certificate((address, port)).encode()
        if not root:
            return None
        return root

    @property
    def connected(self):
        return self.channel

    @classmethod
    def get_session(cls, key, user, custom_log=None):
        """Retrieve or create a GNMI session instance.

        The key can be a string or a device profile.

        Args:
          key (str): Device name or uses the base.profile_name as key.
        Returns:
          GnmiSession
        """
        # accept device name or profile
        if not isinstance(key, YSDeviceProfile):
            dev_profile = YSDeviceProfile.get(key)
        else:
            dev_profile = key
            key = dev_profile.base.profile_name

        if key not in cls.instances:
            if dev_profile.gnmi.enabled:
                cls.instances[key] = cls(key, user, custom_log)
            else:
                raise ValueError("gNMI not enabled in device profile")

        return cls.instances[key]

    @classmethod
    def close(cls, user, key):
        """Remove the session instance from the cache.

        The key can be a string or a device profile.

        Args:
          key (str): Device name or uses the base.profile_name as key.
        """
        if isinstance(key, YSDeviceProfile):
            key = key.base.profile_name

        if key in cls.instances:
            session = cls.instances.pop(key)
            if session in session.active_notifications:
                session.log.info(
                    'Stopping session subscribe stream {0}:{1}'.format(
                        user, key
                    )
                )
                subscribe_thread = session.active_notifications[session]
                subscribe_thread.stop()

            session.log.info('Stopping session {0}:{1}'.format(
                user, key
            ))
            if session.connected:
                session.disconnect()

    def capabilities(self):
        request = proto.gnmi_pb2.CapabilityRequest()
        return self.service.Capabilities(request, metadata=self.metadata)

    def get(self, request):
        return self.service.Get(request, metadata=self.metadata)

    def set(self, request):
        return self.service.Set(request, metadata=self.metadata)

    def subscribe(self, request_iter):
        return self.service.Subscribe(request_iter,  metadata=self.metadata)

    def disconnect(self):
        if hasattr(self, 'channel'):
            self.channel.close()
            del self.channel._channel
            self.channel = None

    def result_queue(self):
        data = []
        while len(self.results):
            entry = self.results.popleft()
            data.append(str(entry))
        return {'result': data}


if __name__ == '__main__':
    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'yangsuite.settings.dev.develop'
    os.environ['MEDIA_ROOT'] = '/Users/miott/ysuite/install/data'
    django.setup()
    sess = GnmiSession('MGBL-R2-5508', 'yangsuite-developer')
