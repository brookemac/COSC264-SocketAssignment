import socket
import sys
import select


def check_input(request_type, ip_address, port):
    
    """This function checks the validity of the request type, ip address
    and port number. If any of the test cases fail the and error message is
    printed and a system exit"""

    if request_type != 'date' and request_type != 'time':  # Request type check
        print("That is an invalid request type, must be date or time")
        sys.exit(1)
    
    try:
        host = socket.gethostbyname(ip_address)
    except socket.gaierror:
        print("Host name could not be found and could not connect")    
        sys.exit(1)

    if int(port) < 1024 or int(port) > 64000:  # port number check
        print("Invalid port number, it must between 1024 and 64000")
        sys.exit(1)
    

    return request_type, host, port


def printPacket(response_packet):
    
    """This function is used after the response packet from the server
    has passed all its checks, then it prints the results of all that was 
    in the response packet"""
    
    magic_num = response_packet[0] << 8 | response_packet[1]
    packet_type = response_packet[2] << 8 | response_packet[3]
    language_code = response_packet[4] << 8 | response_packet[5]
    year = response_packet[6] << 8 | response_packet[7]
    month = response_packet[8]
    day = response_packet[9]
    hour = response_packet[10]
    minute = response_packet[11]
    length = response_packet[12]
    text = response_packet[13:].decode()
    
    
    print("Magic number: {}".format(hex(magic_num)))
    print("Packet type: {}".format(packet_type))
    print("Language code: {}".format(language_code))
    print("Year: {}".format(year))
    print("Month: {}".format(month))
    print("Day: {}".format(day))
    print("Hour: {}".format(hour))
    print("Minute: {}".format(minute))
    print("Length: {}".format(length))
    print('Text: "{}"'.format(text))
    
    


def check_responsePkt(response_packet):
    
    """This function checks that everything in the response packet from
    the server is in the correct dt_response form, if it is not an error 
    message is printed and there is a system exit."""
    
    magic_num = response_packet[0] << 8 | response_packet[1]
    packet_type = response_packet[2] << 8 | response_packet[3]
    language_code = response_packet[4] << 8 | response_packet[5]
    year = response_packet[6] << 8 | response_packet[7]
    month = response_packet[8]
    day = response_packet[9]
    hour = response_packet[10]
    minute = response_packet[11]
    length = response_packet[12]

    
    if len(response_packet) < 13:
        print("The response packet must be at least 13 bytes long")
        sys.exit()
    if magic_num != 18814:
        print("The MagicNo must have the value of 0x497E")
        sys.exit()
    if packet_type != 2:
        print("The PacketType must have a value of 0x0002")
        sys.exit()
    if language_code < 1 or language_code > 3:
        print("The LanguageCode must have the value of 0x0001, 0x0002, or 0x0003")
        sys.exit()
    if year >= 2100:
        print("The Year must have a value below 2100")
        sys.exit()
    if month < 1 or month > 12:
        print("The Month must have a value between 1 and 12")
        sys.exit()
    if day < 1 or day > 31:
        print("The Day must have a value between 1 and 31")
        sys.exit()
    if hour < 0 or hour > 23:
        print("The Hour must have a value between 0 and 23")
        sys.exit()
    if minute < 0 or minute > 59:
        print("The Minute must have a value between 0 and 59")
        sys.exit()
    if (len(response_packet) - 13) != length:
        print("The Length must equal the payload length")
        sys.exit()
    
    printPacket(response_packet)
    
    
def main(request_type, ip_address, port):
    
    """This is the main function where it takes the request type,
    ip address and port number and call the check_input function. 
    It opens up a UDP socket and prepares a dt_request packet to send to server.
    It then waits for a response from server checks if it takes longer than a second and then processes that with checks and prints the final result of the response packet, it then closes"""
    
    request_type, ip_address, port = check_input(request_type, ip_address, port)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    dt_request = bytearray()
    
    if request_type == "date":
        type_req = (0x0001)
    else:
        type_req = (0x0002)    
    
    magic_num = 18814
    packet_type = 1
    
    dt_request += magic_num.to_bytes(2,byteorder='big')
    dt_request += packet_type.to_bytes(2,byteorder='big')
    dt_request += type_req.to_bytes(2,byteorder='big')
    
        
    try:
        client.sendto(dt_request, (ip_address, int(port)))
        print("Request Packet has been sent")
    except:
        print("There has been an error when sending request packet")
    
    

    
    #when response packet from server has been sent to client
    client.setblocking(0)
    lists, _, _ = select.select([client], [], [], 1)
    
    try:
        if lists[0]:
            response_packet, address = client.recvfrom(1024)
            check_responsePkt(response_packet)            

    except IndexError:
        print("There has been a timeout error, response packet took over a second")
        sys.exit(1)
        
    

#This calls the main function with the different inputs of either:
#request_type: "date" or "time"
#ip_address: either as a dotted-decimal notation or host-name of the computer, as a string as server
#port: interger of the port for either English, Maori or German
main("date", "192.168.1.65", 5001)