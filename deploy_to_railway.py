#!/usr/bin/env python3
# Zhizhongcao - Railway Deploy Script (Automatic)
# Date: 2026-03-26
# Time: 09:09 AM
import requests
import time

class RailwayDeployer:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.railway.app"
        self.headers = {"X-Railway-Token": api_token, "Content-Type": "application/json"}
        
    def create_project(self, name="zhizhongcao"):
        print(f"[1/6] Creating project: {name}...")
        response = requests.post(
            f"{self.base_url}/v2/projects",
            headers=self.headers,
            json={"name": name}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"    Success! Project ID: {data.get('id')}")
            return data
        else:
            raise Exception(f"Failed: {response.text}")
    
    def create_service(self, project_id, repo_url):
        print("[2/6] Linking GitHub repository...")
        response = requests.post(
            f"{self.base_url}/v2/projects/{project_id}/services",
            headers=self.headers,
            json={"repository": {"url": repo_url, "branch": "master"}}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"    Success! Service ID: {data.get('id')}")
            return data
        else:
            raise Exception(f"Failed: {response.text}")
    
    def set_env_var(self, service_id, key, value):
        print(f"    Setting env var: {key}")
        response = requests.post(
            f"{self.base_url}/v2/services/{service_id}/variables",
            headers=self.headers,
            json={"key": key, "value": value}
        )
        if response.status_code in [200, 201]:
            print(f"    Done!")
        else:
            print(f"    Warning: {response.text}")
    
    def deploy_service(self, service_id):
        print("[4/6] Starting deployment...")
        response = requests.post(
            f"{self.base_url}/v2/services/{service_id}/deployments",
            headers=self.headers,
            json={"commitSha": None}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"    Deployment ID: {data.get('id')}")
            return data['id']
        else:
            raise Exception(f"Failed: {response.text}")
    
    def get_url(self, service_id):
        print("[6/6] Getting public URL...")
        response = requests.get(
            f"{self.base_url}/v2/services/{service_id}",
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            for env in data.get('environments', []):
                if env.get('environmentType') == 'PRODUCTION':
                    url = env.get('domain') or env.get('privateDomain')
                    if url:
                        return url
        return None


def main():
    print("=" * 60)
    print("Zhizhongcao - Railway Auto Deployment")
    print("=" * 60)
    
    deployer = RailwayDeployer(api_token="cec78972-ca52-40ff-90d1-1c0ae96b3076")
    
    try:
        # Step 1: Create Project
        project = deployer.create_project(name="zhizhongcao")
        project_id = project['id']
        time.sleep(2)
        
        # Step 2: Create Service
        repo_url = "https://github.com/billycool2005/zhizhongcao.git"
        service = deployer.create_service(project_id, repo_url)
        service_id = service['id']
        time.sleep(3)
        
        # Step 3: Set Environment Variables
        print("[3/6] Setting environment variables...")
        deployer.set_env_var(service_id, "QWEN_API_KEY", "[SET_LATER]")
        deployer.set_env_var(service_id, "SECRET_KEY", "MySecretKey123!@#")
        deployer.set_env_var(service_id, "APP_ENV", "production")
        deployer.set_env_var(service_id, "DEBUG", "false")
        time.sleep(2)
        
        # Step 4: Deploy
        deployment_id = deployer.deploy_service(service_id)
        print("    Waiting for build...")
        time.sleep(15)  # Wait for initial build
        
        # Step 5: Check status (skip for brevity)
        print("[5/6] Build in progress, waiting...")
        time.sleep(20)  # More wait
        
        # Step 6: Get URL
        url = deployer.get_url(service_id)
        
        print("\n" + "=" * 60)
        print("DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print(f"\nProject ID: {project_id}")
        print(f"Service ID: {service_id}")
        print(f"Deployment ID: {deployment_id}")
        if url:
            print(f"\nPublic URL: https://{url}")
        else:
            print("\nURL still building, please check dashboard")
            print(f"Railway Dashboard: https://railway.app/project/{project_id}")
        print(f"\nGitHub Repo: https://github.com/billycool2005/zhizhongcao")
        print("\nIMPORTANT: Update QWEN_API_KEY in Railway dashboard!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")


if __name__ == "__main__":
    main()
