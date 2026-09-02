import httpx
import asyncio

async def test_upload():
    test_files = [
        'C:\\Laxman\\SIH\\cyber-graph\\backend\\uploads\\test_cicids.csv',
        'C:\\Laxman\\SIH\\cyber-graph\\backend\\uploads\\test_cicids2_proper.csv'
    ]
    
    for filepath in test_files:
        print(f"\n=== Testing {filepath.split(chr(92))[-1]} ===")
        with open(filepath, 'rb') as f:
            files = {'file': (filepath.split(chr(92))[-1], f, 'text/csv')}
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post('http://localhost:8000/api/logs/upload', files=files)
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text[:500]}")
            except Exception as e:
                print(f"Error: {e}")

asyncio.run(test_upload())
