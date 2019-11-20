import time
cooldowns = {}


async def check(parent, setting, how_long):
    global cooldowns
    try:
        if float(time.time())-float(cooldowns[parent][setting]) > int(how_long):
            cooldowns[parent][setting] = str(time.time())
            return True
        else:
            return None
    except KeyError:
        cooldowns[parent] = {
            setting: str(time.time())
        }
        return True
