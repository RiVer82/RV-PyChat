from river.tryout.networing.RVServer import RVClientConnection

__author__ = 'Rik Verbeek'

#!/usr/bin/env python
# Encoding		: utf-8
# File			: dummyserver.py
# Version		: 0.0
# Author		: Rik Verbeek


'''
    Simple socket server using threads, returns the SHA224
	hash of incoming string then closes the connection
'''

import socket
import sys
from threading import *
from river.basics.commandline.ShowInfo import ShowInfo
from river.basics.interpreter.interpreter import Interpreter
from river.tryout.networing.RVServer.RVClientConnection import RVClientConnection



class RVServer(Interpreter, ShowInfo):
    cont = True
    st = None
    hn = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    comlinethread = None
    connections = {}
    cnos = 0

    def __init__(self):
        self.info("Initing server")
        self.cont = True
        self.addcommand("nodes", self.nodes)
        self.addcommand("exit", self.exit)
        self.addcommand("stop", self.stop)
        self.addcommand("closeall", self.closeall)
        self.addcommand("close", self.close)

    def start(self, host, port):
        self.info("Starting server")
        try:
            #self.ss = socketserver.TCPServer
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((host, port))

            self.info("Bound at: " + str(host) + " port: " + str(port) + " and listening")
        except socket.error as msg:
            self.error("Binding socket failed. Error code: " + str(msg[0]) + " Message: " + msg[1])
            sys.exit()

        self.s.listen(5)

        self.hn = ("%s:%s" % (self.s.getsockname()[0], str(self.s.getsockname()[1])))
        self.comlinethread = Thread(group=None, target=self.commandline, name='CommandLine', args=())
        self.comlinethread.start()

        while self.cont:
            #wait to accept a connection - blocking call
            self.info("Trying to accept a connection")
            rvcc = None
            conn = None
            addr = None

            try:
                conn, addr = self.s.accept()
                self.cnos += 1
            except socket.error as msg:
                self.error("Error while accepting connections. Shutting down server?")
                self.cont = False
                break

            self.info("#%s Connected with: %s:%s" % (self.cnos, addr[0], str(addr[1])))

            # Start new thread takes 1st argument as a function name to be run,
            # second is the tuple of arguments to the function.
            rvcc = RVClientConnection(conn, self, self.cnos)
            #rvcc.start()

            Thread(group=None, target=rvcc.start, name=None, args=(conn, self, self.cnos, )).start()
            self.connections[self.cnos] = rvcc

            self.info("Created new thread")
            self.info("")

        self.info("Server done, closing connection!")
        self.s.close()

    def commandline(self):
        while self.cont:
            inp = input("[%s] " % self.hn)
            self.interpret(inp)

    def removeclient(self, client, number):
        if number in self.connections:
        #if client in self.connections:
            del(self.connections[number])
            #self.connections.remove(client)
        else:
            self.error("Tried to remove non-existing client: %s" % client)

    def messageclients(self, origin, message):
        for n in self.connections:
            if not self.connections[n].connumber == origin:
                self.connections[n].send("%s says: '%s'" % (origin, message))

    ## Interpreted commands START

    def nodes(self, command):
        if len(self.connections) == 0:
            self.info("No connections to other nodes")
        else:
            self.info("Current nodes:")
            for n in self.connections:
                self.info("  Node %s" % self.connections[n])

    def exit(self, command):
        self.info("Exiting!")
        self.cont = False
        self.closeall(command)
        self.s.close()
        sys.exit()

    def closeall(self, command):
        k = self.connections.keys()
        for key in k:
            self.connections[key].disconnect()

#        for clnt in self.connections:
#            #clnt.disconnect()
#            try:
#                self.lock.acquire()
#                self.connections[clnt].disconnect()
#            finally:
#                self.lock.release()

    def stop(self):
        self.info("Stopping server!")

    def close(self, command):
        com = command.strip().split(' ')
        #self.debug("Keys in connections: %s" % self.connections.keys())
        #self.debug("close command: %s length: %s" % (com, len(com)))
        if len(com) >= 1:
            for n1 in com:
                n2 = 0
                try:
                    n2 = int(n1)
                except:
                    # self.debug("Ignore failed casting")
                    n2 = 0
                #self.debug("Closing: %s" % n1)
                if n2 in self.connections.keys():
                    self.connections[n2].disconnect()
                else:
                    self.warning("Node unkown: %s" % n1)
        else:
            self.warning("Usage close command: close <node nummer>")

    ## Interpreted commands END

    def unknowncommand(self, command):
        self.error("Unkown command: %s" % command)