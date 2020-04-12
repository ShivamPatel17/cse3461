#client for the IM 
import socket
import select
import queue
import sys

print("IM Platform")


def main():
    ''' 
    create socket
    param1: family
        AF_INET -> Address Format Internet
    param2: type
        SOCK_STREAM -> socket stream (sequenced, reliable, two-way connection, connection based stream over TCP)
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        client.connect(('0.0.0.0', 8080))
    except:
        print("Connection error")
        return

    #this is a list of the sources we can get input from 
    #client, which is the server side response and stdin, which is where the client can type into the terminal. 
    inputs = [client, 0]
    #as long as we have some input sources, we can read through them
    while inputs:
        #select will grab all the inputs that are sent here to the client
        readable, writeable, exceptional = select.select(inputs, [], [])

        for i in readable:
            #terminal stdin input
            if( i == 0):
                command = input().strip()
                client.send(command.encode())
            #response/message from the server
            elif(i is client):
                response = client.recv(4096).decode()
                print(response)
    #close connection
    client.send("close".encode())
    

if __name__ == "__main__":
    main()    