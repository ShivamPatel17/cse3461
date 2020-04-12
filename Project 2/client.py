#client for the IM 
import socket,pickle
import select
import queue
import sys

print("File Sharing Platform\n")


def main():
    ''' 
    create socket
    param1: family
        AF_INET -> Address Format Internet
    param2: type
        SOCK_DGRAM 
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ftps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #listen on any free port
    ftps.bind(('0.0.0.0', 0))

    #this is a list of the sources we can get input from 
    #client, which is the server side response and stdin, which is where the client can type into the terminal. 
    inputs = [client, 0]
    #as long as we have some input sources, we can read through them
    while inputs:
        #select will grab all the inputs that are sent here to the client
        readable, a, b = select.select(inputs, [], [])

        for i in readable:
            #terminal stdin input
            if( i == 0):
                command = input().strip()
                client.sendto(command.encode(), server_address)
            #response/message from the server
            elif(i is client):
                #maybe from here check if you're supposed to send a mess
                response = pickle.loads(client.recv(4096))
                code = response[0]
                # 0 = error message to SERVER
                if(code == 0):
                    print(response[1])
                # 1 = list of files available for download from SERVER
                elif(code == 1):
                    print(response[1])
                # 2 = addr to request download from SERVER
                elif(code == 2):
                    download_addresses = response[1]
                    filename = response[2]
                    for addr in download_addresses:
                        print("Requesting {} to download {}".format(addr, filename))
                        request = (3, filename)
                        client.send(pickle.dumps(request), addr)
                #download request from another client
                elif(code ==3):
                    filename, addr = response[1]
                    print("Request from {} to download {}".format(addr, filename))                 
                else:
                    print("Unrecognized Code: {} ".format(code))
                          
    #close connection
    client.send("close".encode())
    

if __name__ == "__main__":
    main()    