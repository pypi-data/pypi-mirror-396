# omni_lid/decoder.py
import torch
import numpy as np
from itertools import groupby

class ViterbiDecoder:
    def __init__(self, id2lang, silence_id, transition_scale=1.0, min_confidence=0.0):
        self.id2lang = id2lang
        self.num_classes = len(id2lang)
        self.silence_id = silence_id
        self.transition_scale = transition_scale
        self.min_confidence = min_confidence
        self.frame_duration = 0.02

    def decode(self, logits):
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        log_probs = np.log(probs + 1e-9)
        
        # Low Confidence Filtering
        if self.min_confidence > 0:
            max_probs = np.max(probs, axis=-1)
            low_conf_mask = max_probs < self.min_confidence
            log_probs[low_conf_mask, :] = -20.0 
            log_probs[low_conf_mask, self.silence_id] = 0.0 

        T, C = log_probs.shape
        dp = np.zeros((T, C))
        backpointers = np.zeros((T, C), dtype=int)
        
        # 초기화
        dp[0] = log_probs[0]

        # 전이 행렬 (확률 평행이동)
        transition_matrix = np.full((C, C), -self.transition_scale)
        np.fill_diagonal(transition_matrix, 0.0)

        # Forward
        for t in range(1, T):
            prev_scores = dp[t-1][:, None] + transition_matrix
            best_prev_idx = np.argmax(prev_scores, axis=0)
            max_scores = np.max(prev_scores, axis=0)
            
            dp[t] = max_scores + log_probs[t]
            backpointers[t] = best_prev_idx

        # Backward
        best_path = np.zeros(T, dtype=int)
        best_path[-1] = np.argmax(dp[-1])
        
        for t in range(T-2, -1, -1):
            best_path[t] = backpointers[t+1, best_path[t+1]]

        return best_path, probs

    def get_segments(self, best_path):
        segments = []
        current_time_idx = 0
        
        for token_id, group in groupby(best_path):
            duration_frames = len(list(group))
            start_time = current_time_idx * self.frame_duration
            end_time = (current_time_idx + duration_frames) * self.frame_duration
            
            lang_name = self.id2lang.get(token_id, f"Unknown({token_id})")
            segments.append({
                "label": lang_name,
                "start": start_time,
                "end": end_time,
                "id": token_id
            })
            current_time_idx += duration_frames
            
        return segments