# haqq_alarm_TG

install  python3
```
sudo apt install python3
```
### Set the required values in the script

###### 1. LOCAL_RPC = "localhost:26657" - RPC of your validator node
###### 2. TRUSTED_API = "https://haqq.api.t.stavr.tech" - Reliable API service
###### 3. VALOPER = "" - Your valoper address
###### 4. ADDRESS = "" - Your key address
###### 5. HEX_ADDRESS = "" - Your Hex Address (you can get this address in popular explorers)
###### 6. CRITICAL_BLOCKS_GAP = 25 - The maximum number of blocks by how much it is permissible to lag behind
###### 7. CRITICAL_PEERS_COUNT = 5 - Critical number of peers
###### 8. UPTIME_WINDOW = 500 - Number of blocks for uptime calculation
###### 9. TELEGRAM_TOKEN = "" - Your telegram token
###### 10 .TELEGRAM_CHAT_ID = "" - Chat id for receiving messages


Run via crontab once every 5 minutes (edit crontab with crontab -e):
*/5  * * * * python3 $HOME/haqq_alarm.py >> $HOME/haqq_alarm.log 2>&1
