from picamera2 import Picamera2
from time import sleep

picam2 = Picamera2()
cprops = picam2.camera_properties
picam2.start(show_preview=True)
print(f"--------------------------------------------------")
print(f"Raspberry Pi Camera '{cprops['Model']}'")
print(f"  Unit Cell Size: {cprops['UnitCellSize'][0]}x{cprops['UnitCellSize'][1]}")
print(f"     Pixel Array: {cprops['PixelArraySize'][0]}x{cprops['PixelArraySize'][1]}")
print(f"        Rotation: {cprops['Rotation']}")
print(f"        Location: {cprops['Location']}")
print(f"--------------------------------------------------")
print(cprops)
print(f"--------------------------------------------------")
sleep(30)
picam2.stop()
picam2.close()
print(f"Done")
