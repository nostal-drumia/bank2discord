import json
import requests
import re
import argparse
import logging as log
from discord_webhook import DiscordWebhook, DiscordEmbed

class bagnonInventory:
  def __init__(self, path, pattern = r'([0-9]+\:){3}[0-9]+\,[0-9]*'):
    self.path = path
    self.pattern = pattern
    self.inventory = list()
    try:
      f = open(self.path, "r")
    except:
      log.critical("Can't open BAGNON lua file")
      exit(1)
    for line in f:
      search = re.search(self.pattern, line)
      if search:
        self.inventory.append({'id':(search.group()).split(':')[0], 'count':((search.group()).split(',')[1] or 1)})
  
  def search(self, id):
    for i in self.inventory:
      if i['id'] == str(id):
        return i

class wowDb:
  def __init__(self, id):
    self.wowdb = "https://api.wowclassicdb.com/item/"
    self.iconURL = "https://cdn.wowclassicdb.com/icons/"
    self.url = self.wowdb + id
    r = requests.get(self.url)
    self.item = json.loads(r.content.decode('utf8'))
  
  def show(self):
    print(json.dumps(self.item, indent=2))

  def getId(self):
    log.debug("id=%s" % self.item.get("id"))
    return self.item.get("id")
  
  def getName(self):
    log.debug("name=%s" % self.item.get("name"))
    return self.item.get("name")
  
  def getIcon(self):
    log.debug("icon=%s" % self.item.get("icon"))
    return self.item.get("icon")

  def getItemLevel(self):
    log.debug("itemLevel=%s" % self.item.get("itemLevel"))
    return self.item.get("itemLevel")
  
  def getRequiredLevel(self):
    log.debug("requiredLevel=%s" % self.item.get("requiredLevel"))
    return self.item.get("requiredLevel")
    
  def getDmg1Min(self):
    log.debug("dmg1Min=%s" % self.item.get("dmg1Min"))
    return self.item.get("dmg1Min")

  def getDmg1Max(self):
    log.debug("dmg1Max=%s" % self.item.get("dmg1Max"))
    return self.item.get("dmg1Max")
  
  def getDmg2Min(self):
    log.debug("dmg2Min=%s" % self.item.get("dmg2Min"))
    return self.item.get("dmg2Min")
  
  def getDmg2Max(self):
    log.debug("dmg2Max=%s" % self.item.get("dmg2Max"))
    return self.item.get("dmg2Max")
  
  def getArmor(self):
    log.debug("armor=%s" % self.item.get("armor"))
    return self.item.get("armor")
  
  def getBlock(self):
    log.debug("block=%s" % self.item.get("block"))
    return self.item.get("block")
  
  def getWeaponSpeed(self):
    if self.item.get("weaponSpeed") is not None:
      return round((self.item.get("weaponSpeed")*0.01), 2)
    else:
      return 0
  
  def getResistanceHoly(self):
    log.debug("resistanceHoly=%s" % self.item.get("resistanceHoly"))
    return self.item.get("resistanceHoly")
  
  def getResistanceFire(self):
    log.debug("resistanceFire=%s" % self.item.get("resistanceFire"))
    return self.item.get("resistanceFire")

  def getResistanceNature(self):
    log.debug("resistanceNature=%s" % self.item.get("resistanceNature"))
    return self.item.get("resistanceNature")

  def getResistanceFrost(self):
    log.debug("resistanceFrost=%s" % self.item.get("resistanceFrost"))
    return self.item.get("resistanceFrost")

  def getResistanceShadow(self):
    return self.item['resistanceShadow']
  
  def getResistanceArcane(self):
    return self.item['resistanceArcane']
  
  def getDurability(self):
    return self.item['durability']

  def getItemSubTypeId(self):
    return self.item['itemSubTypeId']
  
  def getItemTypeId(self):
    return self.item['itemTypeId']
  
  def getQualityId(self):
    return self.item['itemQualityId']
  
  def getItemSlotId(self):
    return self.item['itemSlotId']

  def getDmg1Type(self):
    return self.item['dmg1Type']
  
  def getDmg2Type(self):
    return self.item['dmg2Type']

  def getItemSubType(self):
    return self.item['itemSubType']

  def getItemType(self):
    return self.item['itemType']

  def getSpellEffects(self):
    return self.item.get("spellEffects")

  def getSpellTriggers(self):
    return self.item.get("spellTriggers")
  
  def getItemSlot(self):
    return self.item.get("itemSlot")
  
  def getItemQuality(self):
    return self.item.get("itemQuality")

  def getitemsSets(self):
    return self.item.get("itemSets")
  
  def getIconURL(self):
    return str(self.iconURL + self.getIcon()) + ".jpg"
  
  def getStats(self):
    return self.item['stats']
  
  def getStastsDetails(self):
    stats = self.item['stats']
    r = ""
    for stat in stats:
      if r is None:
        r = "+" + str(stat['ItemStats']['value']) + " " + stat['name']
      else:
        r += "\n+" + str(stat['ItemStats']['value']) + " " + stat['name']
    return r


