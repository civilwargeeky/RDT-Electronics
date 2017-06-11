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

### Asynchronous Antenna Sending Code ###
from threading import Thread, Event #import things for threads
from queue     import Queue, Empty  #import asynchronous queue for thread-safe data transfer. Import "Empty" error

stopSignal = Event() #This will be set when the antenna thread should be ended
charQueue  = Queue() #This is an array of bytes. Bytes are added from sensor data, and removed by the antenna sending them

#The antenna thread
#PRE: serial is the serial port to send data to
def AntennaThread(serial):
  while True:
    try:
      char = charQueue.get(block = True, timeout = 5) #Waits for a new character
      #Do byte sending stuff
      ser.write(bytes(char, "utf-8"))
      time.sleep(0.05)
    except Empty: #Catch exception if there are no bytes at the timeout
      pass
    finally: #Whether we get data or not, make sure we should not be ending
      if stopSignal.is_set()
    
### End Asynchronous Code ###

def sendData( msg, sendOverAntenna = True ): #python is able to send things faster than the antenna can, here we slow python down so it's only sending a character every so often
  msg += "\n" #Add a newline
  print(msg) #in addition to sending the data over antenna we will print it to the console
  #and write it to a file...
  with open('data.txt','a') as f: #open data file to write
      f.write(msg) #write to our file
  if sendDataOverXbee and sendOverAntenna:
    for char in msg:
      charQueue.put(char) #Add each character to our queue. This should always succeed, as we put no limit on the size of our queue
        
#Initialize the Antenna
if sendDataOverXbee:
  sendData("Initializing serial connection and antenna...", sendOverAntenna = False) #Antenna isn't initialized yet!
  ser = serial.Serial() #initiate the serial functions we imported in the header in a variable called ser
  ser.port = '/dev/ttyUSB0' #set to transfer the data through the USB port
  ser.baudrate = 9600 #set the transfer rate (baud) of data to 9600
  ser.open() #open the connection to the device on the other side of the USB
  antennaThread = Thread(target = AntennaThread, args = (ser,)) #Create a new antenna thread, passing in our serial port. This begins waiting for data to be added to our queue
                                                   #Note: ^^ this is a tuple with one value.
#do GPS Initialization
sendData("Initializing GPS...", sendOverAntenna = False);    #Tell everyone gps is starting, don't need to send it over antenna
jr = GPS() #initialize the gps from the import we did as a variable called jr
bimu=BerryImu() #initialize the imu from the import we did as a variable called bimu
sendData("...GPS Initialized successfully!", False); #YAY IT WORKED. Don't need to specify the argument name, don't send over antenna

#do lastSaid Initialization
lastSaid="random"  #to make sure we aren't sending a bunch of repetitive data, keep track of what was last said. Since nothings been said so far we just assign it "random"

#Do server Initialization
sendData("Initializing Server..."); #Tell everyone server is starting
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #sets up socket configuration->Stream of data is nice
s.bind((TCP_IP, TCP_PORT)) #communication can now happen at the host ip/port
s.listen(5) #Wait for clients--> max of 5 connections
sendData("...Server initialized successfully!"); #YAY IT Worked!
count=0
#Literally the main method.
def main():
  while True: #Loop forever waiting for stuff to happen
    try: #try-catch is used in case of errors. The program will keep running even if there is an error at some point
      if count%3000==0:
        sendData(repr(jr.getLocation())+'\n')
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
        sendData("BIMU acc mag: "+str(mag)+" gx: "+str(GYRx)+" gy: "+str(GYRy)+" gz: "+str(GYRz)+" mx:"+str(MAGx)+" my: "+str(MAGy)+" mz: "+str(MAGz)+str(pressTemp));
        count=1
      newLocation = jr.getLocation()
      if lastSaid != newLocation: #if the gps location is different from last time
        lastSaid = newLocation #replace the variable keeping track of the last location
        print(lastSaid)
        sendData(repr(lastSaid)); print("Done") #send location over antenna
      #sendData("OutOfGps")
      c, addr = s.accept() #Try to accept a server connection...Accept whoever idc...
      #sendData('Got connection from'+ str(addr)) #Let the ground know we've made contact
      data = c.recv(BUFFER_SIZE) #receive some of data from other guy
      if data: #if the data they sent us is not bs
        sendData(data.decode("utf-8")+'\n') #send over the antenna
        sendData(jr.getLocation()+'\n')
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
        mag=math.sqrt(((ACCx * 0.224)/1000)**2 +((ACCy * 0.224)/1000)**2 + ((ACCz * 0.224)/1000)**2)
        sendData("BIMU acc mag: "+str(mag)+" gx: "+str(GYRx)+" gy: "+str(GYRy)+" gz: "+str(GYRz)+" mx:"+str(MAGx)+" my: "+str(MAGy)+" mz: "+str(MAGz)+str(pressTemp));
      c.close() #Close connection--> See ya later bro
      count=count+1
    #except Exception as e: # if an error is thrown execute this block of code
    #  sendData("Had an error:"+str(type(e)) + " " + str(e)) #try to send ground any error we get
    #  pass
    except KeyboardInterrupt:
      break


#If this code is not imported as a module, run the main function
if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt: #We allow this error to propogate
    pass
  finally: #No matter what, we want to do these tasks upon program completion
   s.close() #Close the wifi interface
   stopSignal.set() #Tell the antenna to stop waiting for bytes to send