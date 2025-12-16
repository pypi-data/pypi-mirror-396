# TODO: not super sure yet how many session structs we need
#       should there be one for 0.7 too? One for ddnet too?
#       or just version fields?
class Session7:
    def __init__(self):
        self.client_token = b'\xff\xff\xff\xff'
        self.server_token = b'\xff\xff\xff\xff'

        # The amount of vital chunks received
        self.ack = 0

        # The amount of vital chunks sent
        self.sequence = 0

        # The amount of vital chunks acknowledged by the peer
        self.peer_ack = 0
