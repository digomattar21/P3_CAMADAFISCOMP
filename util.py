imagem = "imagem.jpg"
txBuffer = open(imagem, 'rb').read()
txLen = len(txBuffer)
ratio = round(txLen/114) 


def setHeader(arg1,arg2,arg3,arg4):
    un0 = (255).to_bytes(1,byteorder="big") 
    un1 = (arg1).to_bytes(1,byteorder="big") 
    un2 = (arg2).to_bytes(1,byteorder="big") 
    un3 = (arg3).to_bytes(1,byteorder="big") 
    un4 = (arg4).to_bytes(1,byteorder="big") 
    un5 = (0).to_bytes(1,byteorder="big")
    un6 = (0).to_bytes(1,byteorder="big")
    un7 = (0).to_bytes(1,byteorder="big")
    un8 = (0).to_bytes(1,byteorder="big")
    un9 = (0).to_bytes(1,byteorder="big")
    

    header = un0 + un1 + un2  + un3 + un4 + un5 + un6 + un7 + un8 + un9
    return header
    
    
def setEOP():
    return (0).to_bytes(4,byteorder="big")

