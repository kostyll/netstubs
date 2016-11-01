from twisted.internet import protocol, reactor, endpoints, ssl

import pop3

class Pop3ServerSideProtoSecured(pop3.Pop3ServerSideProto):
    pass

class POP3FactorySecured(protocol.Factory):
    def buildProtocol(self, addr):
        return Pop3ServerSideProtoSecured()


def main():
    parser = pop3.make_parser()
    parser.add_argument("--server-key", type=str, action="store", dest="server_key")
    parser.add_argument("--server-cert", type=str, action="store", dest="server_cert")
    try:
        args = parser.parse_args()
    except Exception, e:
        parser.print_help()
        return
    conf = pop3.load_config(args)

    factory = POP3FactorySecured()
    factory.protocol = Pop3ServerSideProtoSecured
    reactor.listenSSL(pop3.POP3Config.Instance().port, factory,
                      ssl.DefaultOpenSSLContextFactory(
            args.server_key, args.server_cert))
    reactor.run()


if __name__ == "__main__":
    main()
