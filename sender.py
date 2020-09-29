from asyncio import run_coroutine_threadsafe, sleep
from codecs import encode
from io import BytesIO
from threading import Thread

from discord import Client

from config import CLOCK_CHANNEL, DATA_CHANNELS, SENDER_TOKEN

buffer = BytesIO()
buffer.seek(0)


class WHGSender(Client):
    def __init__(self, buffer):
        self.buffer = buffer
        super().__init__()

    async def get_channels(self):
        return [await self.fetch_channel(channel_id) for channel_id in DATA_CHANNELS]

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def send_message(self):
        buffer.seek(0)
        channels = await self.get_channels()
        clock = await self.fetch_channel(CLOCK_CHANNEL)
        while byte := buffer.read(1):
            byte = bin(byte[0])[2:]
            for i in zip(byte.zfill(8), channels):
                if i[0] == "1":
                    await i[1].send(content="x")
            await clock.send(content="x")
            await sleep(0.5)
        buffer.truncate(0)
        buffer.seek(0)
        self.sending = False

    def trigger_send(self):
        self.sending = True
        run_coroutine_threadsafe(self.send_message(), client.loop)
        while self.sending:
            pass


def user_input_thread(buffer, client):
    while not client.is_ready():
        pass

    while True:
        message = input("Type message to send: ") + "\x00"
        message = encode(message, "utf-8")
        buffer.write(message)
        client.trigger_send()


client = WHGSender(buffer)
thread = Thread(target=user_input_thread, args=(buffer, client))
thread.daemon = True
thread.start()

client.run(SENDER_TOKEN)
