# Weenie Hut General

This project is made up of two separate components: the Weenie Hut General Bot and the Weenie Hut General Messaging Protocol (WHGMP).

# Weenie Hut General Bot 

## What is the Weenie Hut General Bot?
Simply, the Weenie Hut General Bot is a Discord bot which transforms a server from a regular server to a server where the only thing which can be sent in the server is a single phrase (ie. "weenie hut general"), and all channel names and nicknames are set to said phrase. After that, it can be reverted back. Through the power of democracy, you can set a message to require a certain amount of reactions before transforming the server. Once the message no longer has enough votes, it will be reverted back to normal.

## How do you set it up?
First, copy config-sample.py to config.py. The `DATA_CHANNEL` and `CLOCK_CHANNEL` variables are only required for WHGMP, so feel free to remove those lines if you do not plan on using WHGMP. Most variables should be self explanatory, however there are a few important ones:

* `VOTE_MESSAGE` and `VOTE_CHANNEL`: The message ID and channel ID of the message which the aformentioned voting should take place.
* `UP`: What is considered a "positive vote", or an "upvote". Must be the actual emoji character if not using a custom emoji.
* `DOWN`: Same as up, but for a negative vote. Any reaction on the vote message is not an up or down vote will be removed.
* `ICON_ON` and `ICON_OFF`: The filenames of the server icons to be set when the bot is activated or in normal mode respectively.
* `NICKS_CSV`: The filename of the CSV (techincally TSV) used to store nicknames to be restored on deactivation.
* `CHANNELS`: A `Dict[int, str]` which stores channel IDs and their names in normal mode.
* `DEBUG`: Do not delete any non-phrase messages, change channel names, or change nicknames

Sidenote: Weenie Hut General Bot is very slow to transition from one mode to another. Discord ratelimits bots pretty harshly, so if you try to quickly change between modes expect to see rate limits 2+ minutes.

# Weenie Hut General Messaging Protocol

## What is Weenie Hut General Messaging Protocol (WHGMP)?
WHGMP is a message protocol which uses 2 Discord bots and 9 channels. It uses sender.py to send messages from stdin, and receiver.py to receive messages to stdout.

## How does it work?
WHGMP uses the read/unread badge* in a channel to represent a bit (unread = 1, read = 0). By using 8 channels, one byte can be stored. 

The sender waits for a message from the user, then begins to send messages to the data channels. After storing a single byte, a message is sent to the "clock" channel, letting the receiver know to check the read/unread status. Based off of that, a single byte is constructed. When a null-byte is received, the resulting string is printed.

\*: Technically, it uses the ID of the last message sent in the channel. Discord stores this separately from the actual last message in the channel though, which is why you can see an unread badge even if the message was deleted.

## How do I set it up?
Similar to the bot, copy config-sample.py to config.py with these config items:

* `DATA_CHANNELS`: A `List[int]` of 8 channel IDs to use as data lines.
* `CLOCK_CHANNEL`: A channel ID to use as the clock channel.

## Okay, so how fast is it?
17 seconds to send `hello world`. Yeah. Making it faster is left as an exercise to the reader.

# ...[Weenie Hut General](https://www.youtube.com/watch?v=Q3U57RO1DGE)?
The name originates from the Discord server this "protocol" was inspired by. One fateful night the server became a Weenie Hut General themed server (don't ask), similar to the [cup server](https://discord.com/invite/fza9SXT). Only the message "weenie hut general" was allowed to be sent in any channel. This became too burdensome to manage manually, so Weenie Hut General Bot was created. Contrary to the cup server, it also removes non-phrase nicknames, reactions, and edited messages. Naturally, I begin theorizing ways to communicate despite these limitations. The WHGMP is the result of that.

# LICENSE
Both the bot and WHGMP are released under [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/). If you actually want or need to use this for some reason, God help you.
