import threading

class ThreadBaseMixIn:
    threads = None
    def start_thread(self, **kwargs):
        if self.threads == None: self.threads = list()

        t = threading.Thread(target = kwargs['target'])
        t.setDaemon(True)
        t.start()
        self.threads.append(t)
