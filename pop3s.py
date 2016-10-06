from twisted.internet import protocol, reactor, endpoints, ssl


class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

factory = EchoFactory()
factory.protocol = Echo
reactor.listenSSL(8000, factory,
                  ssl.DefaultOpenSSLContextFactory(
        'keys/server.key', 'keys/server.crt'))
reactor.run()