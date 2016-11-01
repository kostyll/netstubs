#!/usr/bin/env python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

# You can run this module directly with:
#    twistd -ny emailserver.tac

"""
A toy email server.
"""
from __future__ import print_function

import os
import uuid
from zope.interface import implementer

from twisted.internet import defer
from twisted.mail import smtp
from twisted.mail.imap4 import LOGINCredentials, PLAINCredentials

from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.cred.portal import IRealm
from twisted.cred.portal import Portal
from twisted.application import internet
from twisted.application import service


import singleton
import pop3


@singleton.Singleton
class SMTPConfig:
    def __init__(self):
        pass

    def setConf(self, user, password, directory, port, from_, subject, to_):
        print('SMTPConfig created')
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


@implementer(smtp.IMessageDelivery)
class ConsoleMessageDelivery:
    def receivedHeader(self, helo, origin, recipients):
        return "Received: ConsoleMessageDelivery"

    
    def validateFrom(self, helo, origin):
        # All addresses are accepted
        return origin

    
    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        # if user.dest.local == "console":
        #     return lambda: ConsoleMessage()
        # raise smtp.SMTPBadRcpt(user)
        return lambda: ConsoleMessage()


@implementer(smtp.IMessage)
class ConsoleMessage:
    def __init__(self):
        self.lines = []

    
    def lineReceived(self, line):
        self.lines.append(line)

    
    def eomReceived(self):
        print("New message received:")
        print("\n".join(self.lines))

        with open(os.path.join(SMTPConfig.Instance().directory, uuid.uuid1().hex+".eml"), "wb") as f:
            f.write("\n".join(self.lines[2:]))

        self.lines = None
        return defer.succeed(None)

    def connectionLost(self):
        # There was an error, throw away the stored lines
        self.lines = None


class ConsoleSMTPFactory(smtp.SMTPFactory):
    protocol = smtp.ESMTP

    def __init__(self, *a, **kw):
        smtp.SMTPFactory.__init__(self, *a, **kw)
        self.delivery = ConsoleMessageDelivery()
    

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        p.delivery = self.delivery
        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p



@implementer(IRealm)
class SimpleRealm:
    def requestAvatar(self, avatarId, mind, *interfaces):
        if smtp.IMessageDelivery in interfaces:
            return smtp.IMessageDelivery, ConsoleMessageDelivery(), lambda: None
        raise NotImplementedError()



def main():
    if __name__ == "__main__":
        parser = pop3.make_parser()
        try:
            args = parser.parse_args()
        except Exception, e:
            parser.print_help()
            return
        conf = pop3.load_config(args, SMTPConfig)
        pop3.save_pid(args)
    
    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    if __name__ == "__main__":
        checker.addUser(conf.user, conf.password)
    else:
        checker.addUser("guest", "password")
    portal.registerChecker(checker)
    factory = ConsoleSMTPFactory(portal)

    if __name__ == "__main__":

        from twisted.internet import reactor

        reactor.listenTCP(conf.port, factory)
        reactor.run()
    else:
        a = service.Application("Console SMTP Server")
        internet.TCPServer(2525, factory).setServiceParent(a)

        return a


application = main()

