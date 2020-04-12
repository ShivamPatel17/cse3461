#client for the IM 
import socket,pickle
import select
import queue
import sys
from threading import Thread

print("File Sharing Platform\n")


def main():
    ''' 
    create socket
    param1: family
        AF_INET -> Address Format Internet
    param2: type
        SOCK_DGRAM 
    '''
    ftpc= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ftps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', 10000)
    #listen on any free port
    ftpc.bind(('0.0.0.0', 0))


    #listen on ftpc 
    try:
        #args has an empty list because thread wouldn't work on just the socket
        Thread(target = Sharing, args=(ftpc, [])).start()
    except:
        print("Thread didn't start")
    #this is a list of the sources we can get input from 
    #client, which is the server side response and stdin, which is where the client can type into the terminal. 
    inputs = [ftps, 0]
    #as long as we have some input sources, we can read through them
    while inputs:
        #select will grab all the inputs that are sent here to the client
        readable, a, b = select.select(inputs, [], [])

        for i in readable:
            #terminal stdin input
            if( i == 0):
                command = input().strip()
                message = command + ":"+str(ftpc.getsockname()[1])
                ftps.sendto(message.encode(), server_address)
            #response/message from the server
            elif(i is ftps):
                #maybe from here check if you're supposed to send a mess
                response = pickle.loads(ftps.recv(4096))
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
                        success = Download(filename, addr, ftps)
                        if(success == 1):
                            break
                        #send request to (Sharing())
                        #this listen for download() maybe start another thread?
                        #make the request to the ftpc connection received from the server
                #download request from another client
                elif(code ==3):
                    filename, addr = response[1]
                    print("Request from {} to download {}".format(addr, filename))                 
                else:
                    print("Unrecognized Code: {} ".format(code))
                          
def Sharing(ftpc, max_buffer = 4096):
    print("Listening on {}".format(ftpc.getsockname()[1]))
    data, addr = ftpc.recvfrom(4096)
    print("Request from {} to download {}".format(addr, data))

def Download(filename, port, ftps): 
    address = ('0.0.0.0', int(port))              
    ftps.sendto(filename.encode(), address)

if __name__ == "__main__":
    main()    