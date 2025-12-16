#!/usr/bin/env python
# *18* coding: utf-8 *18*
"""
⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀
⠀⠀⢀⣴⡟⠛⣻⣿⣿⠿⠟⠛⠛⠛⠛⠿⢿⣿⡛⢻⣿⣿⣷⣄⠀⠀⠀
⠀⣠⡿⠋⢠⣾⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⡇⠙⢷⣦⠀
⠈⢿⣧⡀⣿⣿⣿⣿⣷⣦⣤⣤⣤⣄⣀⣀⣀⣈⡉⠉⠉⠁⣠⣾⠟⠁
⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿1⣿⣿8⣿⣿⣿⣿⣷⣤⣴⡟⠁⠀⠀
⠀⠀⠀⠀⠙⣿⣍⠉⠉⠛⠛⠛⠛⠛⠛⠛⠻⠿⢿⣿⣿⡿⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠻⣷⣶⣶⣶⣦⣄⠀⠀⢀⣀⣴⣿⠟⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿9⠿⠿⠿⠿⢿6⠟⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⡀⠀⣰⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
test_rag_integration.py
End-to-end testing of RAGConnector + StudSar integration.
Verification:
- Full initialization
- External document ingest
- Hybrid semantic searches
- Emotion handling
- Full persistence and reload
"""

from __future__ import annotations
import os
import sys
import traceback
from pathlib import Path
from typing import Any, List, Optional

# Here you must make the project importable from the root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

TMP_DOC = ROOT_DIR / "tmp_ai_research.txt"
SAVE_FILE = ROOT_DIR / "studsar_rag_test.pth"


def check_rag_dependencies() -> bool:
    """Make sure RAG dependencies are installed."""
    try:
        import langchain_community  # noqa: F401
        import langchain_core  # noqa: F401
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        print("--No-- Missing RAG dependencies. Install with:")
        print(" pip install langchain-community langchain-core sentence-transformers pypdf beautifulsoup4")
        return False


def create_test_document() -> None:
    """Create a test document for RAG ingestion."""
    content = """Advanced AI Research Document - 2024
Natural Language Processing (NLP) enables computers to understand human language.
Modern NLP uses transformer architectures like BERT, GPT, and T5 models.
Computer Vision allows machines to interpret visual information from images and videos.
Convolutional Neural Networks (CNNs) are fundamental for image recognition tasks.
Reinforcement Learning trains agents to make decisions through trial and error.
Deep Q-Networks and Policy Gradient methods are popular RL approaches.
Recent AI breakthroughs include:
- Large Language Models like GPT-4 and Claude
- Generative AI for image and text creation  
- Autonomous driving systems
- Medical diagnosis AI systems
- Real-time language translation
- Multimodal AI combining text, image, and audio
Emerging trends:
- Few-shot and zero-shot learning
- Federated learning for privacy
- Explainable AI (XAI) methods
- AI safety and alignment research
"""
    TMP_DOC.write_text(content, encoding="utf-8")

