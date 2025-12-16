# return type Snapshot from within Snapshot class
# remove this after switching to python 3.14
from __future__ import annotations

import copy
import json
from typing import Literal, Optional
from twnet_parser import snap_item
import twnet_parser.serialize
from twnet_parser.obj7 import GAME_DATA_RACE, PLAYER_INFO_RACE
from twnet_parser.packer import Unpacker, pack_int
from twnet_parser.snap_item import SnapItem
from twnet_parser.item_matcher.match_snap7 import match_item as match_item7
from twnet_parser.item_matcher.match_snap6 import match_item as match_item6

# TODO: this is horrible
def get_item_payload(item: SnapItem) -> list[int]:
    ints: list[int] = []
    unpacker = Unpacker(item.pack())
    for _ in range(0, item.size):
        ints.append(unpacker.get_int())
    return ints


# TODO: don't undiff items the slowest possible way
#
#	there should be way to do it like the C++ implementation
#	which does no unpacking or repacking before applying the diff
def undiff_item_slow(old_item: SnapItem, diff_item: SnapItem) -> SnapItem:
    if snap_item is None:
        return diff_item

    if old_item.type_id != diff_item.type_id:
        raise ValueError("Error: can not diff items of different type")
    if old_item.size != diff_item.size:
        raise ValueError("Error: can not diff items of different size")

    old_payload = get_item_payload(old_item)
    diff_payload = get_item_payload(diff_item)
    new_payload: bytes = b''

    for i in range(0, old_item.size):
        diff_applied = old_payload[i] + diff_payload[i]
        new_payload += pack_int(diff_applied)

    unpacker = Unpacker(new_payload)
    old_item.unpack(unpacker)
    return old_item

# TODO: move this??
def item_key(item: SnapItem) -> int:
    return (item.type_id << 16) | (item.id & 0xffff)

