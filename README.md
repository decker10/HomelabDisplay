# HomelabDisplay
public template for displaying code on tft 78x284 of proxmox data

Sorry for the bad coding you might find here.

Idea is:
 - Call the proxmox API via any python capable server (pvestats.py)
 - Aggregate the data (pvestats.py)
 - Publish the data to a mqtt broker (pvestats.py)
 - ESP retreives the data and display it to the tft (ESPHome Homelab Display)
         NOTE: i was able to do this part with ESPHome code. I can't help if you want to code it directly via the Arduino IDE =(
   
