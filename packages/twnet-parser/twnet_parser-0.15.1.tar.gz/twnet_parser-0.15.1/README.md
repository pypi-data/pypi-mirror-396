A teeworlds network protocol library, designed according to sans I/O (http://sans-io.readthedocs.io/) principles

# THIS LIBRARY IS IN EARLY DEVELOPMENT

## Do not get bamboozled by the mature looking readme!
## This project is not in a very usable state yet. It is in very early development!
## APIs might change and many essential features are missing!

---

## install

```bash
pip install twnet_parser
```

## sample usage

```python
import twnet_parser.packet
packet = twnet_parser.packet.parse7(b'\x04\x0a\x00\xcf\x2e\xde\x1d\x04') # 0.7 close

print(packet) # => <class: 'TwPacket7'>: {'version': '0.7', 'header': <class: 'Header'>, 'messages': [<class: 'CtrlMessage'>]}
print(packet.header) # => <class: 'Header'>: {'flags': <class: 'PacketFlags7, 'size': 0, 'ack': 10, 'token': b'\xcf.\xde\x1d', 'num_chunks': 0}
print(packet.header.flags) # => <class: 'PacketFlags7'>: {'control': True, 'resend': False, 'compression': False, 'connless': False}
for msg in packet.messages:
    print(msg.message_name) # => close

print(packet.to_json())
# {
#   "version": "0.7",
#   "payload_raw": "04",
#   "payload_decompressed": "04",
#   "header": {
#     "flags": [
#       "control"
#     ],
#     "ack": 10,
#     "token": "cf2ede1d",
#     "num_chunks": 0
#   },
#   "messages": [
#     {
#       "message_type": "control",
#       "message_name": "close",
#       "message_id": 4,
#       "reason": null
#     }
#   ]
# }
```

More examples can be found in the [examples/](./examples/) folder:
### 0.7

- [map downloader client](./examples/07/download_map/)
- [flood client (connect multiple tees to a server)](./examples/07/flood/)

### 0.6 and 0.7

- [pcap printer (capture with tcpdump and print teeworlds traffic details)](./examples/06_and_07/print_pcap_files/)

## Features

| Feature                      | 0.6.4              | 0.6.5              | 0.7.0 - 0.7.5      |
| ---------------------------- | ------------------ | ------------------ | ------------------ |
| Deserialize packet headers   |                    | :heavy_check_mark: | :heavy_check_mark: |
| Deserialize chunk headers    | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Deserialize messages         | 90%                | 90%                | 90%                |
| Deserialize snapshots        |                    |                    |                    |
| Deserialize connless packets | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Serialize packet headers     | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Serialize chunk headers      | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| Serialize messages           | 90%                | 90%                | 90%                |
| Serialize snapshots          |                    |                    |                    |
| Serialize connless packets   |                    | :heavy_check_mark: | :heavy_check_mark: |

## Non-Features (also not planned for this library)

| Feature                        | Status  | Where to find it                            |
| ------------------------------ | ------- | ------------------------------------------- |
| Networking                     | :x:     | TODO: link if someone implemented it on top |
| Protocol version detection     | :x:     | TODO: link if someone implemented it on top |
| Track sequence number state    | :x:     | TODO: link if someone implemented it on top |
| Track connection state         | :x:     | TODO: link if someone implemented it on top |

Look elsewhere for these features. Or use this library to implement them on top.

This project is intentionally only covering parsing the protocol.
Not fully implemeting a state machine of the protocol.
Or a fully working client / server software.

If you want to build something with this library
you do have to understand how the protocol works
and when the client and server have to send what.

This [protocol documentation](https://chillerdragon.github.io/teeworlds-protocol/index.html)
should get you started to understand the basics.

## Convenient defaults and fully customizable

```python
from twnet_parser.packet import TwPacket7
from twnet_parser.messages7.game.cl_call_vote import MsgClCallVote

"""
The call to packet.pack() generates
a valid byte array that can be sent as an udp payload

It uses default values for things like:
 security token, acknowledge number, packet flags,
 chunk header (flags, size, seq),
 vote type, vote value, vote reason, vote force

It computes a valid chunk header size field based
on the payload length.

It sets the correct num chunks field in the packet header
based on the amount of messages you added (1 in this case)

While this has all fields set that packet would be dropped by a vanilla
implementation because the security token and sequence number is wrong.
So you have to take care of those your self.
"""
packet = TwPacket7()
msg = MsgClCallVote()
packet.messages.append(msg)
packet.pack() # => b'\x00\x00\x01\xff\xff\xff\xff\x00\x00\x80\x01default\x00default\x00default\x00\x00'



"""
Here we also send a Call vote message.
But this time we set a security token and a few other fields.

Note that we set num_chunks to 6 which is wrong because
we only send one message (MsgClCallVote).
But this library allows you to do so.
And it will not compute the correct amount.
But use your explicitly set wrong one instead.

This allows you to have full control and craft any kind of packet.
May it be correct or not.
"""
packet = TwPacket7()
packet.header.token = b'\x48\x1f\x93\xd7'
packet.header.num_chunks = 6
packet.header.ack = 638
packet.header.flags.control = False
packet.header.flags.compression = False
msg = MsgClCallVote()
msg.header.seq = 10
msg.type = 'option'
msg.value = 'test'
msg.reason = ''
msg.force = False
packet.messages.append(msg)
packet.pack() # => b'\x02~\x06H\x1f\x93\xd7\x00\x00\x80\x01option\x00test\x00\x00\x00'
```

## Zero dependencies by default

Running ``pip install twnet_parser`` will not install any additional packages.

But there is an optional dependency for huffman compression.
By default twnet_parser is using the huffman compression code from the [huffman-py](https://github.com/ChillerDragon/huffman-py)
project which is written in pure python.
If you have [libtw2-huffman](https://pypi.org/project/libtw2-huffman/) installed it will use that one instead.
Because it is faster since it is written in rust and has better error handling.
But since it is so much overhead it is not installed by default to keep twnet_parser light weight.


You can install it by running ``pip install libtw2-huffman``
or by running ``pip install -r requirements/optional.txt``


You can also check which huffman backend is currently active with these lines of code

```python
import twnet_parser.huffman
print(twnet_parser.huffman.backend_name()) # => rust-libtw2 or python-twnet_parser
```

## development setup

```bash
git clone https://gitlab.com/teeworlds-network/twnet_parser
cd twnet_parser
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
pre-commit install --hook-type commit-msg
```

## tests and linting

```bash
# dev dependencies
pip install -r requirements/dev.txt

# run unit tests
pytest .

# run style linter
pylint src/

# run type checker
mypy src/

# or use the bundle script that runs all tests
./scripts/run_tests.sh
```

## package and release

```bash
# manual
pip install -r requirements/dev.txt
version=0.14.2
sed -i "s/^__version__ =.*/__version__ = '$version'/" twnet_parser/__version__.py
python -m build
git tag -a "v$version" -m "# version $version"
python -m twine upload dist/*

# or use the interactive convience script
./scripts/release.sh
```
