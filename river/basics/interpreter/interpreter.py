__author__ = 'Rik Verbeek'

from river.basics.commandline.ShowInfo import ShowInfo

#class Interpreter(ShowInfo):
class Interpreter():


    _commands = {}

    def interpret(self, commline):
        #print("        Interpreting line: " + commline)
        com = commline.split(' ')
        co = com[0]
        l = len(com[0])+1
        #print("        Command: " + co)
        #print("        Rest of command: " + commline[l:])
        if not co.strip():
            pass
        elif not co in self._commands:
            self.unknowncommand(co)
            #self.error("Unknown command: " + co)
            # ignore command, no command given
        else:
            f = self._commands[co]
            f(commline[l:])
            #f(self, commline[l:])

#    def interpret(self, commandline):
#        print("Interpreting: " + str(commandline))

    def addcommand(self, command, functionname):
        if not self.hascommand(command):
            self._commands[command] = functionname
            #self.info("Added %s command to function %s" % (command, functionname))
        else:
            pass
           # self.error("Already has command %s" % command)

    def removecommand(self, command):
        if self.hascommand(command):
            del(self._commands[command])
            #self.info("Removed %s command" % (command))
        else:
            pass
            #self.info("No such command %s" % command)

    def hascommand(self, command):
        return command in self._commands

    def unknowncommand(self, command):
        raise NotImplementedError("Function unknowncommand not implemented")
