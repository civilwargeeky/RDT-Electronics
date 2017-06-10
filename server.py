import socket #brings in python code for wifi communication
import serial #brings in python code for connecting to external devices like the accelerometer
import time #brings in python code for timers, stopwatches, sleepers etc.
import sys #brings in python code to discover information about the hardware on the currently running system.
import math #brings in python code for functions like square root, power, etc.

TCP_IP = '192.168.100.2' #ip of this raspberry pi (the server). Tell the client this is where to connect to.
TCP_PORT = 88 #random number on the ip where we talk. Tell the client this is where to connect to.
BUFFER_SIZE = 1024 #Number of bytes of data we receive at a time

from GPS import * #brings in python code for reading from the GPS module.
from BerryImu import * #brings in berryimu code for accelerometer and magnetometer

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant
sendDataOverXbee=False

def sendCharactersEveryTenthOfASecond( msg ): #python is able to send things faster than the antenna can, here we slow python down so it's only sending a character every .007 seconds
  #return;
  msg=msg+"\r\n"
  print(msg) #in addition to sending the data over antenna we will print it to the console
  #and write it to a file...
  with open('data.txt','a+') as f: #open data file to write
      f.write(msg) #write to our file
  if sendDataOverXbee:
    with serial.Serial() as ser: #initiate the serial functions we imported in the header in a variable called ser
      ser.baudrate = 9600 #set the transfer rate (baud) of data to 9600
      ser.port = '/dev/ttyUSB0' #transfer the data through the USB port
      ser.open() #open the connection to the device on the other side of the USB
      for c in msg: #break the string up into characters. One at a time call them c
        ser.write(bytes(c, 'utf-8')) #write the character through the serial connection. Encode it as utf-8
        time.sleep(.007) #sleep for .007 seconds so we don't send data too fast

#do GPS Initialization
sendCharactersEveryTenthOfASecond("Initializing GPS...");    #Tell everyone gps is starting
jr = GPS() #initialize the gps from the import we did as a variable called jr
bimu=BerryImu() #initialize the imu from the import we did as a variable called bimu
sendCharactersEveryTenthOfASecond("...GPS Initialized successfully!"); #YAY IT WORKED

#do lastSaid Initialization
lastSaid="random"  #to make sure we aren't sending a bunch of repetitive data, keep track of what was last said. Since nothings been said so far we just assign it "random"

#Do server Initialization
sendCharactersEveryTenthOfASecond("Initializing Server..."); #Tell everyone server is starting
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #sets up socket configuration->Stream of data is nice
s.bind((TCP_IP, TCP_PORT)) #communication can now happen at the host ip/port
s.listen(5) #Wait for clients--> max of 5 connections
sendCharactersEveryTenthOfASecond("...Server initialized successfully!"); #YAY IT Worked!
count=0
#Basically the main method.
while True: #Loop forever waiting for stuff to happen
  
  try: #try-catch is used in case of errors. The program will keep running even if there is an error at some point
    if count%3000==0:
      sendCharactersEveryTenthOfASecond(repr(jr.getLocation())+'\n')
      #take the opportunity to log the BerryImus data as well.
      ACCx = bimu.readACCx()
      ACCy = bimu.readACCy()
      ACCz = bimu.readACCz()
      GYRx = bimu.readGYRx()
      GYRy = bimu.readGYRy()
      GYRz = bimu.readGYRz()
      MAGx = bimu.readMAGx()
      MAGy = bimu.readMAGy()
      MAGz = bimu.readMAGz()
      pressTemp=bimu.getTempAndPressure();
      mag=math.sqrt(((ACCx * 0.224)/1000)* ((ACCx * 0.224)/1000)+((ACCy * 0.224)/1000)*((ACCy * 0.224)/1000)+((ACCz * 0.224)/1000)*((ACCz * 0.224)/1000))
      sendCharactersEveryTenthOfASecond("BIMU acc mag: "+str(mag)+" gx: "+str(GYRx)+" gy: "+str(GYRy)+" gz: "+str(GYRz)+" mx:"+str(MAGx)+" my: "+str(MAGy)+" mz: "+str(MAGz)+str(pressTemp));
      count=1
    newLocation = jr.getLocation()
    if lastSaid != newLocation: #if the gps location is different from last time
      lastSaid = newLocation #replace the variable keeping track of the last location
      print(lastSaid)
      sendCharactersEveryTenthOfASecond(repr(lastSaid)); print("Done") #send location over antenna
    #sendCharactersEveryTenthOfASecond("OutOfGps")
    c, addr = s.accept() #Try to accept a server connection...Accept whoever idc...
    #sendCharactersEveryTenthOfASecond('Got connection from'+ str(addr)) #Let the ground know we've made contact
    data = c.recv(BUFFER_SIZE) #receive some of data from other guy
    if data: #if the data they sent us is not bs
      sendCharactersEveryTenthOfASecond(data.decode("utf-8")+'\n') #send over the antenna
      sendCharactersEveryTenthOfASecond(jr.getLocation()+'\n')
      #take the opportunity to log the BerryImus data as well.
      ACCx = bimu.readACCx()
      ACCy = bimu.readACCy()
      ACCz = bimu.readACCz()
      GYRx = bimu.readGYRx()
      GYRy = bimu.readGYRy()
      GYRz = bimu.readGYRz()
      MAGx = bimu.readMAGx()
      MAGy = bimu.readMAGy()
      MAGz = bimu.readMAGz()
      pressTemp=bimu.getTempAndPressure();
      mag=math.sqrt(((ACCx * 0.224)/1000)* ((ACCx * 0.224)/1000)+((ACCy * 0.224)/1000)*((ACCy * 0.224)/1000)+((ACCz * 0.224)/1000)*((ACCz * 0.224)/1000))
      sendCharactersEveryTenthOfASecond("BIMU acc mag: "+str(mag)+" gx: "+str(GYRx)+" gy: "+str(GYRy)+" gz: "+str(GYRz)+" mx:"+str(MAGx)+" my: "+str(MAGy)+" mz: "+str(MAGz)+str(pressTemp));
    c.close() #Close connection--> See ya later bro
    count=count+1
  #except Exception as e: # if an error is thrown execute this block of code
  #  sendCharactersEveryTenthOfASecond("Had an error:"+str(type(e)) + " " + str(e)) #try to send ground any error we get
  #  pass
  except KeyboardInterrupt:
                s.close()
                
s.close()
