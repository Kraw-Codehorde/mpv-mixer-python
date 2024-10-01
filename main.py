import os
import subprocess
import random
import time
from collections import deque
from pymediainfo import MediaInfo

FILE_EXTENSIONS=['mkv', 'mp4', 'ts']

class MPVController:
    """Handles interactions with MPV commands."""
    
    def __init__(self, ipc_path=r'\\.\pipe\mpv-pipe'):
        self._ipc_path = ipc_path
        self._playlist = PlaylistManager().playlist
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
        print('PLAYLIST LEN', len(self._playlist))
        # print(self._playlist)
        while len(_list):
            try:
                i_file = _list.popleft()
                filename = i_file[0]
                start = i_file[1][0]
                self.send_command(f'loadfile "{filename}" replace start={start}')   #load current file
                time.sleep(5)
                self.send_command(f'loadfile "{filename}" replace start={start}')
                # time.sleep(2)
                # self.send_command(f'playlist-next')
            except IndexError:
                pass

        # self.send_command(f'loadfile "{self._playlist[0][0]}" replace start={self._playlist[0][1][0]}')
        # time.sleep(2)
        # print('start 2nd file', self._playlist[1][1][0])
        # self.send_command(f'loadfile "{self._playlist[1][0]}" append start={self._playlist[1][1][0]}')

                

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
    
    def __init__(self, length=15, total=500):
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
        
        while l > 0 and len(_pl_dict):
            try:
                rand_key = random.choice(list(_pl_dict.keys()))
                key_value = _pl_dict.get(rand_key)
                if not key_value:
                    break
                i = random.choice(range(len(key_value)))
                rand_value = key_value.pop(i)
                out.append((rand_key, rand_value))
                l -= self._length
            except Exception as e:
                print(e)
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
   
