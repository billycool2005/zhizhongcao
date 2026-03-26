#!/usr/bin/env python3
# Zhizhongcao - Railway Deploy Script v2
# Using Railway's direct import feature

import requests
import time
import os

API_TOKEN = "cec78972-ca52-40ff-90d1-1c0ae96b3076"
GITHUB_REPO = "https://github.com/billycool2005/zhizhongcao.git"

print("=" * 70)
print("Zhizhongcao - Railway Deployment (v2)")
print("=" * 70)

headers = {
    "X-Railway-Token": API_TOKEN,
    "Content-Type": "application/json"
}

# Step 1: Try to get projects first
print("\n[Step 1] Checking existing projects...")
response = requests.get(
    "https://api.railway.app/v2/projects",
    headers=headers
)

if response.status_code == 200:
    print("   Success! Token is valid.")
    projects = response.json()
    print(f"   Found {len(projects)} existing project(s)")
else:
    print(f"   Status code: {response.status_code}")
    print(f"   Error: {response.text[:200]}")
    
    # Maybe the token format is wrong, let's check documentation
    print("\n   Note: Railway API might need bearer prefix")
    print("   Trying with 'Bearer' prefix...")

# Step 2: Try with Bearer prefix
headers_bearer = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("\n[Step 2] Testing with Bearer auth...")
response = requests.get(
    "https://api.railway.app/v2/projects",
    headers=headers_bearer
)

if response.status_code == 200:
    print("   Success! Bearer auth works.")
    projects = response.json()
    print(f"   Projects found: {len(projects)}")
else:
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:300]}")

# Step 3: Create project using POST
print("\n[Step 3] Creating new project...")
create_payload = {
    "name": "zhizhongcao",
    "isPrivate": False
}

response = requests.post(
    "https://api.railway.app/v2/projects",
    headers=headers_bearer,
    json=create_payload
)

if response.status_code == 200 or response.status_code == 201:
    project_data = response.json()
    project_id = project_data.get('id')
    print(f"   SUCCESS! Project created.")
    print(f"   Project ID: {project_id}")
    
    # Step 4: Add GitHub repository
    print("\n[Step 4] Adding GitHub repository...")
    service_payload = {
        "repository": {
            "url": GITHUB_REPO,
            "branch": "master"
        }
    }
    
    response = requests.post(
        f"https://api.railway.app/v2/projects/{project_id}/services",
        headers=headers_bearer,
        json=service_payload
    )
    
    if response.status_code == 200 or response.status_code == 201:
        service_data = response.json()
        service_id = service_data.get('id')
        print(f"   SUCCESS! Service created.")
        print(f"   Service ID: {service_id}")
        
        # Step 5: Set environment variables
        print("\n[Step 5] Setting environment variables...")
        env_vars = [
            {"key": "QWEN_API_KEY", "value": "[SET_LATER]"},
            {"key": "SECRET_KEY", "value": "MySecretKey123!@#"},
            {"key": "APP_ENV", "value": "production"},
            {"key": "DEBUG", "value": "false"}
        ]
        
        for env in env_vars:
            resp = requests.post(
                f"https://api.railway.app/v2/services/{service_id}/variables",
                headers=headers_bearer,
                json=env
            )
            status = "Done!" if resp.status_code in [200, 201] else "Warning"
            print(f"   {env['key']}: {status}")
        
        # Step 6: Trigger deployment
        print("\n[Step 6] Triggering deployment...")
        deploy_payload = {"commitSha": None}
        response = requests.post(
            f"https://api.railway.app/v2/services/{service_id}/deployments",
            headers=headers_bearer,
            json=deploy_payload
        )
        
        if response.status_code == 200:
            deployment_data = response.json()
            deployment_id = deployment_data.get('id')
            print(f"   SUCCESS! Deployment triggered.")
            print(f"   Deployment ID: {deployment_id}")
            
            print("\n" + "=" * 70)
            print("DEPLOYMENT INITIATED!")
            print("=" * 70)
            print(f"\nProject ID: {project_id}")
            print(f"Service ID: {service_id}")
            print(f"Deployment ID: {deployment_id}")
            print(f"\nGitHub Repo: https://github.com/billycool2005/zhizhongcao")
            print(f"Railway Dashboard: https://railway.app/project/{project_id}")
            print("\nIMPORTANT:")
            print("- Wait ~5-10 minutes for build to complete")
            print("- Update QWEN_API_KEY in Railway dashboard")
            print("- Check deployment status at: /v2/services/{service_id}/deployments")
            print("=" * 70)
        else:
            print(f"   Failed to trigger deployment: {response.text}")
    else:
        print(f"   Failed to create service: {response.text}")
else:
    print(f"Failed to create project: {response.text}")
    print("\nAlternative approach:")
    print("Please manually deploy via Railway web interface:")
    print("1. Go to: https://railway.app/login")
    print("2. Sign in with GitHub (billycool2005)")
    print("3. Click 'New Project' -> 'Deploy from GitHub'")
    print("4. Select 'billycool2005/zhizhongcao'")
    print("5. Click 'Deploy'")
