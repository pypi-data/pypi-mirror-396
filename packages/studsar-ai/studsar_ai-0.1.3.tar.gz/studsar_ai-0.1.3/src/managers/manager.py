import os
import torch
from sentence_transformers import SentenceTransformer
import traceback
import random #This Import random for Dream Mode example
from collections import defaultdict # this for ex studsar V2 state
from ..models.neural import StudSarNeural
from ..utils.text import segment_text, SPACY_AVAILABLE 

# 1. New  ex V2 Studsar  

class StudSarManager:
    """
    Manages interaction with StudSarNeural network and auxiliary operations
    (embedding generation, segmentation, persistence).
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', initial_capacity=1024):
        # Explicitly set device to CPU for debugging, or use CUDA if available
        self.device = torch.device("cpu") # Changed to cpu for debugging
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"StudSarManager will use device: {self.device}")
        print("Loading SentenceTransformer model...")
        try:
            self.embedding_generator = SentenceTransformer(model_name, device=self.device)
            print("SentenceTransformer model loaded successfully.")
        except Exception as e:
            print(f"Error loading SentenceTransformer model: {e}")
            import traceback
            traceback.print_exc()
            raise

        print("Initializing StudSarNeural...")
        try:
            self.embedding_dim = self.embedding_generator.get_sentence_embedding_dimension()
            # Initialize StudSar neural network
            self.studsar_network = StudSarNeural(self.embedding_dim, initial_capacity, device=self.device).to(self.device)
            print("StudSarNeural initialized successfully.")
        except Exception as e:
            print(f"Error initializing StudSarNeural: {e}")
            import traceback
            traceback.print_exc()
            raise
        self.embedding_dim = self.embedding_generator.get_sentence_embedding_dimension()
        # Initialize StudSar neural network
        self.studsar_network = StudSarNeural(self.embedding_dim, initial_capacity, device=self.device).to(self.device)
        print("StudSarNeural initialized. Setting up text processor and embedding model...")
        self.text_processor = self
        self.embedding_model = self.embedding_generator
        #  New  V2: Placeholder per modello di segmentazione 
        self.segmentation_model = None # Caricare qui il modello transformer addestrato
        # try:
        #     # self.segmentation_model = load_segmentation_model("path/to/segmentation_model.pth")
        #     print("Transformer segmentation model loaded (placeholder).")
        # except Exception as e:
        #     print(f"Warning: Could not load transformer segmentation model: {e}. Using fallback.")
        # Stop Add V2 


        print(f"\n--- StudSarManager Initialization ---")
        print(f"Embedding Generator Model: {model_name} (Dim: {self.embedding_dim})")
        print(f"StudSarNeural network ready on device: {self.studsar_network.device}")
        print(f" void non Marvel \n")

    def generate_embedding(self, text):
        """Generates embedding for a text using loaded model."""
        if not text or not isinstance(text, str): return None
        #  before encoding
        self.embedding_generator.to(self.device)
        embedding = self.embedding_generator.encode(text, convert_to_tensor=True, device=self.device)
        # Return as numpy array for compatibility 
        return embedding.cpu().numpy()

    # EDIT V2: Added default emotion, use new segmentation ---
    def build_network_from_text(self, text, segment_length=100, use_spacy_segmentation=True, spacy_sentences_per_segment=3, default_emotion=None):
        """Segments text using the configured method and populates StudSarNeural network."""
        print("\n--- Building StudSar Network from Text ---")
        # Reset network with potentially new capacity if needed, keep embedding_dim
        # Pass initial capacity based on potential segment count? Or let it resize? Current: Let it resize.
        # REMOVED: self.studsar_network = StudSarNeural(self.embedding_dim, initial_capacity=initial_capacity, device=self.device).to(self.device)
        # TODO: Implement network reset logic if needed, e.g., self.studsar_network.reset_memory()
        print("Preparing to build network...") # Placeholder message

        # V2: Updated segmentation logic 
# Use transformer model if loaded, otherwise fallback
        if self.segmentation_model:
             print("Using Transformer-based segmentation (placeholder)...")
             # segments = self.segmentation_model.segment(text) #Call to the real model  
             # Placeholder: Use standard segmentation for now until model is ready
             segments = segment_text(text, segment_length=segment_length, use_spacy=use_spacy_segmentation, spacy_sentences_per_segment=spacy_sentences_per_segment)
        else:
             print("Using standard segmentation...")
             # Use the imported segment_text function directly
             segments = self.segment_text(text, segment_length=segment_length, use_spacy=use_spacy_segmentation, spacy_sentences_per_segment=spacy_sentences_per_segment)
        # END OF MODIFICATION  V2 

        if not segments:
            print("No segments generated from text. Network not built.")
            return

        # The network is already initialized in __init__. We add segments to the existing network.
        print(f"Adding {len(segments)} segments to the network...")
        added_count = 0
        for i, seg in enumerate(segments):
            if not seg.strip(): continue # Skip empty segments after join
            embedding = self.generate_embedding(seg)
            if embedding is not None:
                #  EDIT V2: Pass emotion (currently None)  
                marker_id = self.studsar_network.add_marker(seg, embedding, emotion=default_emotion)
                #  FINE MODIFICA V2 
                if marker_id is not None:
                     added_count += 1
            if (i + 1) % 50 == 0: print(f"  Processed {i+1}/{len(segments)} segments...")

        print(f"Added {added_count} markers to StudSar network.")
        print(f"Network memory now contains: {self.studsar_network.get_total_markers()} markers.")
        print("--- Network Construction Complete ---\n")

    def search(self, query_text, k=1):
        """Performs a search in StudSar network."""
        print(f"\n--- Query Search ---")
        print(f"Query: '{query_text}'")
        if not query_text or not isinstance(query_text, str):
             print("Invalid query.")
             return [], [], []

        query_embedding = self.generate_embedding(query_text)
        if query_embedding is None:
            print("Unable to generate embedding for query.")
            return [], [], []

        # Ensure network is on the correct device
        self.studsar_network.to(self.device)
        marker_ids, similarities, segments = self.studsar_network.search_similar_markers(query_embedding, k=k)

        if not marker_ids:
             print("No results found.")
        else:
            print(f"Found {len(marker_ids)} results:")
            # V2: Increment usage count for retrieved markers --- 
            for mid in marker_ids:
                self.studsar_network.increment_usage(mid) # Chiama il metodo in neural.py
            
        print("--- Search Complete ---\n")
        return marker_ids, similarities, segments

    #  V2: Added emotion parameter
    def update_network(self, new_text_segment, emotion=None):
        """Adds a new segment to existing StudSar network."""
        print("\n--- Updating StudSar Network ---")
        print(f"Adding new segment: '{new_text_segment[:100]}...' (Emotion: {emotion})")
        if not new_text_segment or not isinstance(new_text_segment, str):
             print("Invalid segment for update.")
             return None

        embedding = self.generate_embedding(new_text_segment)
        if embedding is None:
            print("Unable to generate embedding for new segment.")
            return None

        # Ensure network is on the correct device
        self.studsar_network.to(self.device)
        #  EDIT V2: Pass emotion (currently None) 
        marker_id = self.studsar_network.add_marker(new_text_segment, embedding, emotion=emotion)
        #  END OF MODIFICATION V2 

        if marker_id is not None:
            print(f"New marker added with ID {marker_id}.")
            print(f"Network memory now contains: {self.studsar_network.get_total_markers()} markers.")
            print("--- Update Complete ---\n")
            return marker_id
        else:
             print("Update failed.")
             print("--- Update Failed ---\n")
             return None

    # NEW ADDITION V2
    def update_marker_reputation(self, marker_id, feedback_score):
        """Provides feedback to a specific marker to update its reputation."""
        print(f"\n--- Updating Marker Reputation ---")
        if self.studsar_network:
            # Ensure network is on the correct device
            self.studsar_network.to(self.device)
            success = self.studsar_network.update_marker_reputation(marker_id, feedback_score)
            print(f"--- Reputation Update {'Complete' if success else 'Failed'} ---\n")
            return success
        else:
            print("Error: StudSar network not initialized.")
            print(f"--- Reputation Update Failed ---\n")
            return False
    # END OF ADDITION V2
    def save(self, filepath="studsar_neural_memory.pth"):
        """Saves StudSarNeural network state and mappings."""
        print(f"\n--- Saving StudSar State ---")
        if not self.studsar_network:
            print("Error: StudSar network not initialized. Nothing to save.")
            print("--- Save Failed ---\n")
            return False

        # Ensure network is on CPU before saving state_dict and other data
        self.studsar_network.cpu()

        # Get model name robustly
        model_name = 'all-MiniLM-L6-v2' # Default
        if hasattr(self.embedding_generator, 'tokenizer') and hasattr(self.embedding_generator.tokenizer, 'name_or_path'):
             model_name = self.embedding_generator.tokenizer.name_or_path
        elif hasattr(self.embedding_generator, 'model_name_or_path'): # Fallback for some models
             model_name = self.embedding_generator.model_name_or_path

        state = {
            'network_state_dict': self.studsar_network.state_dict(),
            'id_to_segment': self.studsar_network.id_to_segment,
            'marker_id_to_index': self.studsar_network.marker_id_to_index,
            'next_id': self.studsar_network.next_id,
            'embedding_dim': self.studsar_network.embedding_dim,
            'embedding_model_name': model_name,
            #  NEWV2: Save V2 dictionaries 
            'id_to_emotion': self.studsar_network.id_to_emotion,
            'id_to_reputation': dict(self.studsar_network.id_to_reputation), # Convert defaultdict to dict for saving
            'id_to_usage': dict(self.studsar_network.id_to_usage)           # Convert defaultdict to dict for saving
            #  AN2 
        }
        try:
            torch.save(state, filepath)
            print(f"StudSar state saved to: {filepath}")
            print("--- Save Complete ---\n")
            return True
        except Exception as e:
            print(f"Error during save: {e}")
            traceback.print_exc()
            print("--- Save Failed ---\n")
            return False

    @classmethod
    def load(cls, filepath="studsar_neural_memory.pth", model_name=None):
        """Loads state from file, including V2 attributes."""
        print(f"\n--- Loading StudSar State ---")
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found.")
            print("--- Load Failed ---\n")
            return None
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            state = torch.load(filepath, map_location=device) # Load to correct device
            # Determine which embedding model to use
            saved_model_name = state.get('embedding_model_name', 'all-MiniLM-L6-v2') # Default if missing
            if model_name is None:
                model_name = saved_model_name
                print(f"Loading will use embedding model: '{model_name}' (from saved state or default)")
            else:
                 print(f"Loading will use embedding model: '{model_name}' (forced by user)")
                 if model_name != saved_model_name:
                      print(f"Warning: Specified model '{model_name}' is different from saved model '{saved_model_name}'.")
            # Create new manager instance
            manager = cls(model_name=model_name) # Initial capacity will be handled by loading state
            # Verify embedding dimension consistency
            saved_embedding_dim = state.get('embedding_dim')
            if saved_embedding_dim != manager.embedding_dim:
                print(f"CRITICAL ERROR: Saved embedding dimension ({saved_embedding_dim}) "
                      f"does not match loaded model dimension ({manager.embedding_dim}). Loading interrupted.")
                print("--- Load Failed ---\n")
                return None

            # Reconstruct network
            # Determine initial capacity from loaded tensor if possible, else use default
            initial_capacity_loaded = 1024 # Default
            if 'network_state_dict' in state and 'memory_embeddings' in state['network_state_dict']:
                 initial_capacity_loaded = state['network_state_dict']['memory_embeddings'].shape[0]
                 if initial_capacity_loaded == 0: initial_capacity_loaded = 1024 # Handle empty saved state

            manager.studsar_network = StudSarNeural(manager.embedding_dim, initial_capacity=initial_capacity_loaded, device=manager.device).to(manager.device)

            # Load the state dict
            manager.studsar_network.load_state_dict(state['network_state_dict'])

            # Load mappings and V2 attributes
            manager.studsar_network.id_to_segment = state.get('id_to_segment', {})
            manager.studsar_network.marker_id_to_index = state.get('marker_id_to_index', {})
            manager.studsar_network.next_id = state.get('next_id', 0)

            #  NEWV2: Load V2 dictionaries 
            manager.studsar_network.id_to_emotion = state.get('id_to_emotion', {})
            # Load reputation and usage, converting back to defaultdict if needed or handling missing keys
            manager.studsar_network.id_to_reputation = defaultdict(float, state.get('id_to_reputation', {}))
            manager.studsar_network.id_to_usage = defaultdict(int, state.get('id_to_usage', {}))
            print(f"Loaded {len(manager.studsar_network.id_to_emotion)} emotion tags.")
            print(f"Loaded {len(manager.studsar_network.id_to_reputation)} reputation scores.")
            print(f"Loaded {len(manager.studsar_network.id_to_usage)} usage counts.")
            #  AN2 


            print(f"StudSar state loaded from: {filepath}")
            print(f"Number of markers loaded: {manager.studsar_network.get_total_markers()}")
            print("--- Load Complete ---\n")
            return manager

        except Exception as e:
            print(f"General error during loading: {e}")
            traceback.print_exc() # Print stack trace for debug
            print("--- Load Failed ---\n")
            return None
    #  END NEW ADDITION V2  

    def segment_text(self, text, segment_length=100, use_spacy=True, spacy_sentences_per_segment=3):
        """Delegates to the global segment_text function."""
        return segment_text(text, segment_length=segment_length, use_spacy=use_spacy, spacy_sentences_per_segment=spacy_sentences_per_segment)

    # NEW ADDITION V2: Hook for View  
    def visualize_graph(self, similarity_threshold=0.85, output_file="studsar_graph.png"):
        """
        Generates and saves a visualization of the internal semantic graph.
        Requires networkx and matplotlib/plotly.
        """
        print("\n--- Generating Semantic Graph Visualization ---")
        if not self.studsar_network:
            print("Error: StudSar network not initialized.")
            print("--- Visualization Failed ---\n")
            return

        try:
            # Import visualization utility here to avoid making it a hard dependency
            from ..utils.visualization import plot_semantic_graph
        except ImportError:
            print("Error: Visualization requires 'networkx' and 'matplotlib'. Please install them (pip install networkx matplotlib).")
            print("--- Visualization Failed ---\n")
            return

        # Ensure network is on the correct device
        self.studsar_network.to(self.device)
        id_to_embedding_map = self.studsar_network.get_all_embeddings_and_ids()

        if not id_to_embedding_map:
            print("No markers in memory to visualize.")
            print("--- Visualization Complete (Empty Graph) ---\n")
            return

        print(f"Generating graph for {len(id_to_embedding_map)} markers...")
        try:
            plot_semantic_graph(
                id_to_embedding_map,
                self.studsar_network.id_to_segment,
                similarity_threshold=similarity_threshold,
                output_file=output_file,
                id_to_emotion=self.studsar_network.id_to_emotion, # Pass emotion data
                id_to_reputation=self.studsar_network.id_to_reputation # Pass reputation data
            )
            print(f"Semantic graph saved to '{output_file}'")
            print("--- Visualization Complete ---\n")
        except Exception as e:
            print(f"Error during graph generation or plotting: {e}")
            traceback.print_exc()
            print("--- Visualization Failed ---\n")
    #  END NEW ADDITION V2   


    #  Added to access marker data (example) 
    def get_marker_details(self, marker_id):
         """Retrieves full details for a marker by accessing the dictionary returned by the network."""
         if self.studsar_network:
              details_dict = self.studsar_network.get_marker_by_id(marker_id)
              if details_dict: # Check if dictionary is not None
                   # Access data using dictionary keys
                   segment = details_dict.get("segment", "N/A")
                   emotion = details_dict.get("emotion", "N/A")
                   reputation = details_dict.get("reputation", 0.0)
                   usage = details_dict.get("usage_count", 0)
                   # embedding = details_dict.get("embedding") # Embedding is also available

                   print(f"\n--- Marker Details (ID: {marker_id}) ---")
                   print(f"Segment: '{segment[:100]}...'" )
                   print(f"Emotion: {emotion}")
                   print(f"Reputation: {reputation:.2f}")
                   print(f"Usage Count: {usage}")
                   # print(f"  Embedding Shape: {embedding.shape if embedding is not None else 'N/A'}") # Uncomment to see shape
                   print(f" Void Embedding  \n")
                   return details_dict # Return the full dictionary
              else:
                   print(f"Marker ID {marker_id} not found.")
                   return None
         else:
              print("Error: StudSar network not initialized.")
              return None