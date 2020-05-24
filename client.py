import os
import socket
import random
import logging
import sys
from rsa_enc_dec import get_encrypted_message
from rsa_enc_dec import get_decrypted_message


def send_message(client, message):
    try:
        enc_message = get_encrypted_message(message)
        client.send(enc_message)
        logging.info("Successfully sent the message %s to server" % message)
    except Exception as err:
        logging.error("Failed to send the message %s to server, error %s" % (message, err))


def recv_ack_noack(client):
    message = client.recv(1024)
    if not message:
        logging.error("Connection closed to the server")
        exit(-4)
    else:
        message = get_decrypted_message(message)
        if message == 'ACK':
            logging.info("ACK received, Message is received successfully by the server")
            return
        elif message == 'NOACK':
            logging.error("NOACK received, Message is not in format for the server")
            return
        message, status_code, output = message.split('$')
        if message == 'ACK':
            logging.info("ACK received, Command successfully ran on the server")
            logging.info("status code = %s, command output = %s" % (status_code, output))
        else:
            logging.error("NOACK received, Command failed to run the on server")
            logging.error("status code = %s, command error = %s" % (status_code, output))


def get_log_file():
    filename = 'logs/client.log'
    index = 0
    newfilename = filename
    while os.path.isfile(newfilename):
        newfilename = filename[:-4] + str(index) + ".log"
        index += 1
    return newfilename


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename=get_log_file())

# create a socket for client
client = None
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info("Client socket is created successfully")
except socket.error as err:
    logging.error("Client socket creation failed with error %s" % err)
    exit(-1)

# server host and port
host = "localhost"
port = 1213

# try to connect to the server
try:
    client.connect((host, port))
    logging.info("Client connected to server successfully")
except socket.error as err:
    logging.error("Client connection to server failed with error %s" % err)
    logging.warning("Make sure server is running at %s:%s" % (host, port))
    exit(-2)

# read all messages and commands
all_messages = []
messages_filename = "messages.txt"
try:
    messages_file = open(messages_filename)
    all_messages = messages_file.readlines()
    messages_file.close()
    logging.info("Read all the messages and commands from %s file" % messages_filename)
except IOError as err:
    logging.error("Failed to read the %s file with error %s" % (messages_filename, err))
    exit(-3)

total_messages = random.randint(10, 20)
for i in range(total_messages):
    message = random.choice(all_messages)
    send_message(client, message)
    recv_ack_noack(client)

client.close()
logging.info("Successfully closed the client socket")
