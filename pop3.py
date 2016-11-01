import os
from email.header import decode_header, Header
import json
from twisted.internet import protocol, reactor, endpoints

import singleton

import argparse

@singleton.Singleton
class POP3Config:
    def __init__(self):
        pass

    def setConf(self, user, password, directory, port, from_, subject, to_):
        print 'POP3Config created'
        self._dir = directory
        self._user = user
        self._password = password
        self._port = port
        self._from_ = from_
        self._subject = subject
        self._to_ = to_
        return self

    @property
    def directory(self):
        return self._dir

    @property
    def port(self):
        return self._port

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def from_(self):
        return self._from_

    @property
    def to_(self):
        return self._to_

    @property
    def subject(self):
        return self._subject


class Pop3ServerSideProto(protocol.Protocol):

    def connectionMade(self):
        self.transport.write("+OK POP3 server ready\r\n")

    @property
    def emls(self):
        if not getattr(self, "_emls", None):
            self._emls = map(lambda x: x[:-4], filter(lambda x: x.endswith(".eml"), os.listdir(POP3Config.Instance().directory)))
        return self._emls

    def size(self, uidl):
        return os.path.getsize(os.path.join(POP3Config.Instance().directory, uidl+".eml"))

    def encode(self, string):
        return Header(string, 'utf-8').encode()

    def make_header(self, header_name, header_value, encode=False):
        return "%s: %s\r\n" % (header_name, self.encode(header_value) if encode else header_value)

    END = "\r\n"
    def run_cmd(self, cmd, *args, **kwargs):
        print "Run cmd %s: args: %s" % (cmd, str(args))
        command_handler = getattr(
            self,
            "cmd_"+cmd.upper(),
            lambda *args, **kwargs: "-ERR Unknown command"
        )
        result = command_handler(*args, **kwargs)
        print "cmd '%s' result:\n%s" % (cmd, result)
        return result

    def dataReceived(self, data, END=END):
        print "S = %s" % (id(self))
        stripped_command = data.split(END)
        arguments = stripped_command[0].split()
        command, arguments = arguments[0], arguments[1:]
        print command, arguments
        self.transport.write(self.run_cmd(command, *arguments)+END)
        # self.transport.socket.close()P

    def cmd_USER(self, *args):
        print "s = %s" % (id(self))
        print args
        if POP3Config.Instance().user != args[0]:
            self.transport.loseConnection()
        return "+OK please send PASS command"

    def cmd_CAPA(self, *args):
        """
        TOP
        USER
        PASS
        LOGIN-DELAY 60
        UIDL
        IMPLEMENTATION ClMail POP Server
        .
        """
        return "+OK\r\n" + "\r\n".join(["USER", "PASS", "UIDL", "TOP", "IMPLEMENTATION pop3 server", "."])

    def cmd_PASS(self, *args):
        print args
        if POP3Config.Instance().password != args[0]:
            self.transport.loseConnection()
        return "+OK MyUsername is welcome here"

    def cmd_LIST(self, *args):
        if len(args) == 0:
            return "+OK\r\n" + "\r\n".join(map(lambda item: "%s %s" % (item[0]+1, self.size(item[1])), enumerate(self.emls)))+"\r\n."
        else:
            number = int(args[0])
            return "+OK\r\n" + "%s %s" % (number, self.size(self.emls[number-1])) +"\r\n."

    def cmd_UIDL(self, *args):
        return "+OK\r\n" + "\r\n".join(map(lambda item: "%s %s" % (item[0]+1, item[1]), enumerate(self.emls)))+"\r\n."

    def cmd_STAT(self, *args):
        return "+OK %s %s\r\n" % (len(self.emls), sum(map(lambda x: self.size(x), self.emls)))

    def headers(self):
        return self.make_header("From", "<%s>" % POP3Config.Instance().from_, encode=False) + \
            self.make_header("To", "<%s>" % POP3Config.Instance().to_, encode=False) + \
            self.make_header("Content-Type", "text/plain") + \
            self.make_header("Subject", POP3Config.Instance().subject, encode=True)

    def cmd_TOP(self, *args):
        print ">>calling TOP..."
        msg_number = int(args[0])
        try:
            msg_lines = int(args[1])
        except IndexError:
            msg_lines = 0
        print "sending %s: %s" % (msg_number, msg_lines)
        result = "+OK\r\n" + self.headers()
        if msg_lines > 0:
            result += "\r\n".join("test line %s" % x for x in xrange(msg_lines))
        result += "\r\n."
        print result
        return result

    def cmd_RETR(self, *args):
        number = int(args[0])
        result = "+OK\r\n" + self.headers() + "\r\n" + open(self.emls[number-1]+".eml", "rt").read() + "\r\n."
        return result

    def cmd_QUIT(self, *args):
        self.transport.loseConnection()
        return ""


class POP3Factory(protocol.Factory):
    def buildProtocol(self, addr):
        return Pop3ServerSideProto()


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login-pass-pare", "-l", dest="login_password", action="store", type=str, default="admin:admin")
    parser.add_argument("--port", "-p", dest="port", action="store", type=int, default=110)
    parser.add_argument("--directory", "-d", dest="directory", action="store", type=str, default="./")
    parser.add_argument("--from", "-f", dest="from_", action="store", type=str, default="test@testhost")
    parser.add_argument("--subject", "-s", dest="subject", action="store", type=str, default="testsubject")
    parser.add_argument("--to", "-t", dest="to_", action="store", type=str, default="to@testhost")
    return parser


def load_config(args):
    POP3Config.Instance().setConf(*(args.login_password.split(":") + [args.directory, args.port, args.from_, args.subject, args.to_] ))

def main():
    parser = make_parser()

    try:
        args = parser.parse_args()
    except Exception, e:
        parser.print_help()
        return

    load_config(args)

    factory = POP3Factory()
    factory.protocol = Pop3ServerSideProto
    reactor.listenTCP(POP3Config.Instance().port, factory)
    reactor.run()


if __name__ == "__main__":
    main()