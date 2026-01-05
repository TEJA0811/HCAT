"""
Test client for the AI backend
"""
import httpx
import asyncio
import json


async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        print("Health Check Response:")
        print(json.dumps(response.json(), indent=2))
        print()


async def test_task_assignment(task_id: int = 1):
    """Test task assignment decision"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        print(f"Requesting AI decision for task {task_id}...")
        print("This may take 30-60 seconds as the AI analyzes the task...\n")
        
        response = await client.post(
            "http://localhost:8000/api/v1/decisions/task-assignment",
            json={"task_id": task_id}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("=" * 80)
            print("AI DECISION RESULT")
            print("=" * 80)
            print(f"\nTask: {result['task_title']}")
            print(f"Assigned to: {result['assigned_user_name']} (ID: {result['assigned_user_id']})")
            print(f"Confidence: {result['confidence']:.2%}")
            print("\n" + "-" * 80)
            print("EXPLANATION:")
            print("-" * 80)
            print(result['explanation'])
            print("\n" + "-" * 80)
            print("ETHICAL ANALYSIS:")
            print("-" * 80)
            print(json.dumps(result['ethical_analysis'], indent=2))
            print("\n" + "-" * 80)
            print("RISK ASSESSMENT:")
            print("-" * 80)
            print(json.dumps(result['risk_assessment'], indent=2))
            print("\n" + "-" * 80)
            print("REASONING TRACE:")
            print("-" * 80)
            for i, trace in enumerate(result['reasoning_trace'], 1):
                print(f"{i}. {trace}")
            print("\n" + "=" * 80)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def main():
    """Run all tests"""
    print("Testing AI Backend\n")
    
    # Test health check
    print("1. Testing Health Check...")
    await test_health_check()
    
    # Test task assignment for task 1
    print("2. Testing Task Assignment Decision for Task 1...")
    await test_task_assignment(task_id=1)


if __name__ == "__main__":
    asyncio.run(main())
