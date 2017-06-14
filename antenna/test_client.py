import serial, time

ser = None
for port in ["COM3", "COM4", "/dev/ttyUSB0"]:
  try:
    ser = serial.Serial(port)
    print("Connecting on serial port",repr(port))
    break
  except OSError:
    pass
    
if not ser:
  raise RuntimeError("Could not connect to antenna port")
  
sendString = "".join(chr(i) for i in range(46, 46 + 79))

print(sendString)
while True:
  rec = ["X" for i in range(len(sendString))]
  char = None
  while True:
    char = ser.read().decode("utf-8")
    if char == "\n":
      break
    try:
      rec[sendString.index(char)] = "O"
    except ValueError:
      print("Char not found:",char)
  print("".join(rec))