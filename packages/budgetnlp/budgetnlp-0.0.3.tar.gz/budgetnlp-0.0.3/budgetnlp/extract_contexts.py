from flashtext import KeywordProcessor
from .utils.text_normalization import _string_to_ascii, handle_data_tuples


def _find_sentence_boundaries(text):
    """Find all period positions that mark sentence boundaries."""
    boundaries = []
    for i, char in enumerate(text):
        if char in '.!?':
            boundaries.append(i)
    return boundaries


def _expand_to_sentence_context(match_start, match_end, boundaries, text_length, context_sentences):
    """Expand a match to include N sentences before and after."""
    # Find which boundaries are before and after the match
    before = [b for b in boundaries if b < match_start]
    after = [b for b in boundaries if b > match_end]
    
    # Get N sentence boundaries before the match
    if len(before) >= context_sentences:
        chunk_start = before[-context_sentences] + 1  # Start after the Nth period back
    else:
        chunk_start = 0  # Start of text
    
    # Get N sentence boundaries after the match
    if len(after) >= context_sentences:
        chunk_end = after[context_sentences - 1] + 1  # Include up to and past the Nth period forward
    else:
        chunk_end = text_length  # End of text
    
    return chunk_start, chunk_end


def _merge_overlapping_chunks(chunks):
    """Merge overlapping or adjacent chunks."""
    if not chunks:
        return []
    
    # Sort by start position
    sorted_chunks = sorted(chunks, key=lambda x: x[0])
    
    merged = [sorted_chunks[0]]
    
    for current_start, current_end in sorted_chunks[1:]:
        last_start, last_end = merged[-1]
        
        # Check if chunks overlap or are adjacent
        if current_start <= last_end:
            # Merge by extending the end position
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add as new chunk
            merged.append((current_start, current_end))
    
    return merged


@handle_data_tuples
def extract_contexts(string, keywords, context_sentences=3):
    """
    Extract text chunks around keyword matches with configurable sentence context.
    
    Overlapping chunks are automatically merged.
    
    Parameters:
    -----------
    string : str
        The text to search in
    keywords : str or list
        Keyword(s) to search for
    context_sentences : int, default=3
        Number of sentences to include before and after each match
        
    Returns:
    --------
    list of str
        Text chunks containing the keywords with surrounding context
    """
    # Normalize input
    string = _string_to_ascii(string)
    
    # Handle single keyword or list of keywords
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # Build keyword processor
    processor = KeywordProcessor(case_sensitive=False)
    for keyword in keywords:
        processor.add_keyword(keyword.lower())
    
    # Extract matches with position information
    matches = processor.extract_keywords(string.lower(), span_info=True)
    
    if not matches:
        return []
    
    # Find all sentence boundaries
    boundaries = _find_sentence_boundaries(string)
    text_length = len(string)
    
    # Expand each match to include context sentences
    chunks = []
    for keyword, start, end in matches:
        chunk_start, chunk_end = _expand_to_sentence_context(
            start, end, boundaries, text_length, context_sentences
        )
        chunks.append((chunk_start, chunk_end))
    
    # Merge overlapping chunks
    merged_chunks = _merge_overlapping_chunks(chunks)
    
    # Extract text for each merged chunk
    results = []
    for start, end in merged_chunks:
        chunk_text = string[start:end].strip()
        results.append(chunk_text)
    
    return results