# MarkBot - Game Playing Bot for Fire Emblem 7 (US)

MarkBot is an attempt to create a bot capable of completing the GBA title "Fire Emblem", using the emulator mGBA to run the game (the bot is integrated with the mGBA API, so requires it to function). 

The bot is capable of completing the first few levels of the game. More work needs to be done to make it more consistent, as well as to beat levels with more complicated layouts, objectives and mid-chapter cutscenes. More work also needs to be done to fix unknown crashes in the server. 

# You will need:

- mGBA (recommended to build it from here: https://github.com/mgba-emu/mgba)
- A ROM of Fire Emblem (version US 1.0). This must be ripped yourself from an official copy of the game. This application does not include ANY of the game's files.
- A save file that has access to the 'Hard Mode' versions of the chapters. The tutorials forced by normal mode cause issues with the bot, creating desyncs.
- A python installation.

# Steps to Run:

1. Open mGBA, and your copy of the game. Make sure mGBA is open in the top right corner of the screen.
2. Navigate to Tools>Scripting. Load SocketServer.lua in it.
3. In the game, start a chapter.
4. Run the app from  console. Make sure to click back onto the emulator quickly (the current implementation mimic's the user's keyboard to control things. As such, when not clicked on, the bot will still try to 'act' and press buttons no matter what is currently being used. This will likely be reworked in the future to control the game through the emulator's API).

NOTE: Currently, the app only works on a per-chapter basis. As such, once you beat a map, you will have to close the application in the command line with ctrl + c. This will be fixed in later versions of the app.
