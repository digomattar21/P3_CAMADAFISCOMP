import sys
from enlace import *
import time
from util import setHeader, setEOP


serialPort = "/dev/ttyACM1"   
#serialName = "/dev/tty.usbmodem1463101" 
#serialName = "COM1"  



def main():
    try:
        com1 = enlace(serialPort)
        com1.enable()


        print('Comunicacao ativa, threads e comunicacao serial iniciados')

        listening = True
        img = bytes(0)
        STATE ='INIT'
        passedP = 0

        while listening:
            rxBuffer, nRx = com1.getData(10)
            headerZero = rxBuffer[0]
            headerType = rxBuffer[1]
            print('Header init: ', headerZero)
            if headerZero ==255:
                STATE = "HEADER"
            else:
                STATE = 'ERROR'
                head = setHeader(2,0,0,0)
                eop = setEOP()
                packet = head + eop
                com1.sendData(packet)

            if STATE == "HEADER":
                if headerType == 1:
                    STATE = 'HANDSHAKE'
                elif headerType == 0:
                    STATE = 'DATA'
                    print('STATE: ', 'DATA')
            if STATE == 'HANDSHAKE':
                head = setHeader(3,0,0,0)
                eop = setEOP()
                packet = head + eop  
                print('packet len',len(packet))
                com1.sendData(packet)
                print('Estabelecendo HandShake')

            elif STATE == "DATA":
                nOfPackets = rxBuffer[2]
                print('Packets to receive:', nOfPackets)
                currPacket = rxBuffer[3]
                print('Current Packet Number: ', currPacket)
                packetSz = rxBuffer[4]
                print('packet Sz: ', packetSz)
                deltaPacket = currPacket - passedP
                print(deltaPacket)
                rxBefore = rxBuffer
                passedP+=1

                if (packetSz<114):
                    print('entrou soh aq')
                    eop,nEOP = com1.getData(4)
                    
                else:
                    rxBuffer,nRx = com1.getData(packetSz)
                    eop, nEOP = com1.getData(4)
                    print('Current Packet:', currPacket)
                
                if int.from_bytes(eop, byteorder='big') !=0 or deltaPacket !=1:
                    if deltaPacket !=1:
                        STATE='ERROR'
                        print('ERROR: wrong packet sending order... retrying')
                        print('currPacket', currPacket)
                        print('passedP', passedP)
                        head = setHeader(5,0,0,0)
                        eop = setEOP()
                        packet = head +eop
                        com1.sendData(packet)
                        time.sleep(0.1)
                        passedP-=1
                    else:
                        STATE ='ERROR'
                        print('ERROR: headerSize is not the same as payload...retrying')
                        head = setHeader(2,0,0,0)
                        eop = setEOP()
                        packet = head +eop
                        time.sleep(0.1)
                        com1.sendData(packet)
                        time.sleep(0.1)
                        passedP-=1
               
                elif currPacket>=nOfPackets:
                    print('Last packet received')
                    img += rxBefore

                    head = setHeader(4,0,0,0)
                    eop = setEOP()
                    packet = head + eop
                    com1.sendData(packet)


                    print('Beggining to write to IMG')
                    file = open('./receivedImg.jpg', 'wb')
                    file.write(img)
                    file.close()
                    print('Ended IMG writing')
                    
                    listening = False
                    STATE ='END'
                else:
                    print(currPacket, nOfPackets)
                    print('Pacote recebido!')
                    img += rxBefore
                    head = setHeader(4,0,0,0)
                    eop = setEOP()
                    packet= head + eop
                    com1.sendData(packet)

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno

        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
    
        com1.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()