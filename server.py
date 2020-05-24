import socket
from select import select
import sys
import subprocess
import logging
from rsa_enc_dec import get_encrypted_message
from rsa_enc_dec import get_decrypted_message


def process_data(sock, message):
    message = get_decrypted_message(message).strip()
    client_addr = client_addr_list[socket_list.index(sock) - 1]
    logging.info("Received %s from %s" % (message, client_addr))
    try:
        type, message = message.split("$")
        if type == 'command':
            process_command(sock, message, client_addr)
        else:
            send_ack_noack(sock, 'ACK')
            logging.info("Sent ACK to client %s:%s" % client_addr)
    except ValueError as err:
        logging.error("Invalid message received from client, error = %s" % err)
        send_ack_noack(sock, 'NOACK')
        logging.info("Sent NOACK to client %s:%s" % client_addr)
    except Exception as err:
        logging.error("Something went wrong while processing message, error = %s" % err)
        send_ack_noack(sock, 'NOACK')
        logging.info("Sent NOACK to client %s:%s" % client_addr)


def send_ack_noack(client, message):
    client.send(get_encrypted_message(message))


def process_command(sock, command, client_addr):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    output, error = output.decode('utf-8')[:-2], error.decode('utf-8')
    status_code = p.wait()
    logging.info("command run %s " % command)
    logging.info("command status code %s " % status_code)
    if status_code == 0:
        logging.info("command output %s " % output)
        reply = '%s$%s$%s' % ('ACK', status_code, output)
    else:
        logging.error("command error %s " % error)
        reply = '%s$%s$%s' % ('NOACK', status_code, error)
    send_ack_noack(sock, reply)
    logging.info("Sent NOACK to client %s:%s" % client_addr)


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename='logs/server.log')

# create server socket
server = None
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info("Server socket created successfully.")
except socket.error as err:
    logging.error("Server socket creation failed with error %s" % err)
    exit(-1)

# default port for server
host = "0.0.0.0"
port = 1213

# bind server to listen on network
try:
    server.bind((host, port))
    logging.info("Server is bind to address %s:%s" % (host, port))
except Exception as err:
    logging.warning("Check if any other process is running at %s:%s" % (host, port))
    logging.error("Server bind to address %s:%s failed with error %s" % (host, port, err))
    exit(-2)

# start listening for incoming connections
server.listen(20)

socket_list = [server]
client_addr_list = []
server_max_timeouts = 30
timeouts = 0

logging.info("Server started listening")
try:
    while timeouts < server_max_timeouts:
        readable_sockets, writable, errored = select(socket_list, [], [], 1)
        for sock in readable_sockets:
            timeouts = 0
            # new connection
            if sock == server:
                client, address = server.accept()
                socket_list.append(client)
                client_addr_list.append(address)
                logging.info("Connection received from client %s:%s" % address)
            else:
                data = sock.recv(1024)
                if data:
                    process_data(sock, data)
                else:
                    index = socket_list.index(sock) - 1
                    client_addr = client_addr_list[index]
                    logging.info("Connection closed from client %s:%s" % client_addr)
                    socket_list.remove(sock)
                    del client_addr_list[index]
                    sock.close()
        if len(socket_list) == 1:
            timeouts += 1
        else:
            timeouts = 0
except KeyboardInterrupt:
    logging.info("Stopping the server\n\n")
else:
    logging.warning("Server idle timed out, So Stopping the server\n\n")

server.close()
