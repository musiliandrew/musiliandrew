#!/usr/bin/env python3
import requests
import json
import os
from collections import defaultdict
import re

# Tech stack mapping with shield badges
TECH_MAPPING = {
    # Languages
    'Python': '![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)',
    'JavaScript': '![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)',
    'TypeScript': '![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)',
    'Java': '![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)',
    'Go': '![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)',
    'Rust': '![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)',
    'C++': '![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)',
    'C': '![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)',
    'PHP': '![PHP](https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white)',
    'Ruby': '![Ruby](https://img.shields.io/badge/Ruby-CC342D?style=for-the-badge&logo=ruby&logoColor=white)',
    'Swift': '![Swift](https://img.shields.io/badge/Swift-FA7343?style=for-the-badge&logo=swift&logoColor=white)',
    'Kotlin': '![Kotlin](https://img.shields.io/badge/Kotlin-0095D5?style=for-the-badge&logo=kotlin&logoColor=white)',
    'Dart': '![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)',
    'Shell': '![Shell Script](https://img.shields.io/badge/Shell_Script-121011?style=for-the-badge&logo=gnu-bash&logoColor=white)',
    
    # Frontend Frameworks
    'React': '![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)',
    'Next.js': '![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)',
    'Vue': '![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)',
    'Angular': '![Angular](https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white)',
    'Svelte': '![Svelte](https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00)',
    
    # Backend Frameworks
    'Django': '![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)',
    'FastAPI': '![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)',
    'Flask': '![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)',
    'Express': '![Express.js](https://img.shields.io/badge/Express.js-404D59?style=for-the-badge)',
    'Node.js': '![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)',
    'Spring': '![Spring](https://img.shields.io/badge/Spring-6DB33F?style=for-the-badge&logo=spring&logoColor=white)',
    
    # Databases
    'PostgreSQL': '![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)',
    'MongoDB': '![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)',
    'Redis': '![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)',
    'MySQL': '![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)',
    'SQLite': '![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)',
    
    # AI/ML
    'TensorFlow': '![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)',
    'PyTorch': '![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)',
    'OpenAI': '![OpenAI](https://img.shields.io/badge/OpenAI-74aa9c?style=for-the-badge&logo=openai&logoColor=white)',
    'Transformers': '![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)',
    
    # Cloud & DevOps
    'Docker': '![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)',
    'Kubernetes': '![Kubernetes](https://img.shields.io/badge/Kubernetes-326ce5?style=for-the-badge&logo=kubernetes&logoColor=white)',
    'AWS': '![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)',
    'GCP': '![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)',
    'Azure': '![Azure](https://img.shields.io/badge/Microsoft_Azure-0089D0?style=for-the-badge&logo=microsoft-azure&logoColor=white)',
}

class GitHubRepoAnalyzer:
    def __init__(self, username, token=None):
        self.username = username
        self.token = token
        self.headers = {'Authorization': f'token {token}'} if token else {}
        self.tech_usage = defaultdict(int)
        
    def get_repositories(self):
        """Fetch all public repositories"""
        repos = []
        page = 1
        
        while True:
            url = f"https://api.github.com/users/{self.username}/repos?page={page}&per_page=100"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Error fetching repos: {response.status_code}")
                break
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        return repos
    
    def analyze_package_files(self, repo):
        """Analyze package files to detect frameworks/libraries"""
        files_to_check = [
            'package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml',
            'go.mod', 'composer.json', 'Pipfile', 'pyproject.toml'
        ]
        
        for file_name in files_to_check:
            try:
                url = f"https://api.github.com/repos/{self.username}/{repo['name']}/contents/{file_name}"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    content = response.json()
                    if content['type'] == 'file':
                        # Decode base64 content
                        import base64
                        file_content = base64.b64decode(content['content']).decode('utf-8')
                        self.analyze_file_content(file_name, file_content)
                        
            except Exception as e:
                continue
    
    def analyze_file_content(self, filename, content):
        """Analyze file content for technologies"""
        content_lower = content.lower()
        
        if filename == 'package.json':
            try:
                data = json.loads(content)
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                for dep in deps.keys():
                    if 'react' in dep and 'native' not in dep:
                        self.tech_usage['React'] += 5
                    elif 'next' in dep:
                        self.tech_usage['Next.js'] += 5
                    elif 'vue' in dep:
                        self.tech_usage['Vue'] += 5
                    elif 'angular' in dep:
                        self.tech_usage['Angular'] += 5
                    elif 'svelte' in dep:
                        self.tech_usage['Svelte'] += 5
                    elif 'express' in dep:
                        self.tech_usage['Express'] += 5
                        
            except json.JSONDecodeError:
                pass
                
        elif filename == 'requirements.txt' or filename == 'pyproject.toml':
            if 'django' in content_lower:
                self.tech_usage['Django'] += 5
            if 'fastapi' in content_lower:
                self.tech_usage['FastAPI'] += 5
            if 'flask' in content_lower:
                self.tech_usage['Flask'] += 5
            if 'tensorflow' in content_lower:
                self.tech_usage['TensorFlow'] += 5
            if 'torch' in content_lower or 'pytorch' in content_lower:
                self.tech_usage['PyTorch'] += 5
            if 'transformers' in content_lower:
                self.tech_usage['Transformers'] += 5
            if 'openai' in content_lower:
                self.tech_usage['OpenAI'] += 5
                
        elif filename == 'Dockerfile':
            if 'postgres' in content_lower:
                self.tech_usage['PostgreSQL'] += 3
            if 'mongo' in content_lower:
                self.tech_usage['MongoDB'] += 3
            if 'redis' in content_lower:
                self.tech_usage['Redis'] += 3
            if 'mysql' in content_lower:
                self.tech_usage['MySQL'] += 3
    
    def analyze_repository_languages(self, repos):
        """Analyze programming languages from GitHub API"""
        for repo in repos:
            if repo['fork'] or repo['archived']:
                continue
                
            try:
                url = f"https://api.github.com/repos/{self.username}/{repo['name']}/languages"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    languages = response.json()
                    for lang, bytes_count in languages.items():
                        # Weight by lines of code
                        weight = min(bytes_count // 1000, 10)  # Cap at 10 points per repo
                        self.tech_usage[lang] += weight
                        
                        # Detect Node.js from JavaScript repos
                        if lang == 'JavaScript':
                            self.tech_usage['Node.js'] += weight // 2
                            
            except Exception as e:
                continue
                
            # Analyze package files for this repo
            self.analyze_package_files(repo)
    
    def generate_tech_badges(self):
        """Generate shield badges for detected technologies"""
        badges = {
            'languages': [],
            'frontend': [],
            'backend': [],
            'ai_ml': [],
            'databases': [],
            'cloud_devops': []
        }
        
        # Sort by usage count
        sorted_tech = sorted(self.tech_usage.items(), key=lambda x: x[1], reverse=True)
        
        for tech, count in sorted_tech:
            if count < 2:  # Only include tech with significant usage
                continue
                
            if tech in TECH_MAPPING:
                badge = TECH_MAPPING[tech]
                
                # Categorize
                if tech in ['Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust', 'C++', 'C', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Dart', 'Shell']:
                    badges['languages'].append(badge)
                elif tech in ['React', 'Next.js', 'Vue', 'Angular', 'Svelte']:
                    badges['frontend'].append(badge)
                elif tech in ['Django', 'FastAPI', 'Flask', 'Express', 'Node.js', 'Spring']:
                    badges['backend'].append(badge)
                elif tech in ['TensorFlow', 'PyTorch', 'OpenAI', 'Transformers']:
                    badges['ai_ml'].append(badge)
                elif tech in ['PostgreSQL', 'MongoDB', 'Redis', 'MySQL', 'SQLite']:
                    badges['databases'].append(badge)
                elif tech in ['Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure']:
                    badges['cloud_devops'].append(badge)
        
        return badges
    
    def update_readme(self, badges):
        """Update README with detected tech stack"""
        readme_path = 'README.md'
        
        try:
            with open(readme_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print("README.md not found")
            return
        
        # Build tech stack section
        tech_section = "\n## 🛠️ Technology Stack\n\n"
        
        if badges['languages']:
            tech_section += "### 🔥 Languages\n"
            tech_section += "\n".join(badges['languages']) + "\n\n"
            
        if badges['frontend']:
            tech_section += "### ⚡ Frontend\n"
            tech_section += "\n".join(badges['frontend']) + "\n\n"
            
        if badges['backend']:
            tech_section += "### 🔧 Backend\n"
            tech_section += "\n".join(badges['backend']) + "\n\n"
            
        if badges['ai_ml']:
            tech_section += "### 🤖 AI/ML\n"
            tech_section += "\n".join(badges['ai_ml']) + "\n\n"
            
        if badges['databases']:
            tech_section += "### 🗄️ Databases\n"
            tech_section += "\n".join(badges['databases']) + "\n\n"
            
        if badges['cloud_devops']:
            tech_section += "### ☁️ Cloud & DevOps\n"
            tech_section += "\n".join(badges['cloud_devops']) + "\n\n"
        
        # Replace the tech stack section
        import re
        pattern = r'## 🛠️ Technology Stack.*?(?=## |\Z)'
        new_content = re.sub(pattern, tech_section, content, flags=re.DOTALL)
        
        with open(readme_path, 'w') as f:
            f.write(new_content)
        
        print("✅ README updated with detected tech stack!")

def main():
    username = "musiliandrew"  # Your GitHub username
    token = os.getenv('GITHUB_TOKEN')  # GitHub token from environment
    
    if not token:
        print("❌ No GITHUB_TOKEN found!")
        return
    
    analyzer = GitHubRepoAnalyzer(username, token)
    
    print("🔍 Fetching repositories...")
    repos = analyzer.get_repositories()
    print(f"📦 Found {len(repos)} repositories")
    
    # Show first few repos for debugging
    for i, repo in enumerate(repos[:5]):
        print(f"  {i+1}. {repo['name']} ({repo.get('language', 'Unknown')})")
    
    print("🔬 Analyzing technologies...")
    analyzer.analyze_repository_languages(repos)
    
    # Debug: Show detected technologies
    print(f"🔍 Detected technologies: {dict(analyzer.tech_usage)}")
    
    print("🎨 Generating badges...")
    badges = analyzer.generate_tech_badges()
    
    # Debug: Show generated badges
    for category, badge_list in badges.items():
        if badge_list:
            print(f"  {category}: {len(badge_list)} badges")
    
    print("📝 Updating README...")
    analyzer.update_readme(badges)
    
    print(f"🚀 Tech analysis complete! Found {len(analyzer.tech_usage)} technologies.")

if __name__ == "__main__":
    main()