class Snapshot:
    """
    The snapshot is representing the current state
    of the most gameplay relevant moving things.

    It contains player, projectile and pickup positions.
    And a few more things. It does NOT include any map data.

    Snapshots are always deltas to a previous snapshot.
    The first snapshot is not a delta
    (or a delta to the empty snapshot however you want to see it).

    Snapshots work technically very similar in 0.7 and 0.6
    so this class covers both of them. If you want to understand more
    about snapshots you can read about it here:
    https://chillerdragon.github.io/teeworlds-protocol/07/snap_items.html
    """

    MAX_TYPE: int = 0x7fff
    MAX_ID: int = 0xffff
    MAX_PARTS: int = 64
    MAX_SIZE: int = MAX_PARTS * 1024
    MAX_PACK_SIZE: int = 900

    def __init__(
            self,
            version: Literal['0.6', '0.7'],
            num_removed_items: int = 0,
            num_item_deltas: int = 0
    ) -> None:
        self._version: Literal['0.6', '0.7'] = version
        self.num_removed_items: int = num_removed_items
        self.num_item_deltas: int = num_item_deltas
        self.removed_item_keys: list[int] = []
        self.items: list[SnapItem] = []
        self.crc = 0

    @property
    def version(self) -> Literal['0.6', '0.7']:
        return self._version

    def __iter__(self):
        yield 'num_removed_items', self.num_removed_items
        yield 'num_item_deltas', self.num_item_deltas
        yield 'removed_item_keys', self.removed_item_keys
        yield 'crc', self.crc
        yield 'items', [dict(item) for item in self.items]

    def to_json(self) -> str:
        return json.dumps(
            dict(self),
            indent=2,
            sort_keys=False,
            default=twnet_parser.serialize.bytes_to_hex
        )

    def match_item(self, unpacker: Unpacker) -> Optional[SnapItem]:
        if self.version == '0.7':
            return match_item7(unpacker)
        if self.version[:3] == '0.6':
            return match_item6(unpacker)
        raise ValueError(f'Error: {self.version} snapshots are not implemented yet')

    # expects the int compressed
    # data field of the snap message
    # not the whole snap message with crc
    # and the other fields
    def unpack(self, data: bytes) -> bool:
        unpacker = Unpacker(data)
        self.num_removed_items = unpacker.get_int()
        self.num_item_deltas = unpacker.get_int()
        unpacker.get_int() # unused by tw 0.7 NumTempItems

        self.removed_item_keys = []
        for _ in range(0, self.num_removed_items):
            self.removed_item_keys.append(unpacker.get_int())

        while unpacker.remaining_size() > 2:
            item = self.match_item(unpacker)
            if item is None:
                continue
            item.id = unpacker.get_int()
            item.unpack(unpacker)
            # print(f"got item size={item.size} type={item.type_id}")
            self.items.append(item)

        self.regenerate_crc()
        return True

    def pack(self) -> bytes:
        return b''

    # the key is one integer holding both type and id
    def get_item_at_key(self, key: int) -> Optional[SnapItem]:
        for item in self.items:
            if key == item_key(item):
                return item
        return None

    # the key is one integer holding both type and id
    def get_item_index(self, key: int) -> Optional[int]:
        for index, item in enumerate(self.items):
            if key == item_key(item):
                return index
        return None


    # TODO: this is wasting clock cycles for no reason
    #
    #	the crc is all snap item payload integers summed together
    #	it does not have to be perfectly optimized
    #	but repacking every item to get its payload summed is horrible
    #
    #	i also had another approach with reflect where every snap object would implement
    #	Crc() on them selfs
    #	but reflect is messy and especially the enum types got annoying to sum
    #	because they require specific casting
    def crc_item(self, item: SnapItem) -> int:
        # TODO: remove once crc is confirmed to be working
        # print(f"getting crc from item {item.item_name} that has a size of {item.size}")

        unpacker = Unpacker(item.pack())

        if self.version == '0.7':
            if item.type_id in (GAME_DATA_RACE, PLAYER_INFO_RACE):
                # the backwards compatibility size
                # is not part of the payload
                # and is not used to compute the crc
                unpacker.get_int()
        if item.item_name == 'obj.unknown':
            unpacker.get_int() # pop size

        # TODO: remove once crc is confirmed to be working
        # print(f" unpacker remaining data size {unpacker.remaining_size()}")

        crc = 0
        for _ in range(0, item.size):
            # TODO: remove once crc is confirmed to be working
            # print(f"   unpacker popped field {i} remaining data size {unpacker.remaining_size()}")

            # 32 bit overflow to match the reference implementation
            # not sure how correct this is should probably be double checked
            # i got it from here https://stackoverflow.com/a/16745422
            crc = (unpacker.get_int() + crc) & 0xffffffff
        return crc

    # from has to be the old snapshot we delta against
    # and the unpacker has to point to the payload of the new delta snapshot
    # the payload starts with NumRemovedItems
    #
    # it returns the new full snapshot with the delta applied to the from
    def unpack_delta(self, unpacker: Unpacker) -> Snapshot:
        # TODO: add all the error checking the C++ reference implementation has

        snap = Snapshot(self.version)
        snap.num_removed_items = unpacker.get_int()
        snap.num_item_deltas = unpacker.get_int()
        unpacker.get_int() # _zero

        deleted_keys: list[int] = []

        for _ in range(0, snap.num_removed_items):
            deleted_keys.append(unpacker.get_int())

        for copy_item in self.items:
            keep = True

            for deleted_key in deleted_keys:
                if deleted_key == item_key(copy_item):
                    keep = False
                    break

            if keep:
                snap.items.append(copy.deepcopy(copy_item))

        for _ in range(0, snap.num_item_deltas):
            item: Optional[SnapItem] = copy.deepcopy(self.match_item(unpacker))
            if item is None:
                raise ValueError("Error: failed to unpack snap item")

            item.id = unpacker.get_int()
            # print(f"unpacking item {item.item_name} typeid={item.type_id} i={i} size={item.size}")
            item.unpack(unpacker)

            key = (item.type_id << 16) | (item.id & 0xffff)
            old_item = copy.deepcopy(self.get_item_at_key(key))

            if not old_item:
                snap.items.append(item)
            else:
                item = undiff_item_slow(old_item, item)
                idx = snap.get_item_index(key)
                if idx is None:
                    raise ValueError( \
                            "Error: snap item update failed. " +
                            f"Item with key={key} type_id={item.type_id} id={item.id} not found."
                    )
                snap.items[idx] = item

        if unpacker.remaining_size() > 0:
            raise ValueError("Error:" \
                f"unexpected remaining size {unpacker.remaining_size()} after snapshot unpack")

        snap.regenerate_crc()
        return snap

    def regenerate_crc(self):
        crc = 0
        for item in self.items:
            # 32 bit overflow to match the reference implementation
            # not sure how correct this is should probably be double checked
            # i got it from here https://stackoverflow.com/a/16745422
            crc = (self.crc_item(item) + crc) & 0xffffffff
        self.crc = crc
        return crc
