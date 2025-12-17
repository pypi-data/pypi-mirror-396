"""
Test script to troubleshoot Qdrant connection
"""

import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import time

def test_qdrant_connection():
    """Test various connection methods to Qdrant"""

    print("="*60)
    print("Qdrant Connection Test")
    print("="*60)

    # Configuration
    configs_to_test = [
        {
            "name": "HTTPS with API Key (full URL with port)",
            "url": "https://qdrant.powerkit.dev",
            "port": 443,
            "api_key": "QpzCZkDvgUGAqwIN9jMSYRhaGczAb5n4",
            "use_host": False
        },
        {
            "name": "HTTPS with API Key (URL only)",
            "url": "https://qdrant.powerkit.dev:443",
            "api_key": "QpzCZkDvgUGAqwIN9jMSYRhaGczAb5n4",
            "use_host": False
        },
        {
            "name": "HTTPS with API Key (no port)",
            "url": "https://qdrant.powerkit.dev",
            "api_key": "QpzCZkDvgUGAqwIN9jMSYRhaGczAb5n4",
            "use_host": False
        },
        {
            "name": "Host mode with HTTPS",
            "host": "qdrant.powerkit.dev",
            "port": 443,
            "api_key": "QpzCZkDvgUGAqwIN9jMSYRhaGczAb5n4",
            "use_host": True,
            "https": True
        },
        {
            "name": "Host mode without HTTPS",
            "host": "qdrant.powerkit.dev",
            "port": 443,
            "api_key": "QpzCZkDvgUGAqwIN9jMSYRhaGczAb5n4",
            "use_host": True,
            "https": False
        },
    ]

    for config in configs_to_test:
        print(f"\n{'='*60}")
        print(f"Testing: {config['name']}")
        print(f"{'='*60}")

        try:
            # Initialize client
            if config.get("use_host"):
                print(f"Connecting with host={config.get('host')}, port={config.get('port')}, https={config.get('https')}")
                client = QdrantClient(
                    host=config.get("host"),
                    port=config.get("port"),
                    api_key=config.get("api_key"),
                    https=config.get("https", True),
                    timeout=10
                )
            else:
                if "port" in config:
                    print(f"Connecting with url={config.get('url')}, port={config.get('port')}")
                    client = QdrantClient(
                        url=config.get("url"),
                        port=config.get("port"),
                        api_key=config.get("api_key"),
                        timeout=10
                    )
                else:
                    print(f"Connecting with url={config.get('url')}")
                    client = QdrantClient(
                        url=config.get("url"),
                        api_key=config.get("api_key"),
                        timeout=10
                    )

            print("Client created successfully!")

            # Try to get collections
            print("Attempting to list collections...")
            collections = client.get_collections()
            print(f"Success! Found {len(collections.collections)} collections:")
            for coll in collections.collections:
                print(f"  - {coll.name}")

            # Try to create a test collection
            test_collection_name = "test_connection_collection"
            print(f"\nAttempting to create test collection '{test_collection_name}'...")

            try:
                client.create_collection(
                    collection_name=test_collection_name,
                    vectors_config=VectorParams(size=128, distance=Distance.COSINE)
                )
                print(f"Test collection created successfully!")

                # Clean up - delete the test collection
                print(f"Cleaning up - deleting test collection...")
                client.delete_collection(test_collection_name)
                print(f"Test collection deleted successfully!")

            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"Collection already exists (this is OK)")
                    # Try to delete it
                    try:
                        client.delete_collection(test_collection_name)
                        print(f"Cleaned up existing test collection")
                    except:
                        pass
                else:
                    raise

            print(f"\n✓ Connection method '{config['name']}' WORKS!")
            print("="*60)

            # If we got here, this config works - no need to test others
            return client, config

        except Exception as e:
            print(f"\n✗ Connection method '{config['name']}' FAILED!")
            print(f"Error: {type(e).__name__}: {e}")
            print("="*60)
            continue

    print("\n" + "="*60)
    print("All connection methods failed!")
    print("="*60)
    return None, None


def main():
    client, working_config = test_qdrant_connection()

    if client and working_config:
        print("\n" + "="*60)
        print("RECOMMENDED CONFIGURATION:")
        print("="*60)
        for key, value in working_config.items():
            if key != "name":
                print(f"{key}: {value}")
        print("="*60)
    else:
        print("\nTroubleshooting tips:")
        print("1. Verify your Qdrant server is running and accessible")
        print("2. Check your API key is correct")
        print("3. Verify the URL and port are correct")
        print("4. Check if there are any firewall rules blocking the connection")
        print("5. Try accessing the Qdrant dashboard directly in your browser")


if __name__ == "__main__":
    main()
