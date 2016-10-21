import json
from twisted.internet import protocol, reactor, endpoints

import singleton

@singleton.Singleton
class POP3Config:
    def __init__(self):
        print 'POP3Config created'
        self._dirr = None
        self._user = "user"
        self._password = "password"

    @property
    def dirr(self):
        return self._dirr

    def set_dirr(self, dirr):
        self._dirr = dirr




class Pop3ServerSideProto(protocol.Protocol):
    END = "\r\n"
    def run_cmd(self, cmd, *args, **kwargs):
        command_handler = getattr(
            self,
            "cmd_"+cmd.upper(),
            lambda *args, **kwargs: "Not implemented"
        )
        return command_handler(self, *args, **kwargs)

    def cmd_USER(self, *args):
        return "+OK please send PASS command"

    def cmd_PASS(self, *args):
        return "+OK MyUsername is welcome here"

    def cmd_LIST(self, *args):
        return "+OK MyUsername is welcome here"

    def dataReceived(self, data, END=END):
        stripped_command = data.split(END)
        arguments = stripped_command[0].split()
        command, arguments = arguments[0], arguments[1:]
        print command, arguments
        self.transport.write(self.run_cmd(command, *arguments)+END)
        # self.transport.socket.close()


class POP3Factory(protocol.Factory):
    def buildProtocol(self, addr):
        return Pop3ServerSideProto()

def main():
    import sys
    pop3config = POP3Config.Instance()
    pop3config

    factory = POP3Factory()
    factory.protocol = Pop3ServerSideProto
    reactor.listenTCP(8000, factory)
    reactor.run()


if __name__ == "__main__":
    main()