import socket
import select
import datetime
import sys


def check_port(portA, portB, portC):
    """This function checks that all the 3 port numbers are between
    1024 and 64000, if not an error message and then a system exit.
    It also checks that none of the port numbers are equal to each other"""

    if (portA < 1024) or (portA > 64000):
        print("The number for port A is invalid, it must be between 1024 and 64000")
        sys.exit(1)
    
    if (portB < 1024) or (portB > 64000):
        print("The number for port B is invalid, it must be between 1024 and 64000")
        sys.exit(1)
    
    if (portC < 1024) or (portC > 64000):
        print("The number for port C is invalid, it must be between 1024 and 64000")
        sys.exit(1)
    
    if (portA == portB) or (portA == portC) or (portB == portC):
        print("There is a duplicate port number")
        sys.exit(1)    
    
    return portA, portB, portC


def binding_sockets(host, portA, portB, portC):
    """This function opens up 3 new sockets and bind these sockets
    to the host and port number, if it is unable to bind an error message
    is printed and there is a system exit."""
     
    #Create sockets and bind to ports
    socketA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketC = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        socketA.bind((host, portA))
    except:
        print("Unable to bind portA, please check port number")
        sys.exit(1)
    try:
        socketB.bind((host, portB))
    except:
        print("Unable to bind portB, please check port number")
        sys.exit(1)
    try:
        socketC.bind((host, portC))
    except:
        print("Unable to bind portC, please check port number")
        sys.exit(1)

    return socketA, socketB, socketC 


def check_validitiy(packet):
    """This function checks the validity of the request_packet 
    that was sent in by client. It checks that all the values in the
    header are correct."""

    magicNumber = packet[0] << 8 | packet[1]
    packetType = packet[2] << 8 | packet[3]
    requestType = packet[4] << 8 | packet[5]
    length = len(packet)
    
    validPack = True
    
    if length != 6:
        print("The request packet must be 6 bytes long")
        validPack = False
    elif magicNumber != 18814:
        print("The MagicNo must be 0x497E")
        validPack = False
    elif packetType != 1:
        print("The PacketType must be 0x0001")
        validPack = False
    elif requestType < 0 or requestType > 2:
        print("The RequestType must be 0x0001 or 0x0002")
        validPack = False
    
    return validPack


def find_month(month, language_code):
    """This is a help function to get the correct month name
    for all the three port numbers and returns that month"""
    
    month_names = [['January', 'February', 'March', 'April', 'May', 
                      'June', 'July', 'August', 'September', 'October', 
                      'November', 'December'], 
                   ['Kohitātea', 'Hui-tanguru', 'Poutu-te-rangi', 'Paenga-whawha', 'Haratua', 'Pipiri', 'Hongongoi',
                      'Here-tuki-koka', 'Mahuru', 'Whiringa-a-nuku', 'Whiringa-a-rangi', 'Hakihea'],
                   ['Januar', 'Februar', 'Marz', 'April', 'Mai', 'Juni',
                      'Juli', 'August', 'September', 'Oktober', 'November', 
                      'Dezember']]
    
    return month_names[language_code][month]


def make_responsePkt(date_or_time, language_code): 
    """This function created the response_packet that will be sent back to client.
    It creates a byte array and fills it in with the appropriate values for the header fields 
    for a dt_response packet. It also creates the message that will be sent,
    whether the user is asking for the date or time and in which language"""
    
    response_packet = bytearray()
    
    magic_num = 18814
    packet_type = 2
    lang_code = language_code
    
    date_time = datetime.datetime.now()
    year = date_time.year
    month = date_time.month
    day = date_time.day
    hour = date_time.hour
    minute = date_time.minute
    
    text = ""
    
    month_name = find_month((month-1), (language_code-1))
    
    
    if date_or_time == "date":
        if language_code == 1:
            text = ("Today's date is {} {}, {}".format(month_name, day, year))
        elif language_code == 2:
            text = ("Ko te ra o tenei ra ko {} {}, {}".format(month_name, day, year))
        else:
            text = "Heute ist der {}. {} {}".format(day, month_name, year)
    
    elif date_or_time == "time":
        if language_code == 1:
            text = ("The current time is {0}:{1:02d}".format(hour, minute))
        elif language_code == 2:
            text = ("Ko te wa o tenei wa {0}:{1:02d}".format(hour, minute))
        else:
            text = ("Die Uhrzeit ist {0}:{1:02d}".format(hour, minute)) 
    
    
    text_bytes = text.encode("utf-8")
    length = len(text_bytes)
    
    response_packet += magic_num.to_bytes(2,byteorder='big')
    response_packet += packet_type.to_bytes(2,byteorder='big')
    response_packet += lang_code.to_bytes(2,byteorder='big')
    response_packet += year.to_bytes(2,byteorder='big')
    response_packet += month.to_bytes(1,byteorder='big')
    response_packet += day.to_bytes(1,byteorder='big')
    response_packet += hour.to_bytes(1,byteorder='big')
    response_packet += minute.to_bytes(1,byteorder='big')
    response_packet += length.to_bytes(1,byteorder='big')
    
    for byte in text_bytes:
        response_packet += byte.to_bytes(1,byteorder='big')
    
    return response_packet
    

def main(host, portA, portB, portC):
    """This is the main function where it get the host ip address and the 
    three port numbers and checks if they are valid and binds them into 3 sockets.
    select() is used to find which socket needs to be used, then gets whether it is
    a date or time and which language code, which is then used to call the funciton
    to make a response_packet. It then sends the response packet to client, if there
    was an error a message is printed, as well as, if the packet is not valid"""
    
    
    portA, portB, portC = check_port(portA, portB, portC)
    socketA, socketB, socketC = binding_sockets(host, portA, portB, portC)
    sockets = [socketA, socketB, socketC]
    
    while True:
        
        read, write, error = select.select(sockets, [], [])
        
        for x in read:
            
            request_packet, address = x.recvfrom(1024)
            
            client_port = x.getsockname()[1]

            valid_requestPack = check_validitiy(request_packet)
            
            requestType = request_packet[4] << 8 | request_packet[5]
            
            date_or_time = ""
            if valid_requestPack == True:
                
                if requestType == 1:
                    date_or_time = "date"
                elif requestType == 2:
                    date_or_time = "time"
                
                language_code = 1
                if client_port == portA:
                    language_code = 1
                if client_port == portB:
                    language_code = 2
                if client_port == portC:
                    language_code = 3
                
                response_packet = make_responsePkt(date_or_time, language_code)
                try:
                    x.sendto(response_packet, address)
                    print("Response Packet has been sent")
                except:
                    print("There was an error when sending to client, please try again")
        
            else:
                print("The Request Packet was not valid, please try again")
                



#This calls the main function with the different inputs of either:
#host: string for ip_address, same as client
#portA: interger of the port for English
#portB: interger of the port for Maori
#portC: interger of the port for German
main("192.168.1.75", 5005, 5006, 5007)