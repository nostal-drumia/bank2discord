import json
import os
import requests
import joblib
import re
import argparse
import logging as log
from discord_webhook import DiscordWebhook, DiscordEmbed
from slpp import slpp as lua

def main():
  init = setup()
  log.info("init.path=%s" % init['path'])
  log.info("init.data=%s" % init['data'])
  dp = init["data"]
  if os.path.isfile(dp):
    if os.stat(dp).st_size != 0:
      f = open(dp, 'r')
      m = str()
      for l in f:
        m+=l
      messages = json.loads(m.replace('\'', '\"'))
      for message in messages:
        deleteWebhookMessage(message['webhook'], message['id'])
      os.remove(dp)
      exit(code=8)
  else:
    open(dp, 'a').close()

  discord_messages = list()

  b = bagnonInventory(init['path'], init['server'], init['character'])
  items = list()
  for inventory in b.inventory:
    item = wowDb(inventory['id'], inventory['count'])
    log.debug("json = %s" % str(item.item))
    items.append(item)

  for item in items:
    log.info("type : %s", item.getItemType())
    if str((item.getItemType())['name']).upper() == "WEAPON" and init["webhook_weapon"]:
      webhook_url = init['webhook_weapon']
    elif str((item.getItemType())['name']).upper() == "ARMOR" and init["webhook_armor"]:
      webhook_url = init['webhook_armor']
    elif str((item.getItemType())['name']).upper() == "RECIPE" and init["webhook_recipe"]:
      webhook_url = init['webhook_recipe']
    else:
      webhook_url = init['webhook_other']
    
    r = sendWebhookMessage(webhook_url, item)
    message = dict(webhook = webhook_url, id = r)
    discord_messages.append(message)
    f = open(dp, 'w')
    f.write(str(discord_messages))
    f.close()
    log.info("webhook result=%s" % r)

class bagnonInventory:
  def __init__(self, path, server, character, pattern = r'([0-9]+\:){3}[0-9]+\,[0-9]*'):
    self.path = path
    self.pattern = pattern
    self.server = server
    self.character = character
    self.inventory = list()
    
    try:
      f = open(self.path, "r")
    except:
      log.critical("Can't open BAGNON lua file")
      exit(1)

    content = lua.decode("{" + (f.read()).replace("\n", '') + "}")
    inventory = ((content.get("BagnonDB")).get(server)).get(character)
    
    for bag in inventory.values():
      if type(bag) is dict:
        for entry in bag.values():
          if re.search(self.pattern, entry):
            self.inventory.append({'id':entry.split(':')[0], 'count':(entry.split(',')[1] or 1)})

class wowDb:
  def __init__(self, id, count):
    self.wowdb = "https://api.wowclassicdb.com/item/"
    self.iconURL = "https://cdn.wowclassicdb.com/icons/"
    self.url = self.wowdb + id
    self.count = count
    r = requests.get(self.url)
    self.item = json.loads(r.content.decode('utf8'))
  
  def show(self):
    print(json.dumps(self.item, indent=2))

  def getId(self):
    log.debug("id=%s" % self.item.get("id"))
    return self.item.get("id")
  
  def getCount(self):
    log.debug("Count=%s" % self.count)
    return self.count
  
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
      return round((self.item.get("weaponSpeed")*0.001), 2)
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
    if self.item['itemType'] is not None:
      return self.item['itemType']
    else:
      return None

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
    return str(self.iconURL + (self.getIcon()).get('name')) + ".jpg"
  
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

