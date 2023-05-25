# cheatsheet wowclassicdb

## weapon

### generate result for teebu item

```bash
curl -sL https://api.wowclassicdb.com/item/1728 | jq . > teebu.json 
```

### get id

```bash
cat teebu.json | jq .id 
```

### get name

```bash
cat teebu.json | jq .name -r 
```

### get icon

```bash
cat teebu.json | jq "https://cdn.wowclassicdb.com/icons/" + .icon -r
```

### get item level

```bash
cat teebu.json | jq .itemLevel -r 
```

### get required level

```bash
cat teebu.json | jq .requiredLevel -r 
```

### get damage 1

```bash
cat tf.json| jq '(.dmg1Min|tostring) + " - " + (.dmg1Max|tostring)' -r
```

### get damage 2

```bash
cat tf.json| jq '(.dmg2Min|tostring) + " - " + (.dmg2Max|tostring)' -r
```

### get armor

```bash
cat tf.json | jq .armor -r 
```

### get block

```bash
cat tf.json | jq .block -r 
```

### get speed

```bash
cat tf.json | jq '.weaponSpeed/1000' -r 
```
### get resistance

#### resistanceHoly

```bash
cat tf.json | jq '.resistanceHoly' -r 
```
#### resistanceFire

```bash
cat tf.json | jq '.resistanceFire' -r 
```

#### resistanceNature

```bash
cat tf.json | jq '.resistanceNature' -r 
```

#### resistanceFrost

```bash
cat tf.json | jq '.resistanceFrost' -r 
```

#### resistanceShadow

```bash
cat tf.json | jq '.resistanceShadow' -r 
```

#### resistanceShadow

```bash
cat tf.json | jq '.resistanceArcane' -r 
```

#### item type ID

```bash
cat tf.json | jq '.itemTypeId' -r 
```

### item type name

```bash
cat tf.json | jq '.itemType.name' -r
```
