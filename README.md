# HomelabDisplay
public template for displaying code on tft 78x284 of proxmox data

Sorry for the bad coding you might find here.

Idea is:
 - Call the proxmox API via any python capable server (pvestats.py)
 - Aggregate the data (pvestats.py)
 - Publish the data to a mqtt broker (pvestats.py)
 - ESP retreives the data and display it to the tft (ESPHome Homelab Display)
         Note: I was able to do this part with ESPHome code. I can't help if you want to code it directly via the Arduino IDE =(
         Note2: I'll try to get a sketch of the ESP connections with the tft's . as of now, they're mounted on my rack, so a bit hard. i'll see what i can do!
   