def test_rag_integration() -> bool:
    """THE story here full test of RAG + StudSar integration."""
    print("<<< sNow history is made guys a RAG + integration test with StudSar V3 >>> \n")
    
    try:
        # 0. Check dependencies
        print("Check dependencies RAG...")
        if not check_rag_dependencies():
            return False
        print("✓ Available RAG Dependencies")

        # Import Modules
        print("\n 1 < Import Modules StudSar >...")
        from src.managers.manager import StudSarManager  # type: ignore
        from src.rag.rag_connector import RAGConnector  # type: ignore
        print("✓ Modules imported successfully")

        # Initialize StudSar with emotions
        print("\n2. Initialization StudSar...")
        manager = StudSarManager()
        
        # Build knowledge base with emotions
        base_knowledge = (
            "Artificial intelligence (AI) is intelligence demonstrated by machines. "
            "Machine learning is a core part of modern AI systems. " 
            "Deep learning uses neural networks with multiple layers for complex pattern recognition."
        )
        manager.build_network_from_text(base_knowledge, default_emotion="neutral")
        base_markers = manager.studsar_network.get_total_markers()
        print(f" ✓ Basic network: {base_markers} markers con emozioni")

        # Connect RAGConnector
        print("\n3. Here is the RAGConnector...")
        rag = RAGConnector(manager)
        print("RAGConnector collegato alla memoria StudSar")

        # Create and add external document
        print("\n4. Ingesting external document...")
        create_test_document()
        
        source_id = rag.add_document(
            str(TMP_DOC),
            source_id="ai_research_2024",
            metadata_extra={
                "emotion": "important",
                "category": "research",
                "topic": "AI_technology",
                "year": 2024,
                "confidence": "high"
            },
        )
        
        if not source_id:
            print(" ❌ Error adding document")
            return False
            
        total_markers = manager.studsar_network.get_total_markers()
        new_markers = total_markers - base_markers
        print(f" ✓ Document added: {source_id}")
        print(f" ✓ New markers: {new_markers} (total: {total_markers})")

        #  Full semantic search (base + RAG)
        print("\n5A. Full semantic search...")
        query1 = "natural language processing transformers"
        ids, similarities, segments = manager.search(query1, k=4)
        print(f"   Query: '{query1}'")
        print(f"   Results: {len(ids)} found")
        
        for i, (marker_id, sim, seg) in enumerate(zip(ids, similarities, segments), 1):
            # Get marker details (including emotions)
            details = manager.get_marker_details(marker_id) if hasattr(manager, 'get_marker_details') else None
            emotion = details.get('emotion', 'N/A') if details else 'N/A'
            reputation = details.get('reputation', 0.0) if details else 0.0
            usage = details.get('usage_count', 0) if details else 0
            
            print(f"   {i}. ID={marker_id} | Sim={sim:.3f} | Emo={emotion} | Rep={reputation:.1f} | Use={usage}")
            print(f"      Text: «{seg[:70]}...»")

        #  RAG-only document search
        print("\n5B. RAG-only document search...")
        query2 = "language models GPT BERT"
        rag_results = rag.search_external_sources(query2, limit=3)
        print(f"RAG Query: '{query2}'")
        print(f"RAG Results: {len(rag_results)} found")
        
        for i, result in enumerate(rag_results, 1):
            print(f"{i}. Source={result['source_id']} | Score={result['score']:.3f}")
            print(f" Text: «{result['text'][:70]}...»")
            metadata = result['source_details']
            print(f"Meta: {metadata.get('category', 'N/A')} | {metadata.get('emotion', 'N/A')}")

        # 6. Test filtered searches
        print("\n6. Testing filtered searches...")
        
        # Filter by type
        filtered_results = rag.search_external_sources(
            "AI systems",
            limit=2,
            source_type_filter=["txt"]
        )
        print(f" Filter by type 'txt': {len(filtered_results)} results")
        
        # Filter by source_id
        specific_results = rag.search_external_sources(
            "machine learning",
            limit=2,
            source_id_filter=["ai_research_2024"]
        )
        print(f" Filter by source_id: {len(specific_results)} results")

        # 7. Test memory update and feedback
        print("\nTesting memory update and feedback...")
        
        # Add new marker with different emotion
        new_marker_id = manager.update_network(
            "Quantum computing with qubits will revolutionize cryptography and optimization.",
            emotion="exciting"
        )
        print(f"New marker added: ID={new_marker_id} (emotion: exciting)")
        
        # Update reputation of existing marker if function exists
        if ids and hasattr(manager, 'update_marker_reputation'):
            target_marker = ids[0]
            manager.update_marker_reputation(target_marker, 1.5)
            updated_details = manager.get_marker_details(target_marker)
            new_reputation = updated_details.get('reputation', 0.0) if updated_details else 0.0
            print(f" ✓ Marker {target_marker} reputation updated → {new_reputation:.1f}")
        else:
            print("Function update_marker_reputation not available")

        # 8. Test full persistence
        print("\n8. Testing full persistence...")
        save_success = manager.save(str(SAVE_FILE))
        if not save_success:
            print("❌ Error saving")
            return False
        print("✓ Full state saved (base + RAG + emotions)")
        
        # Test reload
        print("Attempting reload...")
        reloaded_manager = StudSarManager.load(str(SAVE_FILE))
        if not reloaded_manager:
            print("❌ Error reloading")
            return False
            
        reloaded_markers = reloaded_manager.studsar_network.get_total_markers()
        print(f"✓ Reload successful: {reloaded_markers} markers restored")
        
        # Verify search works post-reload
        reload_ids, reload_sims, reload_segs = reloaded_manager.search("artificial intelligence", k=2)
        if reload_ids:
            print(f"✓ Post-reload search successful: {len(reload_ids)} results, sim={reload_sims[0]:.3f}")
        else:
            print("⚠️ No results post-reload")

        print("\n🎉 === TEST COMPLETED SUCCESSFULLY! ===")
        print(f""" ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⣴2⡶⠶⠶⠶⠶⠶⢦⡀⠀⠀
⠀⠀⠸⣿⣿⣿1⣶⣤⣄8⢀⠝⠀⠀
⠀⠀⠀⠈⢫0⠛⠻⠿⣿⡿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠙⢄⠀⢠0⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠓5⠀""") 
        print("RAG is perfectly integrated with StudSar!")
        print(f"Unified memory: {total_markers} markers (base + external)")
        print("Full support: emotions, persistence")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Verify that the project structure is correct")
        return False
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        traceback.print_exc()
        return False

    finally:
        # Guaranteed cleanup
        print("\n9. Cleanup...")
        cleanup_files = [TMP_DOC, SAVE_FILE]
        for file_path in cleanup_files:
            try:
                file_path.unlink(missing_ok=True)
                print(f"   Removed: {file_path.name}")
            except OSError as e:
                print(f"   Cleanup warning for {file_path.name}: {e}")


if __name__ == "__main__":
    test_rag_integration()