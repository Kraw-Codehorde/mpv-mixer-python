import os
import sys
import subprocess
import random
import time
from collections import deque
from more_itertools import random_permutation, random_combination, random_product
from pymediainfo import MediaInfo


FILE_EXTENSIONS=['mkv', 'mp4', 'ts']    #add more extensions if needed

def set_pipe_uid():
    """Random unique pipe name generator, so you can run multiple instances at the same time."""
    rand_uid = random.randint(1000, 9999)
    ts = int(time.time())
    s = rf'\\.\pipe\mpv-pipe-{ts}-{rand_uid}'
    return s

class MPVController:
    """Handles interactions with MPV commands."""
    
    def __init__(self, ipc_path=r'\\.\pipe\mpv-pipe', segment_len=15, working_dir=None):
        self._ipc_path = ipc_path
        self._playlist = PlaylistManager(length=segment_len, dir=working_dir).playlist
        self._is_playing = False
        self._segment_len = segment_len
        self.mpv_process = subprocess.Popen(['mpv', '--idle', f'--input-ipc-server={self._ipc_path}', 
                                             '--script-opts=autoload-disabled=yes',
                                             ],
                                       shell=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.DEVNULL,#subprocess.PIPE,
                                       stderr=subprocess.DEVNULL)
        

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
        # print(os.access(self._ipc_path, os.W_OK))
        try:
           with open(self._ipc_path, 'w') as pipe:
               pipe.write(command + "\n")
               pipe.flush()
            #    pipe.close()
        except Exception as e:
            raise e

    def run(self):
        self.wait_for_pipe()
        _list = deque(self._playlist)
        _list_length = len(self._playlist)
        counter = 1
  
        while len(_list):
            try:
                print(f'PLAYING {counter} / {_list_length}')

                i_file = _list.popleft()
                filename = i_file[0]
                start = i_file[1]*15

                self.send_command(f'loadfile "{filename}" append-play start={start}')   #load current file
                if self._is_playing:
                    self.send_command(f'playlist-next')
                time.sleep(self._segment_len)
                if not self._is_playing:
                    self._is_playing = True
                counter += 1
 
            except Exception as e:
                print(e)
                pass
        if not len(_list):
            print('PLAYLIST OVER, EXITING...')
            self.send_command(f'quit')  #remove this if you want mpv to loop playlist instead of exiting


class FileLoader:
    """Loads files from dir/dirs."""
    
    @staticmethod
    def load_files_from_dir(dir):
        if os.path.isdir(dir):
            return [
                f for f in os.listdir(dir)
                if f.split('.')[-1] in FILE_EXTENSIONS
            ]

class KeyboardController:
    """Handles keyboard input."""
    pass

class PlaylistManager:
    """Manages playlist.
    length(seconds) -> length of the segments to be played from video file.
    total(seconds) -> total length of playlist.
    dir -> dir location of files to be played. 
    """
    
    def __init__(self, length=15, total=900, dir=None):
        self._length = length
        self._total = total
        self._dir = dir
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
        """Get duration stat from video file."""
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
        # print('PRE-PLAYLIST', out)
        return out

    def prepare_playlist(self):
        """Prepare the playlist to be played"""
        files = FileLoader.load_files_from_dir(self._dir)        
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
    wd = '.'
    if len(sys.argv) > 1:
        wd = sys.argv[1].strip('"')
    segment_length = input("Enter duration (15 by default): ")
    segment_length = int(segment_length) if segment_length.strip() else 15
    mpv = MPVController(ipc_path=set_pipe_uid(), segment_len=segment_length, working_dir=wd)
    mpv.run()