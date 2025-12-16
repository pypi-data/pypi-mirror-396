from typing import Dict, Optional
from twnet_parser.snapshot import Snapshot

class Holder:
    def __init__(self, tick: int, snapshot: Snapshot):
        self.snapshot: Snapshot = snapshot
        self.tick: int = tick

class SnapshotStorage:
    # passed to methods
    EMPTY_SNAP_TICK = -1

    # returned by methods
    UNINITIALIZED_TICK = -1

    def __init__(self) -> None:
        self.holder: Dict[int, Holder] = {}

        # oldest tick still in the holder
        # not the oldest tick we ever received
        self.oldest_tick = self.UNINITIALIZED_TICK

        # newest tick in the holder
        self.newest_tick = self.UNINITIALIZED_TICK

        # the tick we are currently collecting parts for
        self.current_recv_tick: int = 0

        # received parts for the current tick
        # as a bit field
        # to check if we received all previous parts
        # when we get the last part number
        self.snapshot_parts: int = 0

        self.__multi_incoming_data: bytes

    def next_tick(self, tick: int) -> int:
        for k in sorted(list(self.holder.keys())):
            if k > tick:
                return k
        return self.UNINITIALIZED_TICK

    def previous_tick(self, tick: int) -> int:
        for k in reversed(sorted(list(self.holder.keys()))):
            if k < tick:
                return k
        return self.UNINITIALIZED_TICK

    def purge_until(self, tick: int) -> None:
        for k in list(self.holder.keys()):
            if k < tick:
                del self.holder[k]

        if self.oldest_tick != self.UNINITIALIZED_TICK:
            found = self.oldest_tick in self.holder
            if not found:
                self.oldest_tick = self.next_tick(self.oldest_tick)

        if self.newest_tick != self.UNINITIALIZED_TICK:
            found = self.oldest_tick in self.holder
            if not found:
                self.newest_tick = self.next_tick(self.newest_tick)

    def add_incoming_data(self, part: int, num_parts: int, data: bytes) -> None:
        if part == 0:
            # reset length if we get a new snapshot
            self.__multi_incoming_data = b''

        if part != num_parts - 1:
            if len(data) != Snapshot.MAX_PACK_SIZE:
                raise ValueError( \
                                 "Error: incomplete part that is not the last expected part:" \
                                 f"part={part} num_parts={num_parts} " \
                                 f"expected_size={Snapshot.MAX_PACK_SIZE} got_size={len(data)}")
        if len(self.__multi_incoming_data) + len(data) > Snapshot.MAX_SIZE:
            raise ValueError("Error: " \
                f"reached the maximum amount of snapshot data: {Snapshot.MAX_SIZE}")

        self.__multi_incoming_data += data

    def incoming_data(self) -> bytes:
        return self.__multi_incoming_data

    def get(self, tick: int) -> Optional[Snapshot]:
        if tick == self.EMPTY_SNAP_TICK:
            # TODO: can we return an empty snap here?
            #       not really because we do not know if 0.7 or 0.6
            return None
        if tick < 0:
            raise ValueError(f"Error: negative ticks not supported! Tried to get tick {tick}")
        if tick not in self.holder:
            return None

        return self.holder[tick].snapshot

    def add(self, tick: int, snapshot: Snapshot) -> None:
        if tick < 0:
            raise ValueError(f"Error: negative ticks not supported! Tried to add tick {tick}")
        new_snap_id = id(snapshot)
        for holder in list(self.holder.values()):
            if id(holder.snapshot) == new_snap_id:
                raise ValueError(
                    f"Error: snapshot with object id {new_snap_id} already in the storage." \
                        "Use copy.deepcopy() to avoid bugs.")

        if self.oldest_tick == self.UNINITIALIZED_TICK or tick < self.oldest_tick:
            self.oldest_tick = tick
        if self.newest_tick == self.UNINITIALIZED_TICK or tick > self.newest_tick:
            self.newest_tick = tick
        self.holder[tick] = Holder(tick, snapshot)
