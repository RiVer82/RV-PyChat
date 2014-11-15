__author__ = 'Rik Verbeek'

#!/usr/bin/env python
# Encoding		: utf-8
# File			: RVChatClient.py
# Version		: 0.0
# Author		: Rik Verbeek

from threading import Thread
import socket
import hashlib
from river.basics.commandline.ShowInfo import ShowInfo
from river.basics.interpreter.interpreter import Interpreter


class RVChatClient(ShowInfo, Interpreter):
    cont = True
    s = None
    h = None
    hn = ""
    rt = None
    disconnecting = False

    Age = None
    Nickname = None

    def __init__(self):
        #self.show("Initing")
        self.s = None
        self.addcommand('connect', self.conn)
        self.addcommand('discon', self.disconn)
        self.addcommand('nick', self.nick)
        self.addcommand('msg', self.msg)
        self.addcommand('info', self.inf)
        self.addcommand('st', self.st)
        self.addcommand('exit', self.ex)
        self.addcommand('loop', self.loop)
        self.addcommand('age', self.age)

    def commandline(self):
        #if self.Nickname is None:
        #    self.Nickname = input("Enter NickName: ")

        while self.cont:
            if not self.Nickname:
                inp = input("[<nameless>" + self.hn + "] ")
            else:
                inp = input("[" + self.Nickname + self.hn + "] ")
            self.interpret(inp)

#    def interpret(self, commline):
#        com = commline.split(' ')
#        co = com[0]
#        l = len(com[0])+1
#        if not co.strip():
#            pass
#        elif not co in self._commands:
#            self.error("Unknown command: " + co)
#        else:
#            f = self._commands[co]
#            f(self, commline[l:])

    def connect(self, ip, port):
        if self.s is None:
            # Create an INET (?), STREAMing socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # If already connected no need to reconnect
        if not self.isconnected():
            try:
                # Now connect to the server
                self.s.connect((ip, port))
                self.hn = ("@%s:%s" % (self.s.getpeername()[0], str(self.s.getpeername()[1])))

                self.disconnecting = False
                self.rt = Thread(group=None, target=self.receivethread, name=None, args=())
                self.rt.start()
                self.info("Thread started: " + self.rt.name)

            except socket.error as msg:
                self.error("Connecting failed, error code: " + str(msg[0]) + " Message: " + msg[1])
                self.s.close()
        else:
            self.error("Already connected!")

    def disconnect(self):
        self.info("Disconnecting")

        if not self.s is None:
            self.disconnecting = True
            self.s.close()
            self.s = None
            self.hn = ""

    def receivethread(self):
        # Thread for receiving data from server.

        while not self.disconnecting:
            # Receiving from client
            try:
                data = self.s.recv(1024)
                if self.disconnecting or not data:
                    break
                self.show(" ")
                self.info("Data received: " + str(data, 'UTF-8'))
                self.show(" ")

            except socket.error as msg:
                self.error("Could not read socket. Socket closed?")
                self.disconnect()

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

    ## Server commands START
    def sendnick(self, nickname, raiseerror):
        if self.isconnected() and nickname:
            self.send("NICK %s" % nickname)
        elif raiseerror and not self.isconnected():
            self.error("Trying to send Nickname when not connected")
        elif raiseerror and not nickname:
            self.error("Nickname is empty")

    def sendage(self, age, raiseerror):
        if self.isconnected() and age:
            self.send("AGE %s" % age)
        elif raiseerror and not self.isconnected():
            self.error("Trying to send Age when not connected")
        elif raiseerror and not age:
            self.error("Age is empty")

    def sendmessage(self, message):
        if self.isconnected():
            self.send("MSG %s" % message)
        else:
            self.error("Trying to send message when not connected")

    def sendprivatemessage(self, client, message):
        if self.isconnected():
            self.send("PRIV %s %s" % (client, message))
        else:
            self.error("Trying to send message when not connected")
    ## Server commands END

    ## Interpreted commands START
    def msg(self, command):
        if self.isconnected():
            self.send(command)
        else:
            self.warning("Not connected! Please connect before sending a message.")

    def inf(self, command):
        # Show info about the current business
        self.info("Current info:")
        if not self.Nickname is None:
            self.info("Nickname: %s" % self.Nickname)

        if not self.Age is None:
            self.info("Age: %s" % self.Age)

        if self.isconnected():
            self.info("Connection to: %s Port: %s" % (str(self.s.getpeername()[0]), str(self.s.getpeername()[1])))

    def conn(self, command):
        com = command.split(' ')

        if len(com) >= 2:
            self.info("Trying to connect Ip: " + com[0] + " Port: " + com[1])
            self.connect(com[0], int(com[1]))
        else:
            self.warning("Usage con command: con <IP-Address> <port>")

        self.sendnick(self.Nickname, False)
        self.sendage(self.Age, False)

    def disconn(self, command):
        self.disconnect()

    def nick(self, command):
        com = command.split(' ')
        if len(com) >= 1:
            self.Nickname = command
            self.info("Nickname changed: %s" % command)
            if self.isconnected():
                self.send("NICK %s" % self.Nickname)
        else:
            self.warning(" Usage nick command: nick <Desired nickname>")

    def age(self, command):
        if not command:
            self.warning(" Usage age command: age <Actual age>")
        else:
            self.Age = command
            self.info("Age changed: %s" % command)
            if self.isconnected():
                self.send("AGE %s" % self.Age)

    def msg(self, command):
        if command:
            self.sendmessage(command)

    def priv(self, command):
        com = command.split(' ')
        if len(com) >= 2:
            client = com[0]
            message = command[len(client):]
            self.sendprivatemessage(client, message)
        else:
            self.warning("Usage priv command: priv <client> <message>")

    def st(self, command):
        self.conn("localhost 8889")

    def ex(self, command):
        if not self.s is None:
            self.disconnect()
        self.info("Exit!")
        self.cont = False
        exit()

    def loop(self, command):
        com = command.split(' ')
        d = ""
        if len(com) >= 2:
            self.info("Looping #: " + str(com[0]) + " Data: " + str(com[1]))
            for x in range(0, int(com[0])):
                d += str(com[1])
            self.send(d)

        else:
            self.warning(" Usage loop command: loop <no of loops> <data>")

    ## Interpreted commands END

    def unknowncommand(self, command):
        self.error("Unkown command: %s" % command)