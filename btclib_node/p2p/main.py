from btclib_node.p2p.callbacks import callbacks


def handle_p2p(node):
    msg_type, msg, conn_id = node.p2p_manager.messages.popleft()
    if msg_type in callbacks:
        try:
            conn = node.p2p_manager.connections[conn_id]
            callbacks[msg_type](node, msg, conn)
        except Exception as e:
            print(e)
            pass