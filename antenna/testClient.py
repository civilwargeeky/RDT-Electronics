from serial import Serial
from time import sleep

lastLetter = "\n"
testString = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,./<>?;':\"[]{}-=_+!@#$%^&*()"

rec = None
for port in ["COM" + str(i) for i in range(1, 10)] + ["/dev/ttyUSB0"]:
  try:
    rec = Serial(port)
    print("Connecting on serial port",repr(port))
    break
  except OSError:
    pass
    
if not rec:
  raise RuntimeError("Could not connect to antenna port")
  
#rec.open()
hits = []
try:
  print(testString)
  while True:
    print("".join(hits))
    hits  = ["X" for i in range(len(testString))]
    got = []
    char = None
    while char != lastLetter:
      data = rec.read()
      if data == b"\xff":
        continue
      try:
        char = data.decode("utf-8") #Read a single byte
        if char in got:
          break
        got.append(char)
        pos = testString.find(char)
        if pos != -1:
          hits[pos] = "."
      except UnicodeDecodeError:
        pass #Invalid byte
    percent = round(hits.count(".")/len(hits)*100)
    print("".join(hits), round(hits.count(".")/len(hits)*100),"%")
    
    for char in (str(percent) + "\n"):
      sleep(0.05)
      print("Sending",repr(char))
      rec.write(bytes(char, "utf-8"))
          
finally:
  rec.close()