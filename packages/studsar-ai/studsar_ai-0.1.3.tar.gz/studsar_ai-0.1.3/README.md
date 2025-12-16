# StudSAR-AI: RAG Evaluation

## Project Overview

This project implements and evaluates a Retrieval Augmented Generation (RAG) system, StudSAR, designed to enhance the accuracy and relevance of AI-generated responses by integrating a robust retrieval mechanism with a language model. The system is compared against a traditional RAG approach to highlight its advantages.

## Implementation Details

The core of the project is built around a Gradio web interface, allowing for interactive demonstrations and comparisons between StudSAR and Traditional RAG. Key components include:

-   **StudSAR RAG**: Utilizes a neural search approach for document retrieval, aiming for more semantically relevant results.
-   **Traditional RAG**: Employs a keyword-based or simpler retrieval method for baseline comparison.
-   **Evaluation Metrics**: A custom evaluation framework assesses both systems based on relevance, completeness, accuracy, and semantic similarity.

## Technical Approach

1.  **Data Loading and Processing**: Sample documents are loaded and processed to create a knowledge base for both RAG systems.
2.  **Retrieval**: StudSAR uses a `SentenceTransformer` model for embedding queries and documents, enabling semantic search. Traditional RAG uses simpler keyword matching.
3.  **Generation**: (Implicit) The retrieved information is intended to augment a language model's generation capabilities, though the language model itself is abstracted for this comparison.
4.  **Evaluation**: A `evaluate_rag_systems` function compares the outputs of both systems using a combination of keyword matching, semantic similarity (cosine similarity of embeddings), and a simplified coherence score.

## Key Observations from `app.py`

-   **Dynamic Document Loading**: The `sample_docs` dictionary in `app.py` demonstrates how various AI-related topics are used as source material.
-   **Modular Design**: The `StudSarManager` and `TraditionalRAG` classes (from `src.managers.manager` and `traditional_rag.py` respectively) encapsulate the logic for each RAG system.
-   **Interactive Interface**: Gradio is used to create a user-friendly interface where users can input queries and see comparative results and evaluation scores.
-   **Evaluation Logic**: The `evaluate_rag_systems` function calculates scores for relevance, completeness, accuracy, and semantic similarity, providing a quantitative comparison.

## Usage

### Setup and Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/your-username/StudSAR.git
    cd StudSAR
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the Gradio application locally, navigate to the `StudSar` directory and execute the following command:

```bash
cd StudSar
python app.py
```

The application will typically be available at `http://localhost:7860` or a similar address provided in the console output.

### Deployment to Hugging Face Spaces

This application can be easily deployed to Hugging Face Spaces. Ensure your `app.py` and `requirements.txt` files are in the root directory of your Space. Hugging Face Spaces will automatically detect and run the Gradio application.

## Repository Structure

```
StudSar/
├── app.py                  # Main Gradio application and evaluation logic
├── requirements.txt        # Python dependencies
├── src/
│   ├── managers/           # Contains StudSarManager for neural RAG
│   │   └── manager.py
│   ├── models/             # (Potentially) Neural network models or components
│   │   └── neural.py
│   ├── rag/                # RAG-related utilities or base classes
│   │   └── rag_connector.py
│   ├── studsar.py          # Core StudSAR implementation
│   └── utils/              # Utility functions (e.g., text processing)
│       └── text.py
├── traditional_rag.py      # Implementation of the traditional RAG system
├── temp_docs/              # Sample documents for RAG knowledge base
├── examples/               # Example usage scripts
├── tests/                  # Unit and integration tests
└── studsar_neural_demo.pth # Pre-trained model weights (if applicable)
```

## Performance Analysis

The evaluation metrics within `app.py` provide a direct comparison:

-   **Relevance**: Measured by keyword overlap.
-   **Completeness**: Assessed by the proportion of query keywords found in results.
-   **Accuracy**: Determined by semantic similarity to the query.
-   **Semantic Similarity**: Cosine similarity between query and result embeddings.

StudSAR is designed to outperform Traditional RAG in semantic understanding and retrieval accuracy, leading to higher scores in these metrics.

## References

-   **Gradio**: For building the interactive web interface.
-   **Sentence Transformers**: For generating embeddings for semantic search.
-   **Hugging Face Spaces**: For easy deployment and sharing of the application.
