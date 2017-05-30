#This module is a test for the GPS module to determine how long it takes to acquire a fix
#It will test if it has a fix every minute, once it has a fix it will make sure it maintains that fix for 10 minutes, then turn off and on again to reacquire fix

import csv, time

#Times for various actions, in seconds
TIME_FIX_INT      = 60 #Time interval between tests for a fix
TIME_FIX_HOLD     = 60 * 10 #Time to make sure it has a fix
TIME_FIX_HOLD_INT = 20 #Time interval for making sure it has a fix
TIME_OFF          = 60 #Time that GPS will be disabled

#This array will hold all results from testing
#Results are stored as a tuple of
# 0) time to acquire fix (in seconds)
# 1) timestamp fix was acquired
# 2) time fix was held (in seconds)
data = []

def getHourMinuteString(timestamp):
  return "{:2}h{:02}m".format(int(timestamp//60**2),int(timestamp%60**2//60))

#Takes a timestamp from time.time() and turns it into a human readable date-time
#PRE: An integer time since UNIX Epoch. Like from time.time()
#POST: A time in the format "Day Month DD, HH:MM AM/PM". Length 16
def getTimeString(timestamp):
  return time.strftime("%b %d, %I:%M %p", time.gmtime(timestamp))

def getFixString(fixTuple):
  timeString = getHourMinuteString(fixTuple[0])
  #        to match scoreboard       len 6              16              3  = 25
  return "{:^11}{:^16}{:^12}".format(timeString, getTimeString(fixTuple[1]), "{:2}m".format(int(fixTuple[2]//60)))

def printScoreboard():
  DISP_NUM = 5
  timesCopy = data[:] #We don't want to pop from main data table
  timesCopy.sort() #By default sorts them by the first element of tuple
  #We make strings for each time in best and worse
  bestScores = [getFixString(i) for i in timesCopy[:DISP_NUM]] #lowest
  bestScores += [""] * (DISP_NUM - len(bestScores)) #Pad length to number of entries
  timesCopy = timesCopy[DISP_NUM:] #Pop those elements
  worstScores = [getFixString(i) for i in timesCopy[-DISP_NUM:]] #Now last
  worstScores += [""] * (DISP_NUM - len(worstScores))
  
  lrFormat = "{:^39}|{:^39}" #String for left and right formatting
  scoreString = "{:^11}{:^16}{:^12}".format("Time To Fix","Acquired On","Held For") #Just the headers
  print("-"*79)
  print(lrFormat.format("Best Times","Worst Times"))
  print(lrFormat.format(scoreString, scoreString))
  print("{0:-^39}|{0:-^39}".format(""))
  for i in range(DISP_NUM):
    print(lrFormat.format(bestScores[i], worstScores[i]))
  print("-"*79)
  
  avgTime = sum([i[0] for i in data]) / (len(data) or 1) #Sum of all the times to fix / len
  print("Average Time to Fix: "+getHourMinuteString(avgTime))
  
  with open("GPS_Test_Data.csv","w",newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)
  print("CSV Written")

def main():
  import RPi.GPIO as GPIO
  try:
    from GPSLib import GPS as GPSClass #Import GPS under a different name
  except ImportError: #On the Pi its just called GPS.py
    from GPS import GPS as GPSClass

  #This is for the pin that enables/disables the GPS
  OUTPUT_PIN = 17 #BCM 17 is GPIO 0
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(OUTPUT_PIN, GPIO.OUT, initial = GPIO.LOW)#Clear it to low. Low is GPS active
    
  GPS = GPSClass() #Our main object
  
  try:
    while True:
      #One iteration of testing
      print("Waiting for fix")
      startTime = time.time()
      while not GPS.hasFix():
        time.sleep(TIME_FIX_INT)
      endTime = time.time()
      fixTime = endTime - startTime
      print("Acquired fix in "+getHourMinuteString(fixTime))
      print("Checking fix hold for",getHourMinuteString(TIME_FIX_HOLD))
      while (time.time() - endTime) < TIME_FIX_HOLD: #Do testing for a specified amount of time
        if not GPS.hasFix(): #If we no longer have a fix, we record the amnt of time we had a fix for
          break
        time.sleep(TIME_FIX_HOLD_INT)
      fixHoldTime = time.time() - endTime
      print("Fix held for",getHourMinuteString(fixHoldTime))
      data.append((fixTime, endTime, fixHoldTime)) #Insert the tuple into the table of data
      printScoreboard() # Print out all the nice data, store results
      
      print("Disabling GPS for",getHourMinuteString(TIME_OFF),"(the GPS light should be off, if its not, tell Daniel)")
      GPIO.output(OUTPUT_PIN, GPIO.HIGH)
      time.sleep(TIME_OFF)
      GPIO.output(OUTPUT_PIN, GPIO.LOW)
      print("GPS Re-enabled. GPS light should be blinking")
  finally: #No matter what, fix up ports
    GPIO.cleanup()
  
if __name__ == "__main__":
  from sys import argv
  if len(argv) > 1 and argv[1] == "pin_test":
    import RPi.GPIO as GPIO
    OUTPUT_PIN = 17 #BCM 17 is GPIO 0
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OUTPUT_PIN, GPIO.OUT, initial = GPIO.HIGH)
    print("If the GPS light is still blinking, tell Daniel, otherwise run the program without 'pin_test'")
    print("Press enter when done")
    input()
    GPIO.output(OUTPUT_PIN, GPIO.LOW)
    GPIO.cleanup()
  else:
    main()