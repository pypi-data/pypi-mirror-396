"""
Search utilities for hybrid search and reranking.
"""

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


def reciprocal_rank_fusion(
    ranked_lists: List[List[str]],
    k: int = 60,
    min_score: float = 0,
) -> List[Tuple[str, float]]:
    """
    Combine multiple ranked lists using Reciprocal Rank Fusion.
    
    RRF score = Σ 1/(k + rank) for each list where item appears
    
    Args:
        ranked_lists: List of ranked ID lists
        k: RRF constant (default 60)
        min_score: Minimum score threshold
        
    Returns:
        List of (id, score) tuples sorted by score descending
    """
    scores: Dict[str, float] = {}
    
    for ranked_list in ranked_lists:
        for rank, item_id in enumerate(ranked_list):
            rrf_score = 1 / (k + rank + 1)
            scores[item_id] = scores.get(item_id, 0) + rrf_score
    
    results = [(id_, score) for id_, score in scores.items() if score >= min_score]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def maximal_marginal_relevance(
    query_embedding: List[float],
    candidates: List[Tuple[str, List[float]]],
    lambda_param: float = 0.5,
    limit: int = 10,
) -> List[Tuple[str, float]]:
    """
    Maximal Marginal Relevance - balances relevance with diversity.
    
    Args:
        query_embedding: Query vector
        candidates: List of (id, embedding) tuples
        lambda_param: Balance between relevance (1.0) and diversity (0.0)
        limit: Maximum results to return
        
    Returns:
        List of (id, score) tuples
    """
    if not candidates:
        return []
    
    selected: List[Tuple[str, float]] = []
    remaining = list(candidates)
    
    # Pre-compute query similarities
    query_sims = {
        id_: cosine_similarity(query_embedding, emb)
        for id_, emb in candidates
    }
    
    while len(selected) < limit and remaining:
        best_idx = -1
        best_score = float('-inf')
        
        for i, (cand_id, cand_emb) in enumerate(remaining):
            query_sim = query_sims[cand_id]
            
            # Max similarity to already selected
            max_selected_sim = 0.0
            for sel_id, _ in selected:
                sel_emb = next((e for id_, e in candidates if id_ == sel_id), None)
                if sel_emb:
                    sim = cosine_similarity(cand_emb, sel_emb)
                    max_selected_sim = max(max_selected_sim, sim)
            
            # MMR score
            mmr_score = lambda_param * query_sim - (1 - lambda_param) * max_selected_sim
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i
        
        if best_idx >= 0:
            chosen_id, _ = remaining.pop(best_idx)
            selected.append((chosen_id, query_sims[chosen_id]))
        else:
            break
    
    return selected


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot / (norm_a * norm_b)


# Stop words for keyword extraction
STOP_WORDS: Set[str] = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
    'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
    'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'between', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but',
    'if', 'or', 'because', 'until', 'while', 'what', 'which', 'who',
    'whom', 'this', 'that', 'these', 'those', 'am', 'i', 'me', 'my',
    'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
    'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves'
}


def extract_keywords(query: str) -> List[str]:
    """Extract keywords from query, removing stop words."""
    words = re.sub(r'[^\w\s]', ' ', query.lower()).split()
    return [w for w in words if len(w) > 1 and w not in STOP_WORDS]


def keyword_overlap_score(query: str, text: str) -> float:
    """Calculate keyword overlap score between query and text."""
    query_keywords = set(extract_keywords(query))
    text_keywords = set(extract_keywords(text))
    
    if not query_keywords:
        return 0.0
    
    matches = len(query_keywords & text_keywords)
    return matches / len(query_keywords)


@dataclass
class QueryIntent:
    """Detected query intent."""
    type: str  # identity, preference, location, work, relationship, general
    keywords: List[str]
    relation_types: List[str]


def detect_query_intent(query: str) -> QueryIntent:
    """
    Detect the intent of a query for better search routing.
    
    Args:
        query: The search query
        
    Returns:
        QueryIntent with type, keywords, and relevant relation types
    """
    lower_query = query.lower()
    
    # Identity queries (name, who am I)
    if re.search(r'\b(name|who am i|call me|called)\b', lower_query):
        return QueryIntent(
            type='identity',
            keywords=['name', 'called', 'identity'],
            relation_types=['HAS_NAME', 'IS_NAMED', 'CALLED', 'has_name', 'is_named']
        )
    
    # Preference queries
    if re.search(r'\b(like|love|prefer|favorite|hate|dislike)\b', lower_query):
        return QueryIntent(
            type='preference',
            keywords=extract_keywords(query),
            relation_types=['LIKES', 'LOVES', 'PREFERS', 'HATES', 'DISLIKES', 'likes', 'prefers']
        )
    
    # Location queries
    if re.search(r'\b(live|located|location|where|city|country|address)\b', lower_query):
        return QueryIntent(
            type='location',
            keywords=['location', 'city', 'country', 'address', 'live'],
            relation_types=['LIVES_IN', 'LOCATED_IN', 'lives_in', 'located_in']
        )
    
    # Work queries
    if re.search(r'\b(work|job|company|employer|occupation|career)\b', lower_query):
        return QueryIntent(
            type='work',
            keywords=['work', 'job', 'company', 'employer'],
            relation_types=['WORKS_AT', 'EMPLOYED_BY', 'works_at', 'employed_by']
        )
    
    # Relationship queries
    if re.search(r'\b(know|friend|family|married|spouse|partner)\b', lower_query):
        return QueryIntent(
            type='relationship',
            keywords=extract_keywords(query),
            relation_types=['KNOWS', 'FRIENDS_WITH', 'MARRIED_TO', 'knows', 'friends_with']
        )
    
    return QueryIntent(
        type='general',
        keywords=extract_keywords(query),
        relation_types=[]
    )


def sanitize_lucene_query(query: str) -> str:
    """
    Sanitize a query string for Lucene fulltext search.
    
    Args:
        query: Raw query string
        
    Returns:
        Sanitized query safe for Lucene
    """
    # Escape special Lucene characters
    special_chars = r'[+\-&|!(){}[\]^"~*?:\\/]'
    sanitized = re.sub(special_chars, lambda m: '\\' + m.group(0), query)
    
    sanitized = sanitized.strip()
    if not sanitized:
        return ""
    
    # Split into words and add fuzzy matching
    words = sanitized.split()
    if not words:
        return ""
    
    # Use OR between words with fuzzy matching
    return " OR ".join(f"{w}~" for w in words if w)
