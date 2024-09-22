import threading

from grpc_service.server import start_server
from grpc_service.rabbitmq import main as message_receiver


def main():
    t1 = threading.Thread(target=start_server)
    t2 = threading.Thread(target=message_receiver)
    t1.start()
    t2.start()
    t2.join()


if __name__ == '__main__':
    main()
