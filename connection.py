from messages import (
    get_payload,
    verify_headers,
    Version,
    Verack,
    NetworkAddress,
    WrongChecksumError,
)

import threading
import socket
import time
import random
import re
from ipaddress import IPv6Address


class Connection(threading.Thread):
    def __init__(self, socket, address, node):
        super().__init__()

        self.node = node
        self.socket = socket
        self.address = address

        self.terminate_flag = threading.Event()

        self.messages = []
        self.buffer = b""

        self.received_version = False
        self.connected = False

        self.conn_time = time.time()
        self.connect()

    def send(self, data):
        self.socket.sendall(bytes.fromhex(self.node.magic) + data)

    def stop(self):
        self.terminate_flag.set()

    def connect(self):
        services = 1  # TODO
        version = Version(
            version=70015,  # TODO
            services=services,
            timestamp=int(time.time()),
            addr_recv=NetworkAddress(
                1, IPv6Address("::ffff:" + self.address[0]), self.address[1]
            ),  # TODO
            addr_from=NetworkAddress(
                services, IPv6Address("::ffff:" + "0.0.0.0"), 8333
            ),  # TODO
            nonce=random.randint(0, 0xFFFFFFFFFFFF),
            user_agent="/Btclib/",
            start_height=0,  # TODO
            relay=True,  # TODO
        )
        self.send(version.serialize())

    def accep_version(self, version_message):
        return True

    def validate_handshake(self):
        if not self.received_version:
            if self.messages:
                # first message must be version
                if not self.messages[0][0] == "version":
                    self.stop()
                else:
                    version_message = Version.deserialize(self.messages[0][1])
                    if self.accep_version(version_message):
                        # self.address[1] = version_message.port TODO
                        print(1)
                        self.send(Verack().serialize())
                        print(2)
                        self.messages = self.messages[1:]
                        self.received_version = True
                    else:
                        self.stop()
        if self.received_version and not self.connected:
            if self.messages:
                # second message must be verack
                if not self.messages[0][0] == "verack":
                    self.stop()
                else:
                    self.messages = self.messages[1:]
                    self.connected = True

    def parse_messages(self):
        try:
            verify_headers(self.buffer)
            message_length = int.from_bytes(self.buffer[16:20], "little")
            message = get_payload(self.buffer)
            self.buffer = self.buffer[24 + message_length :]
            self.messages.append(message)
        except WrongChecksumError:
            # https://stackoverflow.com/questions/30945784/how-to-remove-all-characters-before-a-specific-character-in-python
            self.buffer = re.sub(
                f"^.*?{self.node.magic}".encode(), self.node.magic.encode(), self.buffer
            )
        except Exception as e:
            pass

    def handle_messages(self):
        if not self.connected:
            self.validate_handshake()
        else:
            pass

    def run(self):
        self.socket.settimeout(0.0)
        while not self.terminate_flag.is_set():
            try:  # TODO: exit if other side is closed
                line = self.socket.recv(4096)
                self.buffer += line
                self.parse_messages()
                if self.messages:
                    self.handle_messages()
            except socket.error:
                pass
            except Exception as e:
                print(e)
                self.terminate_flag.set()
        print("strange")

    def __repr__(self):
        return f"Connection to {self.address[0]}:{self.address[1]}"