
import time
import math

# According to the Dronekit docs:
from dronekit import connect, VehicleMode

# Be careful with relative frames vs absolute frames (mostly WRT altitude)
# https://www.gps-coordinates.net/
# https://www.freemaptools.com/elevation-finder.htm
waypoints = { "grimm_grass_sw_corner": (33.653957, -117.812063, 10),
              "grimm_grass_se_corner": (33.653939, -117.811485, 10),
              "grimm_grass_ne_corner": (33.654386, -117.811511, 10) }

class Pihawk:

    def __init__(self, connection_str='/dev/ttyAMA0', baud=57600):
        self.drone = None
        try:
            print("Attempting to connect to drone at " + connection_str)
            self.drone = connect(connection_str, wait_ready=True, baud=57600)
            print("Battery is at " + str(self.drone.battery))
            self.drone.mode = VehicleMode("GUIDED")
            count = 0
            while self.drone.mode != 'GUIDED':
                print("Waiting for drone to enter GUIDED flight mode... %s" % (count))
                time.sleep(1)
                count += 1
            print("Vehicle now in GUIDED MODE")

        except Exception as e:
            print(f"Error: {str(e)}")
            raise RuntimeError('Cannot connect to drone')

    
    def __del__(self):
        self.close()


    def close(self):
        if self.drone:
            if self.drone.mode != 'LAND':
                self.land()
            if not self.drone.armed:
                self.disarm()
            self.drone.close()


    def arm(self):
        print("Attempting to arm drone")
        count = 0
        while not self.drone.is_armable and count < 15:
            print("Waiting for vehicle to initialize... %s" % (count))
            time.sleep(1)
            count += 1
        if not self.drone.is_armable:
            return self.drone.armed
        print("Vehicle is now armable")
        self.drone.armed = True
        count = 0
        while not self.drone.armed and count < 5:
            print("Waiting for vehicle to arm itself... %s" % (count))
            time.sleep(1)
            count += 1
        print("Drone is now ready")
        return self.drone.armed


    def disarm(self):
        print("Attempting to disarm drone")
        if self.drone == None:
            raise 
        self.drone.armed = False
        count = 0
        while self.drone.armed and count < 10:
            print("Waiting for vehicle to disarm itself... %s" % (count))
            time.sleep(1)
            count += 1
        return self.drone.armed
    

    def takeoff(self, takeoff_height=1):
        print("Attempting to takeoff drone")
        height = 0
        count = 0
        if height > 10:
            print("Capping takeoff height from %sm to 10m" % (takeoff_height))
            takeoff_height = 10
        self.drone.simple_takeoff(takeoff_height)
        timeout = takeoff_height * 5
        while height < 0.95 * takeoff_height and count < timeout:
            height = self.drone.location.global_relative_frame.alt
            print("Drone is now at height %sm... %s" % (height, count))
            time.sleep(1)
            count += 1
        return height


    def land(self):
        print("Attempting to land drone")
        self.drone.mode = VehicleMode("LAND")
        count = 1
        while self.drone.mode != 'LAND' and count < 30:
            print("Waiting for drone to land... %s" % (count))
            time.sleep(1)
            count += 1
        return self.drone.mode
    

    def distance_to(self, target_coordinates):
        # This is a rough calculation that works over small distances but the
        # magic number can be innacurate at different latitudes or over long
        # distances. Use the 'geopy' module for a more reliable conversion.
        lat = target_coordinates.lat - self.drone.location.global_relative_frame.lat
        lon = target_coordinates.lon - self.drone.location.global_relative_frame.lon
        return math.sqrt(lat**2+lon**2) * 111139
    

    def fly_to_coordinates(self, target_coordinates):
        print("[ Flying to coordinates %s ]" % (target_coordinates))
        if self.drone.mode != 'GUIDED':
            self.drone.mode = VehicleMode("GUIDED")
            count = 0
            while self.drone.mode != 'GUIDED':
                print(" ...switching drone to GUIDED mode... %s" % (self.drone.mode, count))
                time.sleep(1)
                count += 1
            if self.drone.mode == 'GUIDED':
                print(" ...drone in GUIDED mode... %s" % (count))
        
        distance = self.distance_to(target_coordinates)
        self.drone.simple_goto(target_coordinates)

        count = 0
        while self.drone.mode == 'GUIDED' and distance > 2:
            distance = self.distance_to(target_coordinates)
            print(" ...waiting for drone to fly to %s (%sm away)... %s" % (self.drone.location.global_relative_frame, distance, count))
            time.sleep(1)
            count += 1
        print(">> Drone flown to coordinates %s (%sm away) <<" % (self.drone.location.global_relative_frame, distance))
        return distance



marty = Pihawk()
marty.arm()
marty.takeoff(1)
print("Takeoff completed, beginning mission in 1s")
time.sleep(1)
marty.fly_to_coordinates(waypoints['grimm_grass_ne_corner'])
print("Mission completed, now landing in 1s")
time.sleep(1)
marty.land()
marty.disarm()
marty.close()
