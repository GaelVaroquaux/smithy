
import hashlib
import logging
import shelve
import uuid

from path import path

log = logging.getLogger(__name__)

class Engine(object):
    def __init__(self):
        self.waiting = {}
        self.signatures = shelve.open(".belt-sigs")

    def add_job(self, job):
        self.waiting[job.id] = job

    def next_job(self):
        ret = None
        for job in self.waiting.itervalues():
            if job.runnable() and job.should_run():
                ret = job
                break
        if ret is None:
            raise ValueError("No jobs are ready to be run.")
        self.waiting.pop(ret.id)
        return ret
    
    def run(self):
        while len(self.waiting):
            job = self.next_job()
            log.info("Running: %s" % job.name)
            job.run()

engine = Engine()