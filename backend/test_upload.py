import httpx
import asyncio

async def test_upload():
    # Test the upload endpoint
    with open(r'C:\Laxman\SIH\cyber-graph\backend\uploads\test_cicids.csv', 'rb') as f:
        files = {'file': ('test_cicids.csv', f, 'text/csv')}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post('http://localhost:8000/api/logs/upload', files=files)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_upload())
