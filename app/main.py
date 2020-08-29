from app.EventMain import DiscordClient
import json

if __name__ == '__main__':
    with open('../secrets/config.json') as config:
        data = json.load(config)
        client = DiscordClient('!!')
        client.run(data['discord']['token'])
