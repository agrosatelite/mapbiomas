# -*- coding: utf-8 -*-

import datetime
import os
import sys
import time
from threading import Thread

import ee

from rsgee.conf import settings
from rsgee.db.models import Task, TaskLog


class TaskManager(Thread):
    def __init__(self, export_class, type, session, max_tasks, interval, max_errors):
        Thread.__init__(self)

        self.__max_tasks = max_tasks
        self.__interval = interval
        self.__export_class = export_class
        self.__type = type
        self.__session = session
        self.__max_errors = max_errors

        self.__tasks_awaiting = {}
        self.__tasks_running = {}
        self.__tasks_completed = {}
        self.__tasks_error = {}
        self.__tasks_failed = {}

    def run(self):
        def process_tasks(tasks):
            while len(tasks) > 0 or len(self.__tasks_running) > 0:
                try:
                    self.__print()
                    self.__submit_task(tasks)
                    self.update_tasks()
                except Exception as e:
                    print "Exception: {0}".format(e)
                time.sleep(self.__interval)

        process_tasks(self.__tasks_awaiting)
        print "Finished!!!"
        sys.exit(0)

    def get_export_class(self):
        return self.__export_class

    def add_task(self, code, specifications):
        task = self.get_task(code)
        if not task:
            task = Task(code=code, model=settings.FEATURE_WRS, type=self.__type, specifications=ee.serializer.toJSON(specifications),
                        state=ee.batch.Task.State.UNSUBMITTED)
            self.__session.add(task)
            self.__session.commit()

            task_log = TaskLog(task=task.id, state=ee.batch.Task.State.UNSUBMITTED, date=datetime.datetime.now())
            self.__session.add(task_log)
            self.__session.commit()
        if task and not task.state in [ee.batch.Task.State.COMPLETED, ee.batch.Task.State.CANCELLED]:
            self.__tasks_awaiting[code] = True
        else:
            print "Task {0} exists!".format(code)

    def get_task(self, code):
        task = self.__session.query(Task).filter_by(code=code).first()
        return task

    def update_tasks(self):
        for code, t in self.__tasks_running.copy().items():
            task = self.get_task(code)

            remote_state = t.status()['state']
            remote_info = None

            if remote_state == ee.batch.Task.State.UNSUBMITTED:
                try:
                    t.start()
                    remote_state = ee.batch.Task.State.READY
                    pass
                except Exception as e:
                    print e
                    del self.__tasks_running[code]
                    remote_info = t.status()['error_message']
                    remote_state = ee.batch.Task.State.FAILED

                    self.__tasks_error[code] = self.__tasks_error[code] + 1 if self.__tasks_error.has_key(code) else 0
                    if self.__tasks_error[code] <= self.__max_errors:
                        self.__tasks_failed[code] = True

            elif remote_state == ee.batch.Task.State.RUNNING and task.state == ee.batch.Task.State.READY:
                task.start_date = datetime.datetime.now()

            elif remote_state == ee.batch.Task.State.COMPLETED:
                task.end_date = datetime.datetime.now()
                del self.__tasks_running[task.code]
                self.__tasks_completed[task.code] = True

            elif remote_state in [ee.batch.Task.State.CANCELLED, ee.batch.Task.State.CANCEL_REQUESTED]:
                del self.__tasks_running[task.code]

            elif remote_state == ee.batch.Task.State.FAILED:
                remote_info = t.status()['error_message']

                if remote_info.find("No valid training data were found") != -1 or remote_info.find("Internal error") != -1:
                    remote_state = ee.batch.Task.State.CANCELLED
                    self.__tasks_failed[code] = True
                    del self.__tasks_running[task.code]
                else:
                    self.__tasks_error[code] = self.__tasks_error[code] + 1 if self.__tasks_error.has_key(code) else 1

                    if self.__tasks_error[code] <= self.__max_errors:
                        remote_state = ee.batch.Task.State.UNSUBMITTED
                        self.__tasks_running[code] = self.__generate_task(code)
                    else:
                        self.__tasks_failed[code] = True
                        del self.__tasks_running[code]

            if task.state != remote_state:
                task.state = remote_state
                self.__session.add(TaskLog(task=task.id, state=remote_state, date=datetime.datetime.now(), info=remote_info))

            self.__session.commit()

    def __print(self):
        os.system('clear')
        print "************************* Tasks *************************"
        print "Awaiting:    {0} tasks".format(len(self.__tasks_awaiting))
        print "Running:     {0} tasks".format(len(self.__tasks_running))
        print "Completed:   {0} tasks".format(len(self.__tasks_completed))
        print "Error:       {0} tasks".format(len(self.__tasks_error))
        print "Failed:      {0} tasks".format(len(self.__tasks_failed))
        print "*********************************************************"
        for code, task in self.__tasks_running.items():
            print code, "|", task.status()['state']

    def __generate_task(self, code):
        task = self.get_task(code)
        if task:
            specifications = ee.deserializer.fromJSON(task.specifications)
        else:
            raise AttributeError("Task not found")
        return self.__export_class(**specifications)

    def __submit_task(self, tasks):
        for code in sorted(tasks.copy().keys()):
            if code in self.__tasks_failed.keys():
                del tasks[code]
                continue
            if len(self.__tasks_running) >= self.__max_tasks or len(tasks) == 0:
                break
            task = self.get_task(code)
            if task.state in [ee.batch.Task.State.COMPLETED, ee.batch.Task.State.CANCELLED]:
                del tasks[code]
            if task.state in [ee.batch.Task.State.UNSUBMITTED, ee.batch.Task.State.FAILED]:
                self.__tasks_running[code] = self.__generate_task(code)
                del tasks[code]
            if task.state in [ee.batch.Task.State.READY, ee.batch.Task.State.RUNNING]:
                print "{0} running in other process".format(code)
                # del tasks[code]