def main():
  init = setup()
  log.debug("init.path=%s" % init['path'])
  

  b = bagnonInventory(init['path'])
  items = list()
  for inventory in b.inventory:
    item = wowDb(inventory['id'])
    log.debug("json = %s" % str(item.item))
    items.append(item)

  

  for item in items:
    r = sendWebhook(init['webhook'], item)
    log.info("webhook result=%s" % r)

def sendWebhook(url: str, item: wowDb):
  webhook = DiscordWebhook(url = url, rate_limit_retry=True)
  log.info("id=%s,Name=%s, color=%s, icon=%s, RequiredLevel=%s",
            item.getId(),
            item.getName(), 
            str(int((item.getItemQuality())['colorCode'], base=16)), 
            item.getIconURL(),
            item.getRequiredLevel()
          )
  embed = DiscordEmbed(title = str(item.getName()), color = int((item.getItemQuality())['colorCode'], base=16))
  embed.set_thumbnail(url = str(item.getIconURL()))
  embed.set_timestamp()
  if item.getRequiredLevel() > 0:
    embed.add_embed_field(name = "Level required", value = str(item.getRequiredLevel()),inline=True)
  if (item.getItemSlot()) != None:
    embed.add_embed_field(name = "Item slot", value = str((item.getItemSlot())['name']),inline=True)
  if (item.getItemSubType()) != None:
    embed.add_embed_field(name = "Type", value = str((item.getItemSubType())['note']) +str((item.getItemSubType())['name']),inline=True)
  if item.getArmor() > 0:
    embed.add_embed_field(name = "Armor", value = str(item.getArmor()),inline=True)
  if item.getBlock() > 0:
    embed.add_embed_field(name = "Block", value = str(item.getBlock()),inline=True)
  if item.getDmg1Min() > 0:
    name = "Damage " + str(item.getDmg1Type()['name'])
    embed.add_embed_field(name = name, value = "+" + str(item.getDmg1Min()) + " - " + str(item.getDmg1Max()),inline=True)
  if item.getWeaponSpeed() is not None or item.getWeaponSpeed() > 0:
    embed.add_embed_field(name = "Speed", value = str(item.getWeaponSpeed()),inline=True)
  if item.getDmg2Min() > 0:
    name = "Damage" + str(item.getDmg2Type()['name'])
    embed.add_embed_field(name = name, value = ("+" + str(item.getDmg2Min()) + " - " + str(item.getDmg2Max())),inline=True)
  if len(item.getStats()) > 0:
    embed.add_embed_field(name = "stats", value = str(item.getStastsDetails()),inline=True)
  if len(item.getSpellEffects()) > 0:
    r = ""
    se = item.getSpellEffects()
    st = item.getSpellTriggers()
    for i in range(len(item.getSpellEffects())):
      if st is not None and st[i] is not None:
        r = st[i].get("name") + " : " + se[i].get("description")
      else:
        r = se[i].get("description")
    embed.add_embed_field(name = "SpellEffects", value = r, inline=True)

  webhook.add_embed(embed)
  webhook.embeds
  log.debug("DEBUG: discord webhook embeds %s" %webhook.embeds)
  response = webhook.execute()
  log.debug("DEBUG: discord webhook %s" % str(response))

def setup():

  parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='''Bagnon to discord''')
  parser.add_argument('-b', metavar='bagnon', nargs=1, help='Path to file of Bagnon Inventory', required=True)
  parser.add_argument('-u', metavar='webook_url', nargs=1, help='Discord WebHook URL', required=True)
  parser.add_argument('-v', action='store_true', help='verbose mode')
  args = parser.parse_args()
  try: 
    path = args.b[0]
    webhook = args.u[0]
    if args.v:
      log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
      log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
  except:
    log.error("All required have not been set")
  return({"path": path, "webhook": webhook})

if __name__ == "__main__":
  main()