def sendWebhookMessage(url: str, item: wowDb):

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
  u = "https://www.wowhead.com/classic/fr/item=" + str(item.getId())
  embed.set_url(url = u)
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
    
  if item.getWeaponSpeed() is not None and float(item.getWeaponSpeed()) > 0:
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
    if len(se) == len(st) and st is not None:
      for i in range(len(se)):
        if i == 0:
          r += st[i].get("name") + " : " + se[i].get("description")
        else:
          r += "\n" + st[i].get("name") + " : " + se[i].get("description")
    elif len(se) > len(st) and len(st) == 1 and st is not None:
      for i in range(len(se)):
        if i == 0:
          r += st[0].get("name") + " : " + se[i].get("description")
        else:
          r += "\n" + st[0].get("name") + " : " + se[i].get("description")
    elif len(se) > len(st) and len(st) > 1 and st is not None:
      if i < (len(se)-1):
        if i == 0:
          r += st[0].get("name") + " : " + se[i].get("description")
      else:
        r += "\n" + st[1].get("name") + " : " + se[i].get("description")
    elif st is None:
      r += se[i].get("description")
    embed.add_embed_field(name = "SpellEffects", value = r, inline=True)
  resist = ""
  if item.getResistanceArcane() is not None and item.getResistanceArcane()>0:
    if resist == "":
      resist += "+" + str(item.getResistanceArcane()) + " Arcane"
    else:
      resist += "\n+" + str(item.getResistanceArcane()) + " Arcane"
  if item.getResistanceFire() is not None and item.getResistanceFire() > 0:
    if resist == "":
      resist += "+" + str(item.getResistanceFire()) + " Fire"
    else:
      resist += "\n+" + str(item.getResistanceFire()) + " Fire"
  if item.getResistanceHoly() is not None and item.getResistanceHoly() > 0:
    if resist == "":
      resist += "+" + str(item.getResistanceHoly()) + " Holy"
    else:
      resist += "\n+" + str(item.getResistanceHoly()) + " Holy"
  if item.getResistanceNature() is not None and item.getResistanceNature() > 0:
    if resist == "":
      resist += "+" + str(item.getResistanceNature()) + " Nature"
    else:
      resist += "\n+" + str(item.getResistanceNature()) + " Nature"
  if item.getResistanceShadow() is not None and item.getResistanceShadow() > 0:
    if resist == "":
      resist += "+" + str(item.getResistanceShadow()) + " Shadow"
    else:
      resist += "\n+" + str(item.getResistanceShadow()) + " Shadow"
  if resist != "":
    embed.add_embed_field(name = "Resitance", value = resist, inline = False )
  if int(item.getCount()) > 1 :
    embed.add_embed_field(name = "Count", value = str(item.getCount()))
  

  webhook.add_embed(embed)
  webhook.embeds
  log.debug("DEBUG: discord webhook embeds %s" %webhook.embeds)
  response = webhook.execute()
  log.debug("DEBUG: discord webhook %s" % str(response))
  return webhook.id

def deleteWebhookMessage(url: str, id: str):
  webhook = DiscordWebhook(url = url, id = id, rate_limit_retry=True)
  webhook.delete()

def setup():

  parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='''Bagnon to discord''')
  parser.add_argument('-b', metavar='bagnon', help='Path to file of Bagnon Inventory')
  parser.add_argument('-c', metavar='character', help='character to push inventory')
  parser.add_argument('-s', metavar='server', help='name of server in Bagnon Inventory')
  parser.add_argument('--weapon', metavar='webhook_weapon', help='Discord WebHook URL for Weapon')
  parser.add_argument('--armor', metavar='webhook_armor', help='Discord WebHook URL for Armor')
  parser.add_argument('--other', metavar='webhook_other', help='Discord WebHook URL for Armor')
  parser.add_argument('--recipe', metavar='webhook_receipe', help='Discord WebHook URL for Receipe')
  parser.add_argument('-v', action='store_true', help='verbose mode')

  args = parser.parse_args()

  if args.v:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
  else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)

  
  log.debug("START")
  try: 
    path = args.b
    server = args.s
    character = args.c
    webhook_weapon = args.weapon
    webhook_armor = args.armor
    webhook_recipe = args.recipe
    webhook_other = args.other


    
    log.debug(vars(args))
    # if args.all[0] is not None:
    if webhook_recipe is None or webhook_armor is None or webhook_weapon is None or webhook_other is None:
      log.error("If you don't set -a argument you need to set four other")
      exit(code= 2)
    # else:
    #   log.info("none")
    #   webhook_all = args.all[0]
  except:
    log.error("All required have not been set")
    log.error(vars(args))
    exit(code = 2)
  
  data = ".data/discord-" + str(server).replace(' ', '') + "-" + character
  log.debug("DATA %s", data)

  return({"path": path, "data": data, "server": server, "character": character, "webhook_weapon": webhook_weapon, "webhook_armor": webhook_armor, "webhook_recipe": webhook_recipe, "webhook_other": webhook_other})

if __name__ == "__main__":
  main()
