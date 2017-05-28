#Libraries
import smbus
import math
import time
import serial
import socket 
import vlc

#Initiliazation of I2C bus
bus = smbus.SMBus(1)
address = 0x68       # Sensor I2C address
address_mag = 0x0c   #Sensor address for magnetometer

# Register address from MPU 9255 register map
power_mgmt_1 = 0x6b
usr_cntrl = 0x6a
int_pin_conf = 0x37
cntrl = 0x0a
mag_xout_h = 0x03
mag_yout_h = 0x05
mag_zout_h = 0x07
gyro_config = 0x1b
gyro_xout_h = 0x43
gyro_yout_h = 0x45
gyro_zout_h = 0x47
accel_config = 0x1c
accel_xout_h = 0x3b
accel_yout_h = 0x3d
accel_zout_h = 0x3f

# Setting power register to start getting sesnor data
bus.write_byte_data(address, power_mgmt_1, 0)

# Setting Acceleration register to set the sensitivity
# 0,8,16 and 24 for 16384,8192,4096 and 2048 sensitivity respectively
bus.write_byte_data(address, accel_config, 24)

# Setting gyroscope register to set the sensitivity
# 0,8,16 and 24 for 131,65.5,32.8 and 16.4 sensitivity respectively
bus.write_byte_data(address, gyro_config, 24)

#Function to read byte and word and then convert 2's compliment data to integer
def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def read_word_mag(address, adr):
    low = read_byte(address, adr)
    high = read_byte(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c_mag(address, adr):
    val = read_word_mag(address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

oldXAccel=0
oldYAccel=0
oldzAccel=0
oldgyroX=0
oldgyroy=0
oldgyroz=0
rockethaslaunched=False
timeTheRocketLaunched=0

#Debugging Variables
showGyro=False
showAccelerometer=True
sendDataToServer=True

TCP_IP = '192.168.100.3' #ip of raspberry pi
TCP_PORT = 87 #random number on the ip where we talk
BUFFER_SIZE = 1024 #Number of bytes of data we receive at a time
        
host = TCP_IP
port = TCP_PORT               


def magnitude(x,y,z):
	return math.sqrt(x*x+y*y+z*z)
	
def recordAndSendMessage(message):
	if(timeTheRocketLaunched!=0):
		message=str(time.time()-timeTheRocketLaunched)+": "+message
	print message
	fromServer="nothing"
	if(sendDataToServer):
            s = socket.socket()
            try:
                with open('clientdata.txt','a+') as f: #open data file to write
                    f.write(message) #write shit to our file
                    f.write("From server:" + fromServer)
                #print "connecting to server"
		s.settimeout(.2)
		s.connect((host, port))
		#print "connected sending message"
		s.send(message)
		#print "sent message receiving message"
		#fromServer=s.recv(1024)
		#print "received from server 1"
		#fromServer=s.recv(1024)
		#print "received from server 2. Closing connection"
		s.close()
            except:
                s.close()
                print "Timeout"
                
if(not sendDataToServer):
    "Not sending to server because boolean is false"
recordAndSendMessage("Client Initialized...Trying to read from accelerometer")

while 1:
	
	accel_xout = read_word_2c(accel_xout_h) #We just need to put H byte address
	accel_yout = read_word_2c(accel_yout_h) #as we are reading the word data
	accel_zout = read_word_2c(accel_zout_h)

	accel_xout_scaled = accel_xout / 2048.0 #According to the sensitivity you set
	accel_yout_scaled = accel_yout / 2048.0
	accel_zout_scaled = accel_zout / 2048.0
	if ((accel_xout_scaled>1.5 or accel_yout_scaled>1.5 or accel_zout_scaled>1.5) and (accel_xout_scaled!=oldXAccel or accel_yout_scaled!=oldYAccel or accel_zout_scaled!=oldzAccel) and showAccelerometer):
		recordAndSendMessage("Raw and Scaled Accelerometer data\n")
		mag=magnitude(accel_xout_scaled,accel_yout_scaled,accel_zout_scaled)
		if(mag>5 and not rockethaslaunched):
			rockethaslaunched=True
			p = vlc.MediaPlayer("R2_screaming.mp3")
			p.play()
			timeTheRocketLaunched=time.time()
			time.clock()
		if(mag<=5 and rockethaslaunched):
			recordAndSendMessage("enabling stage transition\n")
		recordAndSendMessage("X>\t Raw: "+ str(accel_xout)+ "\t Scaled: "+ str(accel_xout_scaled)+"\n")
		recordAndSendMessage("Y>\t Raw: "+ str(accel_yout)+ "\t Scaled: "+ str(accel_yout_scaled)+"\n")
		recordAndSendMessage("Z>\t Raw: "+ str(accel_zout)+ "\t Scaled: "+ str(accel_zout_scaled)+"\n")
		recordAndSendMessage("Magnitude:"+ str(mag) +"\n")
		oldXAccel=accel_xout_scaled
		oldYAccel=accel_yout_scaled
		oldzAccel=accel_zout_scaled
	
	gyro_xout = read_word_2c(gyro_xout_h) #We just need to put H byte address
	gyro_yout = read_word_2c(gyro_yout_h) #as we are reading the word data
	gyro_zout = read_word_2c(gyro_zout_h)

	gyro_xout_scaled = gyro_xout / 16.4 #According to the sensitivity you set
	gyro_yout_scaled = gyro_yout / 16.4
	gyro_zout_scaled = gyro_zout / 16.4
	
	if((gyro_xout_scaled-oldgyroX>16 or gyro_yout_scaled-oldgyroy>16 or gyro_zout_scaled-oldgyroz>16) and showGyro):
		recordAndSendMessage("Raw and Scaled Gyro data\n")
		recordAndSendMessage("X>\t Raw: "+ str(gyro_xout) + "\t Scaled: "+ str(gyro_xout_scaled)+"\n")
		recordAndSendMessage("Y>\t Raw: "+ str(gyro_yout)+ "\t Scaled: "+ str(gyro_yout_scaled)+"\n")
		recordAndSendMessage("Z>\t Raw: "+ str(gyro_zout)+ "\t Scaled: "+ str(gyro_zout_scaled)+"\n")
		oldgyroX=gyro_xout_scaled
		oldgyroy=gyro_yout_scaled
		oldgyroz=gyro_zout_scaled
	
	time.sleep(0.03)
