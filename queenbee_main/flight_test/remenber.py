from queenbee.bee import Bee
import asyncio
from omegaconf import OmegaConf
from tqdm import tqdm
import sys

SYSTEM_ADDRESS="serial:///dev/ttyACM0:115200"

async def main_run():
    with open("./config/matsudo_config.yaml", mode = "r") as f:
        conf1 = OmegaConf.load(f)
    print("current config file: ")
    print(OmegaConf.to_yaml(conf1))

    while True:
        flag = int(input("start: 1, finish: 0  "))
        if flag == 0 or flag == 1:
            break
        print("Error :input 0 or 1")

    if not flag:
        print("-- finish program")
        sys.exit()

    while flag:
        counter = 0
        latlst = []
        lonlst = []
        print(f"\nnum_satellites:{drone.num_satellites}")
        print("-- get position start")
        pbar = tqdm(total=10)
        while counter < 10:
            await asyncio.sleep(1)
            latitude = drone.Latitude_deg
            longitude = drone.Longitude_deg
            if latitude == 0.0 and longitude == 0.0:
                continue
            latlst.append(latitude)
            lonlst.append(longitude)            
            pbar.update()
            counter += 1
        pbar.close()

        lat = sum(latlst)/len(latlst)
        lon = sum(lonlst)/len(lonlst)

        posdict = {"latitude": lat, "longitude": lon}    
        print(f"\n-- position is {posdict}")

        while True:
            flag = int(input("try again: 1 , save: 0  "))
            if flag == 0 or flag == 1:
                break
            print("Error: input 0 or 1")
            
    target = input("set point name :")
    dict_conf = {target:posdict}
    conf2 = OmegaConf.create(dict_conf)
    print("\nconfig file change point : ")
    print(OmegaConf.to_yaml(conf2))
            
    print("current config file: ")
    print(OmegaConf.to_yaml(conf1))

    while True:    
        mergeflag = input("Do you merge files? [yes/no]")
        if mergeflag == "yes":
            conf = OmegaConf.merge(conf1, conf2)
            print("config file after merge: ")
            print(OmegaConf.to_yaml(conf))
            OmegaConf.save(conf,"./config/matsudo_config.yaml")
            exit()
        elif mergeflag == "no" :
            print("remove changes")
            exit()
        else :
            print("Error: input yes or no")
            
        
async def main():
     await drone.Connect(system_address=SYSTEM_ADDRESS)
     await drone.Catch_GPS()
     main_coroutines = [ 
           drone.Loop_position(),
           drone.Loop_gpsinfo(),
           main_run()
      ]
     await asyncio.gather(*main_coroutines)


if __name__ == "__main__":
     drone = Bee()
     asyncio.run(main())