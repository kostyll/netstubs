#!/usr/bin/env python
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse

from twisted.application import internet
from twisted.application import service
from twisted.cred.portal import Portal
from twisted.internet import ssl
from twisted.internet import reactor


import smtp
from smtp import ConsoleMessage, ConsoleSMTPFactory, SMTPConfig, SimpleRealm
import pop3

def main():

    parser = pop3.make_parser()
    parser.add_argument("--server-key", type=str, action="store", dest="server_key")
    parser.add_argument("--server-cert", type=str, action="store", dest="server_cert")

    try:
        args = parser.parse_args()
    except Exception, e:
        parser.print_help()
        return
    conf = pop3.load_config(args, SMTPConfig)
    pop3.save_pid(conf)

    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(conf.user, conf.password)
    portal.registerChecker(checker)
    factory = ConsoleSMTPFactory(portal)

    reactor.listenSSL(
        conf.port,
        factory,
        ssl.DefaultOpenSSLContextFactory(
            args.server_key, args.server_cert)
    )
    reactor.run()

if __name__ == "__main__":
    print "to check it use: openssl s_client -connect localhost:2525 -crlf -quiet"
    main()