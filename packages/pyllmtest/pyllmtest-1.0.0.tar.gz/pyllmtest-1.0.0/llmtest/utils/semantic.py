"""
Semantic Utilities
==================
Semantic similarity and embedding-based comparisons.
"""

from typing import List, Optional
import numpy as np


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score between 0 and 1
    """
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def calculate_semantic_similarity(
    text1: str,
    text2: str,
    provider
) -> float:
    """
    Calculate semantic similarity between two texts using embeddings.
    
    Args:
        text1: First text
        text2: Second text
        provider: LLM provider with embedding support
        
    Returns:
        Similarity score between 0 and 1
    """
    # Get embeddings
    if hasattr(provider, 'get_embedding'):
        emb1 = provider.get_embedding(text1)
        emb2 = provider.get_embedding(text2)
    else:
        raise ValueError("Provider does not support embeddings")
    
    # Calculate cosine similarity
    return cosine_similarity(emb1, emb2)


def find_most_similar(
    query: str,
    candidates: List[str],
    provider,
    top_k: int = 1
) -> List[tuple]:
    """
    Find most similar texts from candidates.
    
    Args:
        query: Query text
        candidates: List of candidate texts
        provider: LLM provider with embedding support
        top_k: Number of top matches to return
        
    Returns:
        List of (text, similarity_score) tuples
    """
    if not hasattr(provider, 'get_embedding'):
        raise ValueError("Provider does not support embeddings")
    
    query_emb = provider.get_embedding(query)
    
    # Calculate similarities
    similarities = []
    for candidate in candidates:
        candidate_emb = provider.get_embedding(candidate)
        sim = cosine_similarity(query_emb, candidate_emb)
        similarities.append((candidate, sim))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]


def semantic_deduplication(
    texts: List[str],
    provider,
    threshold: float = 0.95
) -> List[str]:
    """
    Remove semantically duplicate texts.
    
    Args:
        texts: List of texts
        provider: LLM provider with embedding support
        threshold: Similarity threshold for considering duplicates
        
    Returns:
        Deduplicated list of texts
    """
    if not texts:
        return []
    
    if not hasattr(provider, 'get_embedding'):
        raise ValueError("Provider does not support embeddings")
    
    # Get embeddings
    embeddings = [provider.get_embedding(text) for text in texts]
    
    # Keep track of which texts to keep
    keep = [True] * len(texts)
    
    for i in range(len(texts)):
        if not keep[i]:
            continue
        
        for j in range(i + 1, len(texts)):
            if not keep[j]:
                continue
            
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim >= threshold:
                # Mark j as duplicate
                keep[j] = False
    
    # Return non-duplicate texts
    return [text for i, text in enumerate(texts) if keep[i]]


def cluster_texts(
    texts: List[str],
    provider,
    num_clusters: int = 3
) -> Dict[int, List[str]]:
    """
    Cluster texts by semantic similarity.
    
    Args:
        texts: List of texts to cluster
        provider: LLM provider with embedding support
        num_clusters: Number of clusters
        
    Returns:
        Dictionary mapping cluster_id to list of texts
    """
    if not texts:
        return {}
    
    if not hasattr(provider, 'get_embedding'):
        raise ValueError("Provider does not support embeddings")
    
    # Get embeddings
    embeddings = np.array([provider.get_embedding(text) for text in texts])
    
    # Use k-means clustering
    from sklearn.cluster import KMeans
    
    kmeans = KMeans(n_clusters=min(num_clusters, len(texts)), random_state=42)
    labels = kmeans.fit_predict(embeddings)
    
    # Group texts by cluster
    clusters = {}
    for i, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(texts[i])
    
    return clusters
