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
    try:
        args = parser.parse_args()
    except Exception, e:
        parser.print_help()
        return
    conf = pop3.load_config(args, SMTPConfig)

    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(conf.user, conf.password)
    portal.registerChecker(checker)
    factory = ConsoleSMTPFactory(portal)

    reactor.listenSSL(
        conf.port,
        factory,
        ssl.DefaultOpenSSLContextFactory(
            'keys/server.key', 'keys/server.crt')
    )
    reactor.run()

if __name__ == "__main__":
    print "to check it use: openssl s_client -connect localhost:2525 -crlf -quiet"
    main()