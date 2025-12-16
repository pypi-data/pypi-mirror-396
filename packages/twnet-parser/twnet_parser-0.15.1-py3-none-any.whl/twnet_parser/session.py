from twnet_parser.constants import NET_MAX_SEQUENCE

def seq_in_backroom(sequence: int, ack: int):
    """
    Only used for chunks where the sequence number does not match the expected value
    to decide whether to drop known chunks silently or request resend if something got lost
    The expected value would be the `(last_ack + 1) % DDNET_MAX_SEQUENCE`

    The argument `sequence` is the sequence number of the incoming chunk

    The argument `ack` is the expected sequence number

    true - if the sequence number is already known and the chunk should be dropped
    false - if the sequence number is off and we need to request a resend of lost chunks
    """
    bottom = ack - (NET_MAX_SEQUENCE / 2)
    if bottom < 0:
        if sequence <= ack:
            return True
        if sequence >= (bottom + NET_MAX_SEQUENCE):
            return True
    elif bottom <= sequence <= ack:
        return True
    return False
