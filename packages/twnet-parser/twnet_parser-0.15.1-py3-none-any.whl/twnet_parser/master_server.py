from typing import Literal

class MastersrvAddr():
    def __init__(
            self,
            family: Literal[4, 6] = 4,
            ipaddr: str = '127.0.0.1',
            port: int = 8303
        ) -> None:
        self.family: Literal[4, 6] = family
        self.ipaddr: str = ipaddr
        self.port: int = port

