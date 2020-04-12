#server for the IM
import socket
import sys
from threading import Thread
#create a database dict that the server can reference for user
user_pass = {}
user_conn = {}



def main():
    RunServer()
#this reads in the users/pass from the database and loads it into the users dictionary


def UpdateDict():
    #opens the database file
    database = open("Database", "r")
    line = "init"
    #reads all the lines to add the usernames and passwords to a dictionary for quick loop up
    while(line):
        line = database.readline()
        data = line.split(",", 1)
        if(len(data)>1):
            username = data[0]
            password = data[1].strip()
            user_pass[username] = password
    print("Database loaded")
    database.close()
#this function inserts an entry into the database file
def InsertInDatabase(username, password):
    #open database file to appened
    database = open("Database", "a")

    #create entry, enter it, the close file
    entry = "{},{}\n".format(username,password.strip())
    database.write(entry)
    database.close()
#registers a new user
def Register(registration):
    #this is to separate username and password
    info = registration.split(" ")
    username = info[0]
    if(len(info)<2):
        return "Must provide a password to Register"
    password = info[1]
    if user_pass.get(username):
        return "Username already exists"
    else: 
        user_pass[username] = password
        InsertInDatabase(username,password)
        UpdateDict()
        return "Added new user: {}".format(username)

#run the server
def RunServer():
    #create a Database file in case it was deleted or doese not exist
    create = open("Database", "a+")
    create.close()
    #load in all users to the dictionare
    UpdateDict()
    #create the server socket and have it listening on localhost:8080
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('0.0.0.0', 8080))
    serv.listen(5)
    print("Listening on {}".format(serv.getsockname()[1]))

    #handle connections, this should run as long as the server is running
    while True:   
        #wait here until a client connection
        conn, addr = serv.accept()
        ip = str(addr[0])
        port = str(addr[1])
        print("Connected with [IP: {}     Socket: {}]".format(ip, port))

        try:
            #create a new thread for each of the connections and pass with it as args the: connection, ip and port
            Thread(target = ClientThread, args=(conn, ip, port)).start()
        except:
            print("Thread didn't start")
        #client has connected, now read the whole message
    serv.close()
#login function
def Login(ip, port, login):
    #split login infor into user and password
    info = login.split(" ")
    username = info[0]
    if(len(info)<2):
        return {'msg': "Must provide a password to login", 'user':""}
    password = info[1]
    if(user_pass.get(username)):
        if user_pass[username] == password:
            return {"msg":"Login successful", 'user':username}
        else: 
            return {"msg":"Incorrect password", 'user':''}
    else:
        return {'msg':"No account associated with this username",'user':""}
#logout function
def Logout(user):
    del user_conn[user]
    return "Logging out"
#send a message to a user
def Message(activeuser, user, message):
    try:
        #find the connection that is associated with the user (name)
        conn = user_conn[user]
        msg = "[FROM: {}] {}".format(activeuser, message)
        #send the message
        conn.send(msg.encode())
        return "Message delivered"
    except:
        return "Error sending message"

def ClientThread(conn, ip, port, max_buffer = 4096):
    #connection is default active on creation
    active = True
    #active_user keeps track of the username if a client logins in. Default set to not logged in
    active_user=""

    #in this loop, the server is handling a specific connection and 
    while active:
        #this client input is the value returned by get input, which waits until a message is received from a client
        client_input = GetInput(conn, max_buffer)
        client_input = client_input.split(" ", 1)
        #grab the first word delimted by a space, this is the command
        command = client_input[0]
        command = command.upper()


        #this section is straight forward: call the method associated with the command

        
        #register new user
        if(command == "REGISTER"):
            if(active_user):
                conn.send("Must Logout before registering a new user".encode())
            else:
                if(len(client_input)>1):
                    response = Register(client_input[1])
                    conn.send(response.encode())
                else:
                    conn.send("Must provide both a username and a password to register".encode())
        #login
        elif(command == "LOGIN"):
            if(active_user):
                conn.send("Already logged in. Must sign out first".encode())
            else:
                #ensure that's there's both a username and a password
                if(len(client_input)>1):
                    args = client_input[1]
                    response = Login(ip, port, args)
                    active_user = response['user']
                    conn.send(response['msg'].encode())
                    user_conn[active_user] = conn
                else:
                    conn.send("Must provide both a username and a password to login".encode())
        #list active users 
        elif(command == "LIST"):
            active_users = "Active Users\n-------------------\n"
            for usr in user_conn.keys():
                active_users+="{}\n".format(usr)
            active_users+="-------------------"
            conn.send(active_users.encode())
        #does this have to work for offline users? prof
        elif(command == "MESSAGE"):
            if(active_user):
                args = (client_input[1]).split(" ", 1)
                if(len(args)>1):
                    response = Message(active_user, args[0], args[1])
                    conn.send(response.encode())
                else:
                    conn.send("Must provide a message to send".encode())
                
            else:
                conn.send("Must be signed in to send a message".encode())
        #logout 
        elif(command == "LOGOUT"):
            #but only if someone is currently logged in
            if(active_user):
                if(len(client_input)>1):
                    if(client_input[1] == active_user):
                        response = Logout(active_user)
                    else: 
                        response = "You can only log yourself out"

                else:
                    response = Logout(active_user)
                    active_user = ""
                conn.send(response.encode())
            else:
                    conn.send("Not logged in".encode())
        #close the connection
        elif(command == "CLOSE"):
            if(active_user):
                active_user = ""
            conn.close()
            print("Closing conn with [IP: {}     Socket: {}]".format(ip, port))
            break
        else:
            #invvalude command section
            response = "ERROR: Command not recognized"
            conn.send(response.encode())

        #print the active user's username here if that account is logged in
        #these print statements are so the user can see what's happening on the server
        if(active_user):
            print("[{}] {}: {}     Socket: {}".format(active_user, command,ip, port))
        else:
            print("[not logged in] {}: {}     Socket: {}".format(command,ip, port))

            



def GetInput(conn, max_buffer):
    #get client input
    #this is blocking so the thread is going to wait here until there's input received
    client_input = conn.recv(max_buffer)
    message = client_input.decode()
    return message



if __name__ == "__main__":
    main()

