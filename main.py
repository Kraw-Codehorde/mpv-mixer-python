import os
import sys
import subprocess
import random
import time
from collections import deque
from more_itertools import random_permutation, random_combination, random_product
from pymediainfo import MediaInfo

FILE_EXTENSIONS=['mkv', 'mp4', 'ts']



class MPVController:
    """Handles interactions with MPV commands."""
    
    def __init__(self, ipc_path=r'\\.\pipe\mpv-pipe'):
        self._ipc_path = ipc_path
        self._playlist = PlaylistManager().playlist
        self._is_playing = False
        self.mpv_process = subprocess.Popen(['mpv', '--idle', f'--input-ipc-server={self._ipc_path}', 
                                             '--script-opts=autoload-disabled=yes'],
                                       shell=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        

    def wait_for_pipe(self, timeout=5, interval=0.1):
        """Wait for the IPC pipe to be created."""
        pipe_path = self._ipc_path
        elapsed_time = 0
        while elapsed_time < timeout:
            if os.path.exists(pipe_path):  # Check if pipe exists
                print("Pipe is ready.")
                return True
            time.sleep(interval)
            elapsed_time += interval
        raise TimeoutError("IPC pipe was not created in time.")


    def send_command(self, command):
        """Send command to pipe"""
        try:
           with open(self._ipc_path, 'w') as pipe:
               pipe.write(command + "\n")
               pipe.flush()
        except Exception as e:
            raise e

    def run(self):
        self.wait_for_pipe()
        _list = deque(self._playlist)
  
        while len(_list):
            try:
                i_file = _list.popleft()
                filename = i_file[0]
                start = i_file[1]*15

                self.send_command(f'loadfile "{filename}" append-play start={start}')   #load current file
                if self._is_playing:
                    time.sleep(1)
                    self.send_command(f'playlist-next')
                time.sleep(3)
                if not self._is_playing:
                    self._is_playing = True
 
            except Exception as e:
                print(e)
                pass


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
    
    def __init__(self, length=15, total=600):
        self._length = length
        self._total = total
        self.playlist = self.prepare_playlist()
    
    def segment_file(self, duration):
        """Divide a file into segments set by duration"""
        segment_len = self._length
        segments = int(duration // segment_len)
        total = self._total // segment_len
        max_total = min(segments, total)

        random_segments = list(random_permutation(range(segments), r=max_total))   
        return random_segments

    def get_duration(self, file):
        vf = MediaInfo.parse(file)
        duration = ([t for t in vf.tracks if t.track_type == "Video"][0].duration) / 1000
        return duration
    
    def shuffle_playlist(self, pl_dict):
        out = []
        l = self._total
        _pl_dict = pl_dict.copy()
        
        while l > 0 and len(_pl_dict):
            try:
               rand_key = random.choice(list(_pl_dict.keys()))  #random key from dict
               key_value = _pl_dict[rand_key]   
               if not len(key_value):   #if value from array is empty then remove key from dict
                   del _pl_dict[rand_key]
                   continue
               
               out.append((rand_key, key_value.pop()))

               l -= self._length    #rest segment length from total playtime

            except Exception as e:
               pass
        print('PRE-PLAYLIST', out)
        return out

    def prepare_playlist(self):
        """Prepare the playlist to be played"""
        files = FileLoader.load_files_from_dir()        
        print('raw files', files, len(files))
        pl = {}
        for f in files:
            try:
                fd = self.get_duration(f)
                pl[f] = self.segment_file(fd)
                print('file ready', pl[f])
            except Exception as e:
                print(e)
                pass
        return self.shuffle_playlist(pl)

        

if  __name__ == "__main__":
    mpv = MPVController()
    mpv.run()
   
