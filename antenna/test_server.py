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
timeout = 0.02

for char in sendString:
  ser.write(bytes(char,"utf-8"))
  time.sleep(timeout)
time.sleep(1)
ser.write(bytes("\n","utf-8"))