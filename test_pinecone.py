import os
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pinecone_connection():
    """Test connection to Pinecone."""
    try:
        # Get credentials from environment
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("INDEX_NAME", "policy-assistant")
        
        if not api_key:
            print("ERROR: Pinecone API key must be set in .env file")
            return False
        
        print(f"Connecting to Pinecone...")
        print(f"Using index name: {index_name}")
        print(f"Expected configuration:")
        print(f"- Host: https://policy-assistant-emvpjns.svc.aped-4627-b74a.pinecone.io")
        print(f"- Dimension: 384")
        print(f"- Metric: cosine")
        print(f"- Region: us-east-1")
        print(f"- Cloud: aws")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # List available indexes
        indexes = pc.list_indexes()
        index_names = indexes.names() if hasattr(indexes, 'names') else [i['name'] for i in indexes]
        print(f"Available indexes: {index_names}")
        
        # Check if our index exists
        if index_name in index_names:
            print(f"✅ Index '{index_name}' exists")
            # Get index stats
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"Index stats: {stats}")
            return True
        else:
            print(f"⚠️ Index '{index_name}' does not exist yet")
            print("It will be created when you first run the ingest script")
            return True
            
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Pinecone connection...")
    success = test_pinecone_connection()
    if success:
        print("\n✅ Pinecone connection successful!")
    else:
        print("\n❌ Pinecone connection failed. Please check your credentials.")
