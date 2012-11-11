import threading

def start_server_stack(server_stack):
    for server in server_stack:
        def server_thread():
            server.run()

        t = threading.Thread(target = server_thread)
        t.start()

def shutdown_server_stack(server_stack):
    for server in reversed(server_stack):
        server.shutdown()
