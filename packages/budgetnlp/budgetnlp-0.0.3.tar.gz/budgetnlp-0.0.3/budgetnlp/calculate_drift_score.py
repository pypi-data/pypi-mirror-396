import math

def calculate_drift_score(embeddings, token_counts=None):
    if len(embeddings) < 2:
        raise ValueError("Need at least 2 embeddings to calculate drift")
    
    if token_counts and len(token_counts) != len(embeddings):
        raise ValueError("token_counts must match embeddings length")
    
    results = []
    
    for i in range(len(embeddings) - 1):
        prior_emb = embeddings[i]
        current_emb = embeddings[i + 1]
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(prior_emb, current_emb))
        norm_prior = math.sqrt(sum(a * a for a in prior_emb))
        norm_current = math.sqrt(sum(b * b for b in current_emb))
        
        cosine_sim = dot_product / (norm_prior * norm_current)
        cosine_dist = 1 - cosine_sim
        
        # Drift score (with length penalty if provided)
        drift_score = cosine_dist
        if token_counts:
            drift_score = cosine_dist * math.log(token_counts[i + 1])
        
        results.append({
            'comparison': f'{i} vs {i+1}',
            'cosine_distance': cosine_dist,
            'drift_score': drift_score
        })
    
    return results


# Usage:
# embeddings = [emb_2020, emb_2021, emb_2022, emb_2023]
# token_counts = [5000, 5200, 4800, 6000]
# drift = calculate_drift_score(embeddings, token_counts)