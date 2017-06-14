from serial import Serial
from time import sleep

lastLetter = "\n"
testString = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,./<>?;':\"[]{}-=_+!@#$%^&*()"

rec = None
for port in ["COM" + str(i) for i in range(2, 10)] + ["/dev/ttyUSB0"]:
  try:
    rec = Serial(port)
    print("Connecting on serial port",repr(port))
    break
  except OSError:
    pass
    
if not rec:
  raise RuntimeError("Could not connect to antenna port")

lowerBound = 0.00001
upperBound = 0.001
qualityCutoff = 98
iterations = 5
repeats = 10

# while True:
  # for time in [0.02]:
    # print("Time:",time)
    # for i in range(iterations):
      # print("Iter:",i)
      # for char in testString:
        # rec.write(bytes(char,"utf-8"))
        # sleep(time)
      # sleep(0.2)
      # rec.write(bytes(lastLetter,"utf-8"))
      # sleep(0.2)

print("Starting send")
try:
  for i in range(iterations): #Do 20 iterations of testing\
    percents = []
    testBound = (upperBound + lowerBound) / 2 #Midway between them
    print("Sending with delay",round(testBound,5),"  Upper:",round(upperBound,5),"Lower:",round(lowerBound,5))
    for j in range(repeats):
      print("Iter",j+1,": ",end = " ")
      for char in testString:
        rec.write(bytes(char,"utf-8"))
        sleep(testBound)
      sleep(0.5)
      rec.write(bytes(lastLetter,"utf-8"))
      data = rec.readline()
      perc = (int(data.decode("utf-8","ignore").rstrip()))
      if perc: 
        percents.append(perc) #Get number without newline
        print(percents[-1])
      else:
        print("Invalid Data")
    #So if we have acceptable quality, we lower the upper bound so testBound will be lower
    #  otherwise, we raise the lowerBound so testBound will be higher
    avg = sum(percents)/len(percents)
    print("Average Percent:",round(avg,2))
    if avg > qualityCutoff:
      upperBound = testBound
    else:
      lowerBound = testBound
  print("Final sleep time:",testBound)
finally:
  rec.close()
