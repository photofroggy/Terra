
import os
import sys
import time
from threading import Thread
from threading import BoundedSemaphore

class Logger(Thread):
    
    def __init__(self, dAmn, logging=True, debug=False):
        super(Logger, self).__init__()
        self.dAmn = dAmn
        self.logging = logging
        self.mute_channels = []
        self.debug = debug
        self.running = False
        self._run = False
        # Create locks
        self.qlock = BoundedSemaphore()
        #self.mlock = BoundedSemaphore()
        self.llock = BoundedSemaphore()
        # Create queues
        self.wqueue = [] # Output queue
        #self.mqueue = [] # Muter queue
        self.lqueue = [] # Logger queue. Just in case.
        # Just in case.
        self.subbing = False
        self.subthread = None
    
    def run(self):
        self.running = True
        self._run = True
        while self._run:
            # Muter processing
            #self.mlock.acquire()
            #if len(self.mqueue) != 0:
            #    self.flush_muters()
            #self.mlock.release()
            # Writer processing
            self.qlock.acquire()
            q = self.wqueue
            self.wqueue = []
            self.qlock.release()
            if len(q) != 0:
                self.flush(q)
            time.sleep(.5)
        #self.flush_muters()
        self.qlock.acquire()
        q = self.wqueue
        self.wqueue = []
        self.qlock.release()
        self.flush(q)
        if self.subbing:
            log, self.logging = self.logging, False
            self.writeout(time.time(), '~Global', '** Waiting for logs to finish writing...', False)
            while self.subbing:
                time.sleep(.4)
        self.running = False
    
    def stop(self):
        self._run = False
    
    def write(self, ts, ns, msg, showns=True, mute=False, pkt=None):
        if not showns and ns != '~Global' and self.dAmn.format_ns(ns) in self.dAmn.channel.keys():
            if msg.startswith('** Got'):
                if self.dAmn.channel[self.dAmn.format_ns(ns)].member == {}:
                    mute = True
        if not self.running:
            self.writeout(ts, ns, msg, showns, mute, pkt)
            return
        self.qlock.acquire()
        self.wqueue.append((ts, ns, msg, showns, mute, pkt))
        self.qlock.release()
    
    def flush(self, queue):
        if len(queue) > 60:
            self.writeout(time.time(), '~Global',
                '>> Received a ridiculous amount of data!', False)
            self.writeout(time.time(), '~Global',
                '>> Skipping all data in the queue.', False)
            if not self.logging:
                return
            self.writeout(time.time(), '~Global',
                '>> This data will still appear in the logs.', False)
            self.start_threaded_flush(queue)
        while len(queue) != 0:
            tups = queue.pop(0)
            self.writeout(*tups)
    
    def start_threaded_flush(self, queue):
        self.lqueue = queue
        self.subbing = True
        self.subthread = Thread(target=self.threaded_flush)
        self.subthread.start()
    
    def threaded_flush(self):
        while True:
            self.llock.acquire()
            q, self.lqueue = self.lqueue[:50], self.lqueue[50:]
            self.llock.release()
            for item in q:
                self.save_log(*item)
            self.llock.acquire()
            waiting = len(self.lqueue)
            self.llock.release()
            if waiting == 0:
                self.subbing = False
                return
            time.sleep(.8)
    
    def writeout(self, ts, ns, msg, showns=True, mute=False, pkt=None):
        if self.logging:
            self.save_msg(ts, ns, msg, showns, mute, pkt)
        self.pnt_message(ts, ns, '{0} {1}'.format(('{0}|'.format(ns) if showns else ''), msg), showns, mute, pkt)
        
    def pnt_message(self, ts, ns, message, showns=True, mute=False, pkt=None):
        try:
            if (mute or ns.lower() in self.dAmn.mute_channels) and not self.debug:
                return
            sys.stdout.write('{0}{1}\n'.format(self.clock(ts), message))
            if self.debug:
                self.save_msg(ts, '~Debug', message, showns, mute, pkt)
        except UnicodeError:
            sys.stdout.write('{0} >> Received an unprintable message!\n'.format(self.clock(ts)))
        sys.stdout.flush()
        
    def clock(self, ts):
        return '{0}|'.format(time.strftime('%H:%M:%S', time.localtime(ts)))
        
    def save_msg(self, ts, ns, msg, showns=True, mute=False, pkt=None):
        if not self.subbing:
            self.save_log(ts, ns, msg, showns, mute, pkt)
            return
        self.llock.acquire()
        self.lqueue.append((ts, ns, msg, showns, mute, pkt))
        self.llock.release()
        
    def save_log(self, ts, ns, msg, showns=True, mute=False, pkt=None):
        if not os.path.exists('./storage'): os.mkdir('./storage', 0o755)
        if not os.path.exists('./storage/logs'): os.mkdir('./storage/logs', 0o755)
        if not os.path.exists('./storage/logs/' + ns): os.mkdir('./storage/logs/' + ns, 0o755)
        file = open('./storage/logs/{0}/{1}.txt'.format(ns,
            time.strftime('%Y-%m-%d', time.localtime(ts))), 'a')
        try:
            file.write('{0} {1}{2}'.format(self.clock(ts), msg.lstrip(), "\n"))
        except UnicodeEncodeError:
            file.write('{0} >> Unprintable message received in {1}!\n'.format(self.clock(ts), ns))
        file.close()

# EOF
