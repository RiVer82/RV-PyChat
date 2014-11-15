__author__ = 'Rik Verbeek'

#!/usr/bin/env python
# Encoding		: utf-8
# File			: dummyserver.py
# Version		: 0.0
# Author		: Rik Verbeek



import socket
import sys
import hashlib
from threading import *
from river.basics.commandline.ShowInfo import ShowInfo
from river.basics.interpreter.interpreter import Interpreter

class RVClientConnection(ShowInfo, Interpreter):
    cont = True
    rvserver = None
    s = None
    connumber = 0
    #lock = None
    connected = True

    Age = None
    Nickname = None

    def __init__(self, conn, rvserver, cons):
        self.info("Initing client connection")
        #Thread.__init__(self)
        self.rvserver = rvserver
        self.s = conn
        self.connumber = cons
        self.addcommand("NICK", self.nick)
        self.addcommand("AGE", self.age)
        self.addcommand("MSG", self.msg)

    def __str__(self):
        return "#: %s IP: %s Port: %s Connected: %s Name: %s Age: %s" % (
                                self.connumber, self.s.getpeername()[0], self.s.getpeername()[1],
                                self.connected, self.Nickname, self.Age)

    def start(self, conn, rvserver, number):
#    def run(self):
        self.info("Starting client connection")

        #self.lock = lock
        #Sending message to connected client

        # Loop until end of connection detected. Then let the loop stop.
        while self.cont:
            #Receiving from client
            try:
                #data = conn.recv(1024)  # Blocking call
                data = self.s.recv(1024)  # Blocking call
                if not data:
                    self.cont = False
                    self.disconnect()
                    break
            except socket.error as msg:
                self.error("[%s] Socket receive error, probably connection closed." % self.connumber)
                self.disconnect()

            if self.cont:
                self.info("Data received: " + str(data, 'UTF-8'))
                self.interpret(str(data, 'UTF-8'))
                #hs = hashlib.sha224(bytes(data)).hexdigest()
                #self.info("HS1: " + hs)
                #self.info("Length: " + str(len(data)))
                #conn.send(bytes(str(hs), 'UTF-8'))

        #came out of loop
        self.info("[%s] Closing connection, thread ending " % self.connumber)

    def disconnect(self):
        self.info("Disconnecting client %s" % self)
        self.cont = False
        self.connected = False

        if not self.s is None:
           self.send("DISCONNECT")
           self.rvserver.removeclient(self, self.connumber)

    def send(self, data):
        if not self.s is None and not data is None:
            try:
                sent = self.s.send(bytes(data, 'UTF-8'))
                if sent == 0:
                    raise RuntimeError("	Socket broken")
            except socket.error as msg:
                self.error("Could not send message")
                self.s.close()
                self.s = None

            self.info("Data sent: " + str(data))
            self.info("Length: " + str(sent))
            return hashlib.sha224(bytes(data, 'UTF-8')).hexdigest()

    def isconnected(self):
        c = False
        if not self.s is None:
            try:
                peername = self.s.getpeername()
                c = True
            except:
                self.warning("Is connected had an exception")

        return c

    ## Interpreted commands START
    def nick(self, command):
        if not command:
            self.error("[%s] Empty nickname given, ignoring command" % self.connumber)
        else:
            self.Nickname = command
            self.info("[%s] Nickname changed: %s" % (self.connumber, command))
            self.send("NICK OK")

    def age(self, command):
        if not command:
            self.error("[%s] Empty age given, ignoring command" % self.connumber)
        else:
            self.Age = command
            self.info("[%s] Age changed: %s" % (self.connumber, command))

    def msg(self, command):
        if not command:
            self.info("")
            self.error("[%s] Empty message send, ignoring msg command" % self.connumber)
            self.info("")
        else:
            self.rvserver.messageclients(self.connumber, command)

    ## Interpreted commands END

    ## Inherited functions START
    def unknowncommand(self, command):
        self.error("Unkown command: %s" % command)

    ## Inherited functions START
