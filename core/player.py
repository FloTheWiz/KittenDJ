from collections import defaultdict, deque
from datetime import datetime, timedelta
from itertools import cycle
import random
from pomice import Queue, Track, Player

class CustomQueue(Queue):
    def __init__(self):
        super().__init__()
        self.mode = "Normal"
        self.user_track_map = defaultdict(deque)  # Use deque to maintain the order of requests
        self.request_times = defaultdict(list)
        self.track_score_map = {}
        self.played_tracks = set()  # Track played songs

    def put(self, track: Track):
        # Track the request time
        self.request_times[track.requester].append(datetime.now())
        self.user_track_map[track.requester].append(track)
        
        if self.mode == "Fair":
            self._queue.append(track)
            self._calculate_fair_scores()
            self._sort_fair()
        elif self.mode == "Round Robin":
            self._queue.append(track)
            self._sort_round_robin()
        elif self.mode == "Anarchy":
            self._queue.append(track)
            random.shuffle(self._queue)  # Shuffle the queue after adding a new track
        else:
            self._queue.append(track)  # Normal mode

    def get(self) -> Track:
        if self.is_empty:
            print('The dreaded day has come. The queue is empty.') # This should never happen
            return
        if self.mode == "Anarchy":
            random.shuffle(self._queue)  # Shuffle before each retrieval in Anarchy mode
        return self._queue.pop(0)

    def _calculate_fair_scores(self):
        # Define the time window for counting requests (e.g., 15 minutes)
        time_window = timedelta(minutes=10)
        current_time = datetime.now()

        for track in self._queue:
            requester = track.requester
            # Calculate the number of requests within the time window
            recent_requests = [t for t in self.request_times[requester] if t >= current_time - time_window]

            # Calculate the score based on the defined factors
            score = (
                len(recent_requests) * 10  # Penalty for multiple requests in the time window
                + track.length / 60  # Penalize longer tracks (in minutes)
                + sum(t.length for t in self.user_track_map[requester]) / 600  # Penalize users with many or long requests
            )
            self.track_score_map[track.title] = score

    def _sort_fair(self):
        # Sort the queue based on the calculated scores (ascending order)
        self._queue.sort(key=lambda track: self.track_score_map.get(track, 0))

    def _sort_round_robin(self):
        tracks = []
        user_tracks = defaultdict(list)
        for track in self._queue:
            user_tracks[track.requester].append(track)
        users = cycle(user_tracks.keys())
        while len(tracks) < len(self._queue):
            user = next(users)
            if user_tracks[user]:
                tracks.append(user_tracks[user].pop(0))
        self._queue = tracks

    def set_mode(self, mode: str):
        self.mode = mode
        if mode == "Fair":
            self._calculate_fair_scores()  # Calculate scores immediately when switching to Fair mode
            self._sort_fair()
        elif mode == "Round Robin":
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
