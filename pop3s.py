from twisted.internet import protocol, reactor, endpoints, ssl

import pop3

class Pop3ServerSideProtoSecured(pop3.Pop3ServerSideProto):
    pass

class POP3FactorySecured(protocol.Factory):
    def buildProtocol(self, addr):
        return Pop3ServerSideProtoSecured()


def main():
    parser = pop3.make_parser()
    try:
        args = parser.parse_args()
    except Exception, e:
        parser.print_help()
        return
    pop3.load_config(args)

    factory = POP3FactorySecured()
    factory.protocol = Pop3ServerSideProtoSecured
    reactor.listenSSL(pop3.POP3Config.Instance().port, factory,
                      ssl.DefaultOpenSSLContextFactory(
            'keys/server.key', 'keys/server.crt'))
    reactor.run()


if __name__ == "__main__":
    main()
