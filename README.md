# Media Artwork Organiser

Media Organiser is a Python script that helps you organize your media artwork, specifically designed for Plex libraries. It finds matching artwork for movie folders and copies them if necessary, changing file names to meet Plex specification.

## Features

* Supports various image formats (JPEG, JPG, PNG, TBN).
  * *Easy to add support for new file extensions*
* Automatically detects and corrects directory paths.
* Provides a user-friendly console interface.
* Copies artwork to movie folders.
* Saves Plex users a lot of time with big libraries!

## Usage

1. Clone or download this repository.
2. Run the script by executing `python media_organiser.py` in your terminal.

## Requirements

* Python 3.x
* Standard Python libraries

## Instructions

1. When prompted, enter the directory paths for your artwork and media libraries.
   * **Artwork Directory:** The directory where your artwork files are located.
   * **Media Directory:** The directory where your movie folders are located.
2. The script will search for matching artwork for your movies in the specified directories and their subdirectories.
3. If matching artwork is found, it will be copied to the corresponding movie folder.
4. The script will display the number of new posters (artwork) copied.

*Note: If you are working with fanart and not posters, you can easily change this in the 'media_artwork_organiser.py' file at the bottom of the script, simply change 'poster' to 'fanart' in the class initialisation.*

## Example Directory Paths

* Artwork Directory: `C:/Pictures/downloaded_art`
* Media Directory: `P:/Videos/Plex/Movies`

## Console Output

The script will provide a detailed console output for each artwork copy operation, including source and destination paths.

## Exiting the Program

* If you ever need to exit the program while it's running, simply press `Ctrl + C`.

## Troubleshooting

* If you encounter any issues, check the error log generated in the `error.log` file for more information.

## Contributors

*[Ben Lewis](https://github.com/benlewisss "Click here to be taken to Ben's GitHub profile!")*

---

Feel free to contribute to this project or report any issues. Have fun!
