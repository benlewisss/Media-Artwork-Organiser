import os
import glob
import re
import sys
import difflib
import pathlib
import traceback
import logging
class MediaOrganiser:
    def __init__(self, artwork_type):
        """
        Initialize the MediaOrganiser with the specified artwork type.

        Args:
            artwork_type (str): Can either be 'poster' or 'fanart, poster is the movie cover seen on the plex library screen, and 'fanart' is the
            background of the movie play screen.

        Returns:
            None
        """
        # Plex supported image formats
        self.extensions = ("*.jpg", "*.jpeg", "*.png", "*.tbn")
        self.artwork_type = artwork_type
        self.clear_console()
        self.art_dir = self.get_directory_input(self, "artwork")
        self.media_dir = "C:/Users/benle/Desktop/PlexTest/Media" #self.get_directory_input(self, "media")
        self.clear_console()
        print("Artwork Directory:", self.art_dir)
        print("Media Directory:", self.media_dir)
        self.art_dir += "/**/"
        self.media_dir += "/**/"

    @staticmethod
    def clear_console():
        """
        Clear the console screen.

        Args:
            None
        
        Returns:
            None
        """
        print("\033[H\033[J")

    @staticmethod
    def separator():
        """
        Print a separator line based on the terminal size.

        Args:
            None

        Returns:
            None
        """
        term_size = int(os.get_terminal_size()[0])
        print("-" * term_size)

    @staticmethod
    def user_input_bool(default="yes"):
        """
        Get user input for yes/no questions.

        Args:
            default (str): The default answer ('yes' or 'no').

        Returns:
            user_input (bool): True for 'yes', False for 'no'.
        """
        valid_input = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError(f"Invalid default answer: '{default}'")

        while True:
            sys.stdout.write(prompt)
            choice = input().lower()
            if default is not None and choice == "":
                return valid_input[default]
            elif choice in valid_input:
                return valid_input[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

    @staticmethod
    def get_directory_input(self, input_type):
        """
        Prompt the user for a directory input and correct if necessary.
        
        Args:
            input_type (str): Either "artwork" or "media".

        Returns:
            directory_path (str): The validated directory path.
        """
        valid_input = False
        while not valid_input:
            if input_type == "artwork":
                print('[e.g. "C:/Pictures/downloaded_art"]')
            elif input_type == "media":
                print('[e.g. "P:/Videos/Plex/Movies"]')
                print('[e.g. "//<server_ip>/Plex/Movies"]')

            dir_path = input(f"Enter the {input_type} directory: ").strip("\"")

            if os.path.exists(dir_path):
                return dir_path

            corrected_dir = MediaOrganiser.directory_check(dir_path)
            if not corrected_dir:
                self.clear_console()
                print("Cannot find the directory. Please try again.\n")
            else:
                print(f"Did you mean {corrected_dir}?")
                choice = MediaOrganiser.user_input_bool("yes")
                self.clear_console()
                if choice:
                    dir_path = corrected_dir
                    valid_input = True
                else:
                    self.clear_console()
                    print("Please enter a valid directory\n")

        return dir_path

    @staticmethod
    def directory_check(directory):
        """
        Attempt to correct a directory path if it doesn't exist.

        Args:
            directory (str): The directory path to check.

        Returns:
            relative_path (str) or None: The corrected directory path if found, otherwise None.
        """
        dir_path = pathlib.Path(directory)
    
        if os.path.exists(dir_path):
            return str(dir_path)

        # Get the parent directory
        parent_dir = dir_path.parent
        dir_name = dir_path.name

        if not os.path.exists(parent_dir):
            return None

        # List files in the parent directory
        rel_path_contents = os.listdir(parent_dir)

        best_match = None
        max_ratio = 0.0

        for file in rel_path_contents:
            ratio = difflib.SequenceMatcher(None, dir_name, file).ratio()
            if ratio > max_ratio and ratio >= 0.7:
                best_match = file
                max_ratio = ratio
        
        if best_match:
            corrected_path = os.path.join(parent_dir, best_match)
            return str(corrected_path)

        return None

    def find_matching_artwork(self):
        """
        Find matching artwork for movie folders and copy them if necessary.

        Args:
            None

        Returns:
            None
        """
        # Initialize lists of supported artwork and movie folders
        matching_artwork = [file for ext in self.extensions for file in glob.glob(os.path.join(self.art_dir, ext), recursive=True)]
        matching_movies = glob.glob(self.media_dir, recursive=True)
        
        # Map artwork paths to their formatted names
        mapped_artwork = {re.sub("[-':;., ]", "", os.path.splitext(os.path.basename(os.path.normpath(src_file)))[0]): src_file for src_file in matching_artwork}
        
        # Map movie folder paths to their formatted names
        mapped_movies = {re.sub("[-':;., ]", "", os.path.basename(os.path.normpath(dst_file))): dst_file for dst_file in matching_movies}
        
        self.separator()
        print("SEARCHING")
        self.separator()
        
        # Number of movie folders without artwork that are available in the art directory
        match_num = 0
        
        print(mapped_artwork.items())
        print("\n")
        print(mapped_movies.items())
        print("\n\n")

        # Loop through the mapped artwork and movie folders
        for art_key, art_value in mapped_artwork.items():
            if art_key in mapped_movies:
                movie_value = mapped_movies[art_key]
                movie_poster_path = os.path.join(movie_value, f"{self.artwork_type}.*")

                # Check if a movie poster already exists; if so, skip
                if not glob.glob(movie_poster_path):
                    match_num += 1
                    art_value_unix = art_value.replace("\\", "/")
                    movie_poster_path_unix = os.path.join(movie_value, f"{self.artwork_type}{os.path.splitext(art_value)[1]}").replace("\\", "/")

                    # Copy artwork to the movie folder
                    #shutil.copy(art_value, os.path.join(movie_value, movie_poster_path_unix))

                    # Print messages and separators
                    print("├◄◄ {}".format(art_value_unix))
                    print("│")
                    print("└►► {}".format(movie_poster_path_unix))
                    self.separator()
        
        # Display the number of matches (the number of posters that have been moved)
        if match_num == 0:
            print(f"NO NEW {self.artwork_type.upper()}S")
        else:
            print(f"{match_num} NEW {self.artwork_type.upper()}(S)")
        
        self.separator()

if __name__ == "__main__":
    try:
        plex_library = MediaOrganiser(artwork_type="poster")
        plex_library.find_matching_artwork()

    except KeyboardInterrupt:
        os.system("cls")
        print("PROGRAM EXITED")
    
    except Exception as e:
        logging.error(traceback.format_exc())