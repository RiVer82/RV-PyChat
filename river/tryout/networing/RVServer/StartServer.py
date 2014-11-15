__author__ = 'Rik Verbeek'

import RVServer
import river.tryout.networing.RVServer

HOST = 'localhost'  # Symbolic name meaning all available interfaces
PORT = 8889  # Arbitrary non-privileged port

rvs = RVServer.RVServer()
#rvs = RVServer()
#print("     Starting server:")
rvs.start(HOST, PORT)
#print("     Server started!")

