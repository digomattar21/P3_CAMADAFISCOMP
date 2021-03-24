import sys
from enlace import *
import time
from util import setHeader, setEOP
import math

serialPort = "/dev/ttyACM0"           # Ubuntu
# serialName = "/dev/tty.usbmodem1463201"  # Mac
#serialName = "COM2"


def main():
    try:
        com = enlace(serialPort)
        com.enable()

        print('Comunicacao ativa, iniciando envio de pacotes')

        STATE = "INIT"
        init = True
        count = 0

        while init:
            if STATE == "INIT":
                head = setHeader(1, 0, 0, 0)
                eop = setEOP()
                packet = head + eop
                com.rx.clearBuffer()
                com.sendData(packet)
                time.sleep(0.1)
                print('Preparando envio de handshake')
                STATE = 'HANDSHAKE'
            if STATE == "HANDSHAKE":
                recon = True
                timer1 = time.time()
                while recon:
                    bufferLen = com.tx.getBufferLen()
                    if bufferLen == 14:
                        STATE = "PREFLIGHTCHECKOK"
                        print('Checking server status... OK')
                        recon = False
                    timer2 = time.time()
                    deltaT = timer2 - timer1
                    print('Elapsed Time: {0}'.format(deltaT))
                    if deltaT > 5:
                        tryAgain = False
                        tentarNovamente = input(
                            'Server is not responding, try again (S/N)?')
                        if (tentarNovamente == 'S'):
                            tryAgain = True
                            head = setHeader(1, 0, 0, 0)
                            eop = setEOP()
                            packet = head + eop
                            com.sendData(packet)
                            print('Preparando envio de handshake')
                            STATE = 'HANDSHAKE'
                        else:
                            print('Server Crashed, ending...')
                            break

            if STATE == "PREFLIGHTCHECKOK":

                imagem = './imagem.jpg'
                txBuffer = open(imagem, 'rb').read()
                time.sleep(0.1)
                txLen = len(txBuffer)
                if txLen % 114 == 0:
                    ratio = math.floor(txLen/114)
                else:
                    ratio = math.floor(txLen/114) + 1
                cPacket = 1
                count = 0
                print("TxLen: {0}".format(txLen))

                while txLen > 0:  
                    if txLen >= 114:
                        # definindo o header da imagem a ser transmitida
                        head = setHeader(0, ratio, cPacket, 114)
                        nextP = count + 114
                        payload = txBuffer[count:nextP]
                        eop = setEOP()
                        packet = head + payload + eop
                        

                        com.sendData(packet)
                        time.sleep(0.01)  # envio dos dados da imagem
                        cPacket += 1
                        count += 114
                        txLen -= 114

                        print('Packet with length {0} sent, waiting for response'.format(
                            len(packet)))
                        
                        time.sleep(0.01)
                        rxBuffer, nRx = com.getData(14)
                        if rxBuffer[1] == 4:
                            print(
                                'Packet was delivered and read, sending next packet')
                        elif rxBuffer[1] == 2:
                            cPacket -= 1
                            count -= 114
                            txLen += 114
                        elif rxBuffer[1] == 5:
                            cPacket -= 2
                            count -= 114*2
                            txLen += 114*2
                        print('Bytes left: {0}'.format(txLen))
                        print('N Packet: {0}'.format(cPacket))
                        print('Ratio: {0}'.format(ratio))
                        

                    else:
                        head = setHeader(0, ratio, cPacket, txLen)
                        print('txLen: {0}'.format(txLen))
                        payload = txBuffer[count:txLen]
                        eop = setEOP()
                        packet = head + eop
                        com.sendData(packet)
                        print('Last packet sent')
                        time.sleep(0.02)

                        cPacket += 1
                        count += 114
                        txLen -= 114
                        init = False
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("ERRO: {}".format(e))
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)

        com.disable()


    # so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
