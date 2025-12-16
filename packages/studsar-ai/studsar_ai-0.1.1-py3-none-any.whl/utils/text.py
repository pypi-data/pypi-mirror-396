"""
Text segmentation utility module in StudSar.
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Here I made an attempt to import spaCy, but it handled as optional
try:
    import spacy
    SPACY_MODEL_NAME = "en_core_web_sm"
    try:
        nlp = spacy.load(SPACY_MODEL_NAME)
        print(f"SpaCy model '{SPACY_MODEL_NAME}' loaded.")
        SPACY_AVAILABLE = True
    except Exception as e:
        nlp = None
        SPACY_AVAILABLE = False
        print(f"SpaCy model '{SPACY_MODEL_NAME}' not loaded ({e}). Word segmentation will be used as fallback.")
except ImportError:
    spacy = None
    nlp = None
    SPACY_AVAILABLE = False
    print("SpaCy not installed. Word segmentation will be used as fallback.")
    print("To install spaCy (optional): pip install spacy && python -m spacy download en_core_web_sm")

# NEWV2: Placeholder for Transformer Segmentation 
def segment_text_transformer_placeholder(text):
    """Placeholder function for transformer-based segmentation."""
    print("\n--- Using Transformer Segmentation (Placeholder) ---")
    print("WARNING: Transformer segmentation model not implemented. Falling back to basic segmentation.")
    # In a real implementation:
    # - Load the fine-tuned transformer model.
    # - Tokenize the input text.
    # - Use the model to predict segment boundaries.
    # - Split the text based on predictions.
    # segments = model.predict_segments(text)
    # return segments
    # Fallback for now:
    return segment_text(text, use_spacy=False) # Use word-based as fallback here
#  end  

def segment_text(text, segment_length=100, use_spacy=True, spacy_sentences_per_segment=3):
    """Segments the text (words or sentences via spaCy)."""
    segments = []
    #  heare -> spaCy for the user
    if use_spacy and SPACY_AVAILABLE and nlp:
        try:
            doc = nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            if not sentences: return []
            for i in range(0, len(sentences), spacy_sentences_per_segment):
                segments.append(" ".join(sentences[i:i + spacy_sentences_per_segment]))
        except Exception as e:
            print(f"SpaCy error, fallback to words: {e}")
            use_spacy = False # Force fallback
    # Fallback to word-based segmentation
    if not (use_spacy and SPACY_AVAILABLE and nlp): 
        words = text.split()
        if not words: return []
        for i in range(0, len(words), segment_length):
            segments.append(" ".join(words[i:i + segment_length]))
    # Filter empty segments
    segments = [seg for seg in segments if seg.strip()]
    print(f"Text segmented into {len(segments)} blocks.")
    return segments