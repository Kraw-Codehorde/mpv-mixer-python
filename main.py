import os
import subprocess
import random
from pymediainfo import MediaInfo

FILE_EXTENSIONS=['mkv', 'mp4', 'ts']

class MPVController:
    """Handles interactions with MPV commands."""
    
    def __init__(self, ipc_path='/tmp/mpvsocket'):
        self._ipc_path = ipc_path
        self._playlist = PlaylistManager().playlist

    def run(self):
        print(self._playlist)
        # return subprocess.Popen(["mpv", f"{self._playlist}"], shell=True)

class FileLoader:
    """Loads files from dir/dirs."""
    
    @staticmethod
    def load_files_from_dir():
        return [
            f for f in os.listdir()
            if f.split('.')[-1] in FILE_EXTENSIONS
        ]

class KeyboardController:
    """Handles keyboard input."""
    pass

class PlaylistManager:
    """Manages playlist."""
    
    def __init__(self, length=15, total=100):
        self._length = length
        self._total = total
        self.playlist = self.prepare_playlist()
    
    def segment_file(self, duration):
        """Divide a file into segments set by duration"""
        segment_len = self._length
        segments = duration // segment_len
        out = []
        counter = 0
        for x in range(int(segments)):
            current = x*segment_len
            counter += 1
            if counter == segments:
                out.append((current, current + segment_len + ((duration % segment_len) - 1)))
            else:            
                out.append((current, current + segment_len))
        return out   

    def get_duration(self, file):
        vf = MediaInfo.parse(file)
        duration = ([t for t in vf.tracks if t.track_type == "Video"][0].duration) / 1000
        return duration
    
    def shuffle_playlist(self, pl_dict):
        out = []
        l = self._total
        _pl_dict = pl_dict
        
        while l > 0:
            try:
                rand_key = random.choice(list(_pl_dict.keys()))
                key_value = _pl_dict[rand_key]
                i = random.choice(range(len(key_value)))
                rand_value = key_value.pop(i)
                out.append((rand_key, rand_value))
                l -= self._length
            except Exception as e:
                pass
        return out


    def prepare_playlist(self):
        """Prepare the playlist to be played"""
        files = FileLoader.load_files_from_dir()        
        pl = {}
        for f in files:
            fd = self.get_duration(f)
            pl[f] = self.segment_file(fd)
        return self.shuffle_playlist(pl)

        

if  __name__ == "__main__":
    mpv = MPVController()
    mpv.run()
   
