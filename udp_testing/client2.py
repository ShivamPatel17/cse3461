#client for the IM 
import socket,pickle
import select
import queue
import sys
from threading import Thread
import time

print("File Sharing Platform\n")

ftpc= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ftps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def main():
    ''' 
    create socket
    param1: family
        AF_INET -> Address Format Internet
    param2: type
        SOCK_DGRAM 
    '''
    
    server_address = ('0.0.0.0', 10000)
    #listen on any free port
    ftpc.bind(('0.0.0.0', 0))
    #receive data on this port
    receiver.bind(('0.0.0.0', 0))


    #listen on ftpc 
    try:
        #args has an empty list because thread wouldn't work on just the socket
        Thread(target = Sharing, args=(ftpc,[])).start()
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
                        success = Download(filename, addr)
                        if(success == 1):
                            break
                        #send request to (Sharing())
                        #this listen for download() maybe start another thread?
                        #make the request to the ftpc connection received from the server   
                else:
                    print("Unrecognized Code: {} ".format(code))
                          
def Sharing(ftpc, max_buffer = 4096):
    print("Listening on {}".format(ftpc.getsockname()[1]))
    while True:
        filename, addr = ftpc.recvfrom(4096)
        filename = filename.decode().strip()
        print(addr)
        print("Request from {} to download {}".format(addr, filename))
        try:
            f = open(filename, "r")
            SendFile(f, addr)
        except:
            print("Couldn't open/send file: {}".format(filename))

def SendFile(f, addr):
    data = f.read(4096)
    address = addr
    while(data):
        if(ftpc.sendto(data.encode(), address)):  
            data = f.read(4096)
            time.sleep(0.05)
        print("file has been sent")
        
    
def Download(filename, port): 
    address = ('0.0.0.0', int(port))
    timeout = 10.0
    start_time = time.clock()
    i = (receiver.sendto(filename.encode(), address))
    print("{} is requesting {} to download {}".format(receiver.getsockname()[1],port, filename))

    f = open(filename, 'wb')
    inputs = [receiver, 0]
    while inputs:
        readable, writeable, exceptional = select.select(inputs, [], [])
        for i in readable:
            print("got some input")
            if(i ==0):
                print("reading from terminal")
            elif(i is receiver):
                data, addr = receiver.recvfrom(4096)
                f.write(data.decode())
                f.close()
                break
            else:
                print(i)
    
    f.close()
    print("finished download")
    
    '''except:
        print("Failed to download: {}".format(filename))
        return 0
    print("Downloaded: {}".format(filename))
    return 1'''

if __name__ == "__main__":
    main()    