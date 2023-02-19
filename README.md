# Media-Artwork-Organiser
A very simple Python program to simplify the process of assigning artworks to media on Plex


Everything is heavily documented within the code so it is as simple to use as possible. The use-case for this program is quite specific, but it can save you a lot of time if you have a lot of media in your plex server that you would like to apply artwork to (this process is extremely tedious if done manually).

All of the parameters contain example directories etc. so that you can easily copy your own directories in with the correct formatting. But I have also recently implemented a user input function which allows users to simply type in the directories into the terminal.

I hope you find it as useful as I did!

Note, this will require Python 3.0 to run, and will require the following modules to be installed (easily done via PIP):
```
os
shutil
glob
re
```

Note: This also works for TV shows as they follow the same Plex formatting rules.
