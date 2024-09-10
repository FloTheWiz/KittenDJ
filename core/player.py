from collections import defaultdict, deque
import json
import os
import random
from pomice import Queue, Track, Player
import discord  


QUEUE_FILE = 'queue_state.json'

class CustomQueue(Queue):
    def __init__(self):
        super().__init__()
        self.mode = "Normal"
        self.user_track_map = defaultdict(deque)  # Track songs by user
        self.current_user_cycle = None  # Iterator for the round robin cycle
        self.load_queue()
        self.songs = {}
        
        
    def save_queue(self):
        queue_state = {
            "queue_object": {'queue': [(track.uri, track.requester.id) for track in self._queue], 'mode': self.mode},
        }
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue_state, f)
         
    def load_queue(self):
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                queue_state = json.load(f)
        
            queue_object = queue_state.get('queue_object', None)
            if queue_object:
                return queue_object
          
    def put(self, track: Track) -> int:
        """puts a track into the queue

        Args:
            track (Track): Track to be added

        Returns:
            int: position of the track in the queue
        """
        if track.requester.id not in self.songs:
            self.songs[track.requester.id] = []
        self.songs[track.requester.id].append(track)
        # Track the request time
        if self.mode == "Round Robin":
            self._queue.append(track)
            self._sort_round_robin()
        elif self.mode == "Anarchy":
            self._queue.append(track)
            random.shuffle(self._queue)  # Shuffle the queue after adding a new track
        else:
            self._queue.append(track)  # Normal mode   
            
        position = self.find_position(track)
        return position

        
    def get_user_song(self, member: discord.Member, n: int):
        if n > 0:
            if n > len(self._queue):
                return "Index Longer than Queue!"
            else:
                if self._queue[n-1].requester.id == member.id:
                    return self._queue[n-1] 
                else:
                    if member.guild_permissions.manage_messages:
                        return self._queue[n-1]
                    else:
                        return "You can't remove somebody else's song"
        elif n == 0:
            return "That's a skip."
        else:
            user_songs = self.songs.get(member.id, [])
            if abs(n) > len(user_songs):
                return "Index longer than user queue"
            else:
                
                return user_songs[n]
            

    def get(self) -> Track:
        if self.is_empty:
            print('The dreaded day has come. The queue is empty.') # This should never happen
            return
        if self.mode == "Anarchy":
            random.shuffle(self._queue)  # Shuffle before each retrieval in Anarchy mode
        song = self._queue.pop(0)
    
        return song
    
    def _sort_normal(self):
        # Iterate over users, for each user, pick a song from them 
        self._queue.clear()
        for track in self.request_times:
            self._queue.append(track)
        
    def _sort_anarchy(self):
        random.shuffle(self._queue)
    
    def _sort_round_robin(self):
        new_queue = []
        print(self.songs)
        max_length = max([len(self.songs[user]) for user in self.songs])
        for n in range(max_length):
            for user in self.songs: 
                print(f"{n} - {user}")
                if n >= len(self.songs[user]) or self.songs[user] == []:
                    continue
                new_queue.append(self.songs[user][n])
                print(new_queue)
        print(new_queue)
        self._queue.clear()
        self._queue = new_queue 
        
                
            
    
        
    def set_mode(self, mode: str):
        self.mode = mode
        if mode == "Normal":
            self._sort_normal()  # Apply sorting when switching to Normal mode
        if mode == "Round Robin":
            self._sort_round_robin()  # Apply sorting when switching to Round Robin mode
        elif mode == "Anarchy":
            random.shuffle(self._queue)  # Shuffle when switching to Anarchy mode
            
    def get_mode(self):
        return self.mode



class CustomPlayer(Player):
    def __init__(self, *args, **kwargs):
        self.queue = CustomQueue()
        super().__init__(*args, **kwargs)

    def set_queue_mode(self, mode: str):
        self.queue.set_mode(mode)

    def get_queue_mode(self) -> str:
        return self.queue.get_mode()
