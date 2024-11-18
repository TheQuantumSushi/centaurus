import os
import shutil
import re
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from LogWriter import LogWriter

# Todo
# move api key from argument to keyring/json file
# replace "movie" in variable names

TMDB_API_KEY = "f0ceb830389ee3d912871135d4489911"

class Error(Exception):
    """
    Custom error class that inherits from Exception, to raise errors with a message written to log file
    """
    def __init__(self, message, logger):
        super().__init__(message)  # Initialize the base Exception with the message
        self.message = message
        self.logger = logger

    def log(self):
        """
        Print the formatted error message
        """
        # Write to log file :
        self.logger.write("ERROR", {"message":f"{self.message}", "raised by":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}})

class FileManager:

    def __init__(self, logger, api_key : str):
        """
        Initialize class parameters
        """
        self.logger = logger
        self._TMDB_API_KEY = api_key

        # Write to log file :
        self.logger.write("ACTION", {"action":"Initialized FileManager instance", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
    @property
    def api_key(self) -> str:
        """
        Get the API key
        """
        # Write to log file :
        self.logger.write("ACTION", {"action":"Fetched API key", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        return self._TMDB_API_KEY

    @api_key.setter
    def api_key(self, key : str):
        """
        Set the API key
        """
        try:
            assert key
            self._TMDB_API_KEY = key
            # Write to log file :
            self.logger.write("ACTION", {"action":"Updated API key", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        except:
            raise Error("Provided API key is blank")
            sys.exit(1)

    def extract_id(self, link : str) -> tuple[str, str]:
        """
        Extract IMDB or TMDB IDs from provided link
        """
        # Write to log file :
        self.logger.write("ACTION", {"action":f"Started ID exctraction from link {link}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        # IMDB :
        imdb_match = re.search(r"imdb\.com/title/(tt\d+)", link)
        # Write to log file :
        self.logger.write("ACTION", {"action":"Performed IMDB search", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":f"{imdb_match is None}"})
        
        # TMDB :
        tmdb_match = re.search(r"themoviedb\.org/movie/(\d+)", link)
        # Write to log file :
        self.logger.write("ACTION", {"action":"Performed TMDB search", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":f"{tmdb_match is None}"})
        
        if imdb_match:
            return "imdb", imdb_match.group(1)
        elif tmdb_match:
            return "tmdb", tmdb_match.group(1)
        else:
            return None, None

    def fetch_data(self, id_type : str, movie_id : int) -> dict[str, any]:
        """
        Fetch movie data from IMDB/TMDB using ID
        """
        # Write to log file :
        self.logger.write("ACTION", {"action":f"Started fetching data of id {movie_id} using {id_type}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        # Select correct id method :
        if id_type == "imdb":
            url = f"https://api.themoviedb.org/3/find/{movie_id}"
            params = {
                "api_key": self._TMDB_API_KEY,
                "external_source": "imdb_id"
            }
        else:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {
                "api_key": self._TMDB_API_KEY
            }

        # Fetch the data using requests :
        response = requests.get(url, params = params)
        #response.raise_for_status()  # raise an error for bad responses
        data = response.json()
        
        # Parse and structure the data :
        if id_type == "imdb":
            movie_data = data.get("movie_results", [])[0] if data.get("movie_results") else None
        else:
            movie_data = data

        # Write to log file :
        self.logger.write("ACTION", {"action":"Fetched and parsed data", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":f"{movie_data}"})
        
        return movie_data

    def generate_nfo(self, movie_data : dict[str, any]) -> str:
        """
        Generate the .nfo content in XML format with proper indentation (4 spaces).
        """
        # Define the entries
        title = movie_data.get("title", "Unknown Title")
        year = movie_data.get("release_date", "Unknown Year").split("-")[0]
        plot = movie_data.get("overview", "")
        imdb_link = f"https://www.imdb.com/title/{movie_data.get('imdb_id')}" if movie_data.get("imdb_id") else ""
        tmdb_link = f"https://www.themoviedb.org/movie/{movie_data.get('id')}"
        
        # Create the root element
        movie = ET.Element("movie")
        
        # Add child elements
        ET.SubElement(movie, "title").text = title
        ET.SubElement(movie, "year").text = year
        ET.SubElement(movie, "plot").text = plot
        ET.SubElement(movie, "imdb").text = imdb_link
        ET.SubElement(movie, "tmdb").text = tmdb_link
        ET.SubElement(movie, "genres").text = ", ".join([genre["name"] for genre in movie_data.get("genres", [])])
        ET.SubElement(movie, "rating").text = str(movie_data.get("vote_average", "N/A"))

        # Convert the tree to a string (no indentation)
        raw_xml = ET.tostring(movie, encoding="UTF-8", method="xml").decode("UTF-8")
        
        # Use minidom to pretty print with desired indentation
        parsed_xml = minidom.parseString(raw_xml)
        pretty_xml = parsed_xml.toprettyxml(indent="    ")  # 4 spaces for indentation

        # Write to log file :
        self.logger.write("ACTION", {"action":"Defined and parsed XML content", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":pretty_xml})

        # Remove the extra newline after the declaration
        return "\n".join(pretty_xml.splitlines()[1:])


    def create_data(self, base_path : str, folder_name : str, torrent_file_path : str, nfo_content : str):
        """
        Create the folder structure and write the .nfo file
        """
        # Extract the folder names from provided paths :
        movie_folder = os.path.join(base_path, folder_name)
        metadata_folder = os.path.join(movie_folder, "metadata")

        # Create the folders :

        os.makedirs(movie_folder, exist_ok = True)
        # Write to log file :
        self.logger.write("ACTION", {"action":f"Created movie folder at {movie_folder}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        os.makedirs(metadata_folder, exist_ok = True)
        # Write to log file :
        self.logger.write("ACTION", {"action":f"Created metadata folder at {metadata_folder}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

        # Copy the torrent file to the movie folder :
        torrent_filename = os.path.basename(torrent_file_path)
        movie_file_path = os.path.join(movie_folder, torrent_filename)
        shutil.copy(torrent_file_path, movie_file_path)

        # Write to log file :
        self.logger.write("ACTION", {"action":f"Copied file {torrent_filename} into {movie_file_path}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

        # Write the .nfo file :
        nfo_path = os.path.join(movie_folder, f"{folder_name}.nfo")
        with open(nfo_path, "w", encoding="utf-8") as nfo_file:
            nfo_file.write(nfo_content)

        # Write to log file :
        self.logger.write("ACTION", {"action":f"Wrote content to {nfo_path} file", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

if __name__ == "__main__":

    # Define the base path and torrent file path :
    base_path = "/home/thomas/Documents"  # replace with the actual path
    torrent_file_path = "/home/thomas/Documents/test.torrent"  # replace with the actual path to torrent file
    movie_link = input("Enter the IMDb or TMDb link for the movie: ")

    logger = LogWriter("log.txt")
    filemanager = FileManager(logger, TMDB_API_KEY)

    # Extract ID and fetch movie data :
    id_type, movie_id = filemanager.extract_id(movie_link)
    if not movie_id:
        print("Error: Could not extract movie ID from the provided link.")
    else:
        movie_data = filemanager.fetch_data(id_type, movie_id)
        if movie_data:
            # Generate NFO content and create folder structure :
            nfo_content = filemanager.generate_nfo(movie_data)
            folder_name = movie_data.get("title", "Unknown Movie").replace(" ", "_")
            filemanager.create_data(base_path, folder_name, torrent_file_path, nfo_content)
        else:
            print("Error: Could not fetch movie data from TMDb.")
