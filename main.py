# main.py
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.indexer import Indexer
from core.searcher import Searcher


# ============== SAMPLE DOCUMENTS ==============
def get_sample_documents():
    """Return a list of sample documents."""
    return [
        {"id": 1, "title": "Python Programming", "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming."},
        {"id": 2, "title": "Machine Learning Fundamentals", "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data without explicit programming. It includes supervised learning, unsupervised learning, and reinforcement learning."},
        {"id": 3, "title": "Data Structures and Algorithms", "content": "Data structures are ways to organize and store data efficiently. Common data structures include arrays, linked lists, stacks, queues, trees, graphs, and hash tables."},
        {"id": 4, "title": "Web Development with JavaScript", "content": "JavaScript is a programming language that enables interactive web pages. It is an essential part of web applications, along with HTML and CSS."},
        {"id": 5, "title": "Introduction to Database Systems", "content": "Database systems are software applications that store, organize, and manage data. SQL databases like MySQL and PostgreSQL use structured query language."},
        {"id": 6, "title": "Artificial Intelligence Overview", "content": "Artificial intelligence is the simulation of human intelligence in machines. It encompasses machine learning, natural language processing, computer vision, and robotics."},
        {"id": 7, "title": "Version Control with Git", "content": "Git is a distributed version control system that tracks changes in source code during software development. It enables collaboration through branching, merging, and pull requests."},
        {"id": 8, "title": "Cloud Computing Essentials", "content": "Cloud computing provides on-demand access to computing resources over the internet. Service models include Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS)."},
        {"id": 9, "title": "Cybersecurity Fundamentals", "content": "Cybersecurity is the practice of protecting computer systems, networks, and data from digital attacks. Key concepts include encryption, authentication, firewalls, and intrusion detection."},
        {"id": 10, "title": "Software Testing and Quality Assurance", "content": "Software testing validates that software works as expected. Testing types include unit testing, integration testing, system testing, and acceptance testing."},
    ]


# ============== COMMANDS ==============
def build_index():
    """Build the search index and save to disk."""
    print("📚 Loading documents...", flush=True)
    documents = get_sample_documents()
    
    if not documents:
        print("❌ No documents found. Add some documents first!")
        return
    
    print(f"✅ Loaded {len(documents)} documents")
    
    print("🔨 Building index...")
    indexer = Indexer(auto_load=False)  # Don't load, we're building fresh
    
    for doc in documents:
        indexer.add_document(doc["id"], doc["title"], doc["content"])
    
    print("📊 Calculating TF-IDF weights and norms...")
    indexer.finalize_index()
    
    print("💾 Saving index...")
    indexer.save_index()  # Uses default path "data/index_data.json"
    
    stats = indexer.get_stats()
    print("✅ Index built successfully!")
    print(f"   - Documents: {stats['total_docs']}")
    print(f"   - Unique terms: {stats['unique_terms']}")
    print(f"   - Total term occurrences: {stats['total_term_occurrences']}")


def search_command(query: str, k: int = 10):
    """Search using the saved index (CLI version)."""
    print(f"🔍 Searching for: '{query}'")
    
    try:
        # Indexer auto-loads the index
        indexer = Indexer()  # Uses default path "data/index_data.json"
        
        # Create searcher
        searcher = Searcher(indexer)
        
        # Execute search
        results = searcher.search(query, k)
        
        if not results:
            print("❌ No results found.", flush=True)
            return
        
        print(f"\n📊 Found {len(results)} results:\n", flush=True)
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['score']:.4f}] {result['title']}", flush=True)
            print(f"   {result['snippet'][:200]}...\n", flush=True)

        return result
            
    except FileNotFoundError:
        print("❌ Index not found. Run 'python main.py build' first.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def add_document():
    """Interactive document addition."""
    print("📝 Add a new document")
    title = input("Enter document title: ").strip()
    content = input("Enter document content: ").strip()
    
    if not title or not content:
        print("❌ Title and content are required.")
        return
    
    # Load existing index to get next ID
    try:
        indexer = Indexer()  # Loads existing index
        print(f"📚 Current documents: {len(indexer.documents)}")
    except FileNotFoundError:
        # No index exists yet
        indexer = Indexer(auto_load=False)
        print("📚 No existing index found. Starting fresh.")
    
    # Add the new document
    indexer.add_document(title, content)
    print(f"✅ Document added with ID: {len(indexer.documents)}")
    
    # Rebuild the index
    print("📊 Rebuilding index...")
    indexer.finalize_index()
    
    print("💾 Saving index...")
    indexer.save_index()
    
    stats = indexer.get_stats()
    print("✅ Index updated successfully!")
    print(f"   - Total documents: {stats['total_docs']}")
    print(f"   - Unique terms: {stats['unique_terms']}")


def start_server(port: int = 8000):
    """Start the web server."""
    try:
        from ui.server import run_server
        run_server(port)
    except ImportError:
        print("❌ Error: ui.server module not found.")
        print("   Make sure ui/server.py exists and has a run_server() function.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


def show_help():
    """Show help message."""
    print("""
🔍 Primitive Search Engine - Command Line Interface

Commands:
    python main.py build              - Build the search index from sample documents
    python main.py search <query>     - Search for documents (CLI)
    python main.py add                - Add a new document interactively
    python main.py serve              - Start the web server (port 8000)
    python main.py serve <port>       - Start the web server on specific port
    python main.py help               - Show this help message

Examples:
    python main.py build
    python main.py search "python programming"
    python main.py add
    python main.py serve
    python main.py serve 8080
""")


# ============== MAIN ENTRY POINT ==============
def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "build":
        build_index()
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            print("   Example: python main.py search 'python programming'")
            return
        query = " ".join(sys.argv[2:])
        k = 10  # Default
        search_command(query, k)
    
    elif command == "add":
        add_document()
    
    elif command == "serve" or command == "server":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        start_server(port)
    
    elif command in ["help", "--help", "-h"]:
        show_help()
    
    else:
        print(f"❌ Unknown command: '{command}'")
        print("   Run 'python main.py help' for available commands.")


if __name__ == "__main__":
    main()