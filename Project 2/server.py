#server for the File Sharing Platform
import socket, pickle
import sys
from threading import Thread

#key is a file, value is a set of address that can share that file
file_addr = {}
#key is addr, value is a set of the files that addr can share
addr_files = {}
#this is a set of clients that are "active"
active = {}

def main():
    RunServer()
#this reads in the users/pass from the database and loads it into the users dictionary

#run the server
def RunServer():
    #create the server socket and have it listening on localhost:8080
    serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', 10000)
    serv.bind(server_address)
    print("Listening on {}".format(serv.getsockname()[1]))

    #handle connections, this should run as long as the server is running
    while True:   
        #wait here until a client connection
        data, addr = serv.recvfrom(4096)
        print("Request from [IP: {}  Socket: {}]".format(addr[0], addr[1]))
        try:
            #create a new thread for each of the connections and pass with it as args the: connection, ip and port
            Thread(target = HandleRequest, args=(serv,data, addr)).start()
        except:
            print("Thread didn't start")
        #client has connected, now read the whole message
    serv.close()

#addr[0] is IP and addr[1] is port
def HandleRequest(server_socket, data, addr, max_buffer = 4096):
    request = data.decode()
    data = request.split(':', 1)
    client_server = data[1]
    request = data[0].split(' ', 1)
    command = request[0].upper()
    #print(client_server)
    if(len(request)>1):
        #args are the files names, if present
        args = request[1]

    
    if(command == 'REGISTER'):
        active.add(addr)
    #this is for a client sayign which files it can share
    elif(command == 'SHARE'):
        if(len(request)>1):
            files = args.split(' ')
            AddFileAddresses(files, client_server)
            AddAddressFiles(files, client_server)
    #send client the files available for download
    elif(command == 'LIST'):
        file_list = []
        for address in addr_files.keys():
            if(address != client_server):
                file_list.extend(addr_files[address])
        response = (1, set(file_list))
        server_socket.sendto(pickle.dumps(response), addr)
    #send client the address of where to download a file
    elif(command == 'DOWNLOAD'):
        if(len(request)==2):
            file_addr[args]
            if(args in file_addr.keys()):
                address = []
                for add in file_addr[args]:
                    if(add!=client_server):
                        address.append(add)
                response = (2, address, args)
            else:
                response = (0, "File does not exist for download")
        else: 
            #exactly 1 file may be requested for download
            response = (0, "Exactly 1 file must be requested to download")
    
        server_socket.sendto(pickle.dumps(response), addr)
    else:
        msg = 'Invalid command {}'.format(command)
        response = (0, msg)
        server_socket.sendto(pickle.dumps(response), addr)

def AddFileAddresses(files, addr):
    files = set(files)
    for file in files:
        if(file in file_addr.keys()):
            file_addr[file].add(addr)
        else:
            file_addr[file] = {addr}

def AddAddressFiles(files, addr):
    files = set(files)
    if(addr in addr_files.keys()):
        addr_files[addr].update(files)
    else:
        addr_files[addr] = files

if __name__ == "__main__":
    main()