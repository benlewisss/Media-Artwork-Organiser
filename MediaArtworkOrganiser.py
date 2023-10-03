import os
import shutil
import glob
import re
import sys
import difflib
import pathlib

class MediaOrganiser:
    def __init__(self, artwork_type):
        """
        Initialize the MediaOrganiser with the specified artwork type.
        """
        self.artwork_type = artwork_type
        self.clear_console()
        self.art_dir = self.get_directory_input(self, "artwork")
        self.media_dir = self.get_directory_input(self, "media")
        self.clear_console()
        print("Artwork Directory:", self.art_dir)
        print("Media Directory:", self.media_dir)
        self.art_dir += "/**/"
        self.media_dir += "/**/"

    @staticmethod
    def clear_console():
        """Clear the console screen."""
        print("\033[H\033[J")

    @staticmethod
    def separator():
        """
        Print a separator line based on the terminal size.
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
            bool: True for 'yes', False for 'no'.
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
            str: The validated directory path.
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
            str or None: The corrected directory path if found, otherwise None.
        """
        dir_path = pathlib.Path(directory)
        dir_parts = dir_path.parts
        part_index = 1
        rel_path = dir_parts[0]

        if os.path.exists(dir_path):
            return dir_path

        while part_index < len(dir_parts):
            minimum_match_ratio = 0.7
            best_match = ""
            rel_path_contents = os.listdir(rel_path)

            for file in rel_path_contents:
                ratio = difflib.SequenceMatcher(None, file, dir_parts[part_index]).ratio()

                if ratio > minimum_match_ratio:
                    minimum_match_ratio = ratio
                    best_match = file

            if best_match:
                rel_path = os.path.join(rel_path, best_match)
                part_index += 1
            else:
                rel_path = None
                break

        return rel_path

    def find_matching_artwork(self):
        """
        Find matching artwork for movie folders and copy them if necessary.
        """
        # Plex supported image formats
        extensions = ("*.jpg", "*.jpeg", "*.png", "*.tbn")
        # Initialize lists of all supported artwork and movie folder paths
        matching_artwork = []
        matching_movies = []
        # Initialize lists of formatted artwork file and movie folder names mapped to their paths
        mapped_artwork = []
        mapped_movies = []
        # Append all supported artwork paths to a list
        for ext in extensions:
            matching_artwork.extend(glob.glob(os.path.join(self.art_dir, ext), recursive=True))
        # Map the artwork paths to their formatted names
        for src_file in matching_artwork:
            form_src = re.sub("[-':;., ]", "", os.path.splitext(os.path.basename(os.path.normpath(src_file)))[0])
            src_dict = {form_src: src_file}
            mapped_artwork.append(src_dict)
        # Append all movie folder paths to a list
        matching_movies.extend(glob.glob(self.media_dir, recursive=True))
        # Map the movie folder paths to their formatted names
        for dst_file in matching_movies:
            form_dst = re.sub("[-':;., ]", "", os.path.basename(os.path.normpath(dst_file)))
            dst_dict = {form_dst: dst_file}
            mapped_movies.append(dst_dict)
        self.separator()
        print("SEARCHING")
        self.separator()
        # Number of movie folders without artwork that are available in the art directory
        match_num = 0
        # Loop through the list of mapped artwork and the list of mapped movie folders
        for art in mapped_artwork:
            for movie in mapped_movies:
                # Loop through the keys of the list items to check for matches
                for key in art:
                    # If a corresponding movie folder and artwork are found, continue
                    if key in movie:
                        # Checks to see if a movie poster already exists; if so, skip
                        if glob.glob(os.path.join(movie[key], f"{self.artwork_type}.*")):
                            continue
                        # If there is no existing movie poster and one is available, copy it from the source
                        # directory to the corresponding move folder and provide a console output
                        else:
                            shutil.copy(art[key], os.path.join(movie[key], f"{self.artwork_type}{os.path.splitext(art[key])[1]}"))
                            match_num += 1
                            print("├◄◄ {}".format(art[key].replace("\\", "/")))
                            print("│")
                            print("└►► {}".format(os.path.join(movie[key], f"{self.artwork_type}{os.path.splitext(art[key])[1]}").replace("\\", "/")))
                            self.separator()
        # Displays the number of matches (the number of posters that have been moved)
        if match_num == 0:
            print(f"NO NEW {self.artwork_type.upper()}S")
        else:
            print(f"{match_num} NEW {self.artwork_type.upper()}(S)")
        self.separator()

if __name__ == "__main__":
    plex_library = MediaOrganiser(artwork_type="poster")
    plex_library.find_matching_artwork()