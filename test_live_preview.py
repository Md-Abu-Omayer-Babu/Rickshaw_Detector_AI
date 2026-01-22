"""
Quick test script to verify live preview implementation.
Run this after starting the FastAPI backend.
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_async_video_upload():
    """Test async video upload endpoint."""
    print("=" * 60)
    print("Testing Async Video Upload with Live Preview")
    print("=" * 60)
    
    # Note: Replace with an actual video file path
    video_file_path = "test_video.mp4"
    
    try:
        # Upload video asynchronously
        print(f"\n1. Uploading video: {video_file_path}")
        with open(video_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BASE_URL}/api/detect/video/async",
                files=files,
                params={'enable_counting': 'true', 'camera_id': 'test_camera'}
            )
        
        if response.status_code == 200:
            data = response.json()
            job_id = data['job_id']
            print(f"✓ Video upload successful!")
            print(f"  Job ID: {job_id}")
            print(f"  Message: {data['message']}")
            
            # Test live stream URL
            stream_url = f"{BASE_URL}/api/stream/video/{job_id}"
            print(f"\n2. Live Preview Stream URL:")
            print(f"   {stream_url}")
            print(f"   → Open this URL in a browser to see live preview")
            
            # Poll job status
            print(f"\n3. Monitoring job status...")
            while True:
                status_response = requests.get(
                    f"{BASE_URL}/api/detect/video/status/{job_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    print(f"\r  Status: {status_data['status']} | "
                          f"Progress: {status_data['progress']:.1f}% | "
                          f"Frames: {status_data['processed_frames']}/{status_data['total_frames']}", 
                          end='', flush=True)
                    
                    if status_data['status'] == 'completed':
                        print("\n\n✓ Video processing completed!")
                        print(f"  Result:")
                        result = status_data['result']
                        print(f"    - File: {result['file_name']}")
                        print(f"    - Max Rickshaws: {result['rickshaw_count']}")
                        print(f"    - Total Entry: {result['total_entry']}")
                        print(f"    - Total Exit: {result['total_exit']}")
                        print(f"    - Net Count: {result['net_count']}")
                        print(f"    - Output URL: {result['output_url']}")
                        break
                    
                    elif status_data['status'] == 'failed':
                        print(f"\n\n✗ Video processing failed!")
                        print(f"  Error: {status_data.get('error', 'Unknown error')}")
                        break
                
                time.sleep(2)  # Poll every 2 seconds
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Error: {response.text}")
    
    except FileNotFoundError:
        print(f"✗ Error: Video file not found: {video_file_path}")
        print(f"  Please create a test video file or update the path.")
    except requests.exceptions.ConnectionError:
        print(f"✗ Error: Cannot connect to backend at {BASE_URL}")
        print(f"  Please ensure the FastAPI server is running:")
        print(f"    cd backend && python run.py")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")


def test_stream_endpoint():
    """Test that stream endpoint returns proper response."""
    print("\n" + "=" * 60)
    print("Testing Stream Endpoint (with dummy job_id)")
    print("=" * 60)
    
    dummy_job_id = "test-job-id"
    stream_url = f"{BASE_URL}/api/stream/video/{dummy_job_id}"
    
    print(f"\nAttempting to access stream: {stream_url}")
    
    try:
        response = requests.get(stream_url, stream=True, timeout=5)
        
        if response.status_code == 404:
            print("✓ Endpoint exists and returns 404 for unknown job (expected)")
        elif response.status_code == 200:
            print("✓ Stream endpoint is accessible")
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    print("\n🎥 Live Preview Feature Test Script")
    print("=" * 60)
    print("Prerequisites:")
    print("1. Backend server running: python backend/run.py")
    print("2. Test video file available (or update video_file_path)")
    print("=" * 60)
    
    # Test endpoints
    test_stream_endpoint()
    
    print("\n\nTo test full workflow:")
    print("1. Update 'video_file_path' variable in this script")
    print("2. Uncomment the line below and run again")
    print("=" * 60)
    
    # Uncomment to test full workflow:
    # test_async_video_upload()
