from codecs import decode

from discord import Client

from config import CLOCK_CHANNEL, DATA_CHANNELS, RECEIVER_TOKEN


class WHGReceiver(Client):
    last_ids = None
    string = ""

    async def get_channels(self):
        return [await self.fetch_channel(channel_id) for channel_id in DATA_CHANNELS]

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))
        self.last_ids = [
            channel.last_message_id for channel in await self.get_channels()
        ]

    async def on_message(self, message):
        if message.channel.id == CLOCK_CHANNEL:
            byte = ""
            last_ids = [
                channel.last_message_id for channel in await self.get_channels()
            ]
            for ids in zip(last_ids, self.last_ids):
                if ids[0] == ids[1]:
                    byte += "0"
                else:
                    byte += "1"
            # binary to hex
            byte = hex(int(byte, 2))[2:]
            # hex to utf-8, ensure least 2 places
            byte = decode(byte.zfill(2), "hex")
            # utf-8 to string
            byte = decode(byte, "utf-8")
            if byte == "\x00":
                print(self.string)
                self.string = ""
            else:
                self.string += byte
            self.last_ids = last_ids


client = WHGReceiver()
client.run(RECEIVER_TOKEN)
