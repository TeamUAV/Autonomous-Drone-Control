from logging import FATAL
from dronekit import connect,VehicleMode
import time
from pymavlink import mavutil
from threading import Thread


vehicle=connect("udp:127.0.0.1:14550",wait_ready=True)

def arm_and_takeoff(altitude):
    print("basic checkup")
    while not vehicle.is_armable:
        print("waiting to initialize")
        time.sleep(1)
    print("arming motors")
    vehicle.mode=VehicleMode("GUIDED")
    vehicle.armed=True

    while not vehicle.armed:
        print("waiting to be armed")
        time.sleep(1)
    print(vehicle.home_location)
    print("taking off")
    vehicle.simple_takeoff(altitude)

    while True:
        print("altitude: {val}".format(val=vehicle.location.global_relative_frame.alt))
        
        if vehicle.location.global_relative_frame.alt>=altitude*0.95:
            print("target altitude reached")
            break
        time.sleep(1)

def send_ned_velocity(x,y,z,duration):
    msg=vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0,0,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0,0,0,
        x,y,z,
        0,0,0,
        0,0
    )
    for i in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)
    return True

class Threader(Thread):
    def __init__(self,north,east,down,time)->None:
        Thread.__init__(self)
        self.north=north
        self.east=east
        self.down=down
        self.time=time
    def run(self) -> None:
        send_ned_velocity(self.north,self.east,self.down,self.time)
        time.sleep(self.time+2.5)

def form_square():
    north=10 #velocity for y axis
    east=10 #velocity for x axis
    down=0 # velcity for z axis
    count=0 # duration for the message to be sent
    time=5
    flag1=False
    flag2=False
    thread=Threader(-north,east,down,time)
    for i in range(4):
        if not flag1 and not flag2:
            thread.start()
            thread.join()
            flag1=True
            thread=Threader(north,east,down,time)
        elif flag1 and not flag2:
            thread.start()
            thread.join()
            flag2=True            
            thread=Threader(north,-east,down,time)
        elif flag1 and flag2:
            thread.start()
            thread.join()
            flag1=flag2=False
            thread=Threader(-north,-east,down,time+1)
        else:
            thread.start()
            thread.join()



def main():
    arm_and_takeoff(50) # taking off to an altitude of 50 m
    form_square()
    vehicle.mode=VehicleMode("RTL") # going back and landing at the home location
if __name__=="__main__":
    main()
    
    