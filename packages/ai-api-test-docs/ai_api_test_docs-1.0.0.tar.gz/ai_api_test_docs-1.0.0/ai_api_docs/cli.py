import os
import re
import google.generativeai as genai
from dotenv import load_dotenv, set_key, unset_key
import textwrap
import mimetypes
import sys

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

model = None

def ensure_api_key():
    """Ensure Gemini API key is set, prompt and store if missing."""
    load_dotenv(ENV_PATH)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Gemini API key not found.")
        api_key = input("Please enter your Gemini API key: ").strip()
        if api_key:
            set_key(ENV_PATH, "GOOGLE_API_KEY", api_key)
            print("API key saved securely in .env file.")
        else:
            print("No API key provided. Exiting.")
            exit(1)
    return api_key

def delete_api_key():
    """Delete the stored Gemini API key from .env."""
    load_dotenv(ENV_PATH)
    if os.getenv("GOOGLE_API_KEY"):
        unset_key(ENV_PATH, "GOOGLE_API_KEY")
        print("API key deleted from .env.")
    else:
        print("No API key found to delete.")

def list_folders():
    """List directories and let user select one"""
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    if not folders:
        print("No folders found!")
        exit(1)
        
    print("Select a folder:")
    for idx, folder in enumerate(folders):
        print(f"{chr(97+idx)}. {folder}")
    
    choice = input("User input: ").strip().lower()
    try:
        return folders[ord(choice) - 97]
    except (IndexError, ValueError):
        print("Invalid choice.")
        exit(1)

def is_text_file(filepath):
    """Check if file is text-based"""
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith('text/'):
        return True
    
    # Check common code extensions
    code_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', 
                       '.cs', '.cpp', '.h', '.swift', '.kt', '.rs', '.dart']
    if any(filepath.endswith(ext) for ext in code_extensions):
        return True
    
    # Check common config files
    config_files = ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle', 
                   'dockerfile', 'docker-compose.yml', '.env', 'config.yml']
    if any(filepath.endswith(f) for f in config_files):
        return True
    
    return False

def scan_entire_project(folder_path):
    """Scan entire project without truncation, return list of file contents with metadata"""
    project_files = []
    
    # Prioritize key directories
    priority_dirs = ['app', 'src', 'lib', 'api', 'routes', 'controllers', 'views', 'test']
    priority_files = ['routes', 'urls', 'controllers', 'views', 'app', 'main', 'server']
    
    # Walk through project directory
    for root, _, files in os.walk(folder_path):
        # Skip virtual environments and hidden directories
        if any(part.startswith('.') or part in ('venv', 'env', 'node_modules') for part in root.split(os.sep)):
            continue
            
        # Prioritize key directories
        dir_priority = 1
        for pdir in priority_dirs:
            if pdir in root.split(os.sep):
                dir_priority = 3
                break
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, folder_path)
            
            # Skip binary files
            if not is_text_file(file_path):
                continue
                
            # Calculate file priority
            file_priority = dir_priority
            for pfile in priority_files:
                if pfile in file.lower():
                    file_priority = 5  # Highest priority
                    break
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
                
                # Add to context with metadata
                project_files.append({
                    'priority': file_priority,
                    'rel_path': rel_path,
                    'content': file_content
                })
            except Exception as e:
                print(f"Could not read {file_path}: {str(e)}")
    
    # Sort by priority (highest first)
    project_files.sort(key=lambda x: x['priority'], reverse=True)
    
    return project_files

def process_in_batches(project_files, processing_function, tech_stack, max_batch_chars=100000):
    """Process files in batches to stay within token limits"""
    current_batch = []
    current_batch_size = 0
    results = []
    
    for file_info in project_files:
        file_size = len(file_info['content'])
        
        # If adding this file would exceed batch size, process current batch first
        if current_batch_size + file_size > max_batch_chars and current_batch:
            context_str = "\n".join(
                f"## File: {item['rel_path']}\n{item['content']}\n"
                for item in current_batch
            )
            results.append(processing_function(context_str, tech_stack))
            current_batch = []
            current_batch_size = 0
        
        current_batch.append(file_info)
        current_batch_size += file_size
    
    # Process any remaining files in the last batch
    if current_batch:
        context_str = "\n".join(
            f"## File: {item['rel_path']}\n{item['content']}\n"
            for item in current_batch
        )
        results.append(processing_function(context_str, tech_stack))
    
    return "\n\n".join(results)

def ai_suggest_framework(project_files):
    """Detect framework using AI analysis with batched processing"""
    # Use first batch for framework detection (most important files)
    context_str = "\n".join(
        f"## File: {item['rel_path']}\n{item['content']}\n"
        for item in project_files[:20]  # Use top 20 files for framework detection
    )
    
    prompt = textwrap.dedent(f"""
    Analyze the following project structure and codebase to determine the:
    1. Programming language
    2. Web framework
    3. Key libraries
    
    Respond in this EXACT format without additional text:
    Language: <language>
    Framework: <framework>
    Libraries: <comma-separated list>
    
    Project context:
    {context_str}
    """)
    
    response = model.generate_content(prompt)
    return parse_ai_response(response.text)

def parse_ai_response(response_text):
    """Parse AI response into structured data"""
    result = {
        'language': 'Unknown',
        'framework': 'Unknown',
        'libraries': []
    }
    
    try:
        for line in response_text.split('\n'):
            if line.startswith('Language:'):
                result['language'] = line.split(':', 1)[1].strip()
            elif line.startswith('Framework:'):
                result['framework'] = line.split(':', 1)[1].strip()
            elif line.startswith('Libraries:'):
                libs = line.split(':', 1)[1].strip()
                result['libraries'] = [lib.strip() for lib in libs.split(',')]
    except Exception:
        pass
    
    return result

def generate_api_tests_batched(project_files, tech_stack):
    """Generate API tests using AI with batched project context"""
    return process_in_batches(
        project_files,
        lambda context, ts: generate_api_tests_single(context, ts),
        tech_stack
    )

def generate_api_tests_single(context_str, tech_stack):
    """Generate API tests for a single batch"""
    prompt = textwrap.dedent(f"""
    You are an expert QA engineer. Generate comprehensive API tests for the project below.
    
    Project Tech Stack:
    - Language: {tech_stack['language']}
    - Framework: {tech_stack['framework']}
    - Libraries: {', '.join(tech_stack['libraries'])}
    
    Requirements:
    1. Create tests for API endpoints found in this batch
    2. Cover success and error cases
    3. Include authentication tests where applicable
    4. Use appropriate testing libraries for the tech stack
    5. Include setup/teardown for database state
    6. Test all HTTP methods (GET, POST, PUT, DELETE, etc.)
    7. Validate response structures and status codes
    
    Project Context:
    {context_str}
    
    Output ONLY the test code without any explanations or markdown formatting.
    """)
    
    response = model.generate_content(prompt)
    return response.text

def generate_api_docs_batched(project_files, tech_stack):
    """Generate API docs using AI with batched project context"""
    return process_in_batches(
        project_files,
        lambda context, ts: generate_api_docs_single(context, ts),
        tech_stack
    )

def generate_api_docs_single(context_str, tech_stack):
    """Generate API docs for a single batch"""
    prompt = textwrap.dedent(f"""
    You are an API documentation specialist. Generate **strictly accurate Markdown documentation** using ONLY the provided context. 
    Follow these rules absolutely:
    1. **NEVER invent endpoints, parameters, or codes** - use ONLY what exists in context
    2. **Extract request/response bodies VERBATIM** from context examples where available
    3. **Reject defaults** - if context doesn't specify "required", omit it; if no examples exist, omit sections

    ### Anti-Hallucination Protocol:
    - For response examples: **ONLY use hardcoded strings** found in context (search for JSON blocks, test fixtures, examples)
    - If status codes aren't explicitly defined in context: **DO NOT document them**
    - When documenting parameters: **Write "Not documented in context"** for missing attributes

    ### Deduction Instructions:
    - **Deduce endpoints** by analyzing route definitions, decorators, function names, or URL patterns in the code (e.g., @app.route, app.get, etc.).
    - **Deduce request bodies** from model definitions, schema classes, or example inputs in tests/code comments.
    - **Deduce response bodies** from return statements, serializer outputs, or hardcoded JSON in the code.

    ### Project Context:
    {context_str}

    ### Tech Stack:
    | Component       | Value                          |
    |-----------------|--------------------------------|
    | Language        | {tech_stack['language']}       |
    | Framework       | {tech_stack['framework']}      | 
    | Libraries       | {', '.join(tech_stack['libraries'])} |

    ### Required Documentation Structure:
    ## Table of Contents
    <!-- Generated from endpoint paths in context -->

    ## Authentication
    <!-- ONLY if auth mechanisms are explicitly defined -->

    ## Endpoints
    ### `[HTTP Method] [Full Path]`
    **Description**  
    <!-- Extract from route comments -->

    **Parameters**  
    | Type   | Name     | Data Type | Required | Constraints |
    |--------|----------|-----------|----------|-------------|
    <!-- Path/query/header params ONLY -->

    **Request Body**  
    ```json
    EXACTLY ONE OF:
    a) Hardcoded example from context OR
    b) Structure from class definitions (if no examples)
    ```

    **Responses**  
    `[STATUS CODE] [Description]`  
    ```json
    // MUST use ACTUAL response strings from:
    // - Test fixtures
    // - Example responses
    // - Serializer definitions
    // If none exist: OMIT ENTIRE BLOCK
    ```

    **Auth**  
    <!-- "None" if not required -->
    """)
    
    response = model.generate_content(prompt)
    return response.text

def generate_security_audit_batched(project_files, tech_stack):
    """Generate security audit with batched project context"""
    return process_in_batches(
        project_files,
        lambda context, ts: generate_security_audit_single(context, ts),
        tech_stack
    )

def generate_security_audit_single(context_str, tech_stack):
    """Generate security audit for a single batch"""
    prompt = textwrap.dedent(f"""
    You are a cybersecurity expert and backend deployment specialist. Perform a security audit and deployment review based on this project batch.

    ### Project Tech Stack:
    - Language: {tech_stack['language']}
    - Framework: {tech_stack['framework']}
    - Libraries: {', '.join(tech_stack['libraries'])}

    ### Security Audit Requirements:
    1. **Security Flaws**:
      - Scan for OWASP Top 10 vulnerabilities
      - Identify authentication/authorization weaknesses
      - Detect insecure dependencies
      - Check for sensitive data exposure
      - Analyze error handling for information leakage

    2. **Logic Gaps**:
      - Review business logic vulnerabilities
      - Identify potential race conditions
      - Check for insufficient validation
      - Analyze database query safety

    3. **Best Practices**:
      - Rate limiting implementation
      - Input validation strategies
      - Secure logging practices
      - Session management security

    ### Deployment Advisor Requirements:
    1. **Server Configuration**:
      - Optimal server hardening techniques
      - Security headers recommendations
      - TLS/SSL configuration best practices

    2. **Cloud Setup**:
      - Secure cloud architecture patterns
      - Network segmentation advice
      - WAF configuration recommendations

    3. **Environment Management**:
      - Secrets handling strategies
      - Environment variable security
      - Configuration management

    4. **CI/CD Security**:
      - Secure pipeline configuration
      - Automated security scanning
      - GitHub Actions security templates

    5. **Compliance Tools**:
      - OWASP ZAP configuration
      - SAST/DAST tool recommendations
      - Dependency scanning tools

    ### Output Requirements:
    - Prioritize findings by severity (Critical, High, Medium, Low)
    - Provide specific code references where vulnerabilities exist
    - Include remediation steps for each finding
    - Generate actionable deployment checklists
    - Suggest framework-specific security enhancements

    Project Context:
    {context_str}

    Output format: Comprehensive Markdown report for this batch
    """)
    
    response = model.generate_content(prompt)
    return response.text

# NEW FUNCTION: Custom README Generator
def generate_readme(project_files, tech_stack):
    """Generate README using AI with custom prompt and project context"""
    # Create context from top files (prioritized)
    context_str = "\n".join(
        f"## File: {item['rel_path']}\n{item['content']}\n"
        for item in project_files[:30]  # Use top 30 files for README
    )
    
    prompt = textwrap.dedent(f"""
    You are a documentation expert creating a comprehensive README.md file.
    Follow these guidelines:
    
    1. Create a professional, well-structured README
    2. Include all standard sections (Overview, Installation, Usage, etc.)
    3. Use appropriate formatting for the tech stack
    4. Follow best practices for documentation
    5. Incorporate the user's specific requirements below
    
    ### Tech Stack:
    - Language: {tech_stack['language']}
    - Framework: {tech_stack['framework']}
    - Libraries: {', '.join(tech_stack['libraries'])}
    
    
    ### Project Context:
    {context_str}
    
    ### Required Sections:
    # Project Title
    ## File structure summary
    ## Overview
    ## Features
    ## Installation
    ## Usage
    ## Configuration
    ## API Documentation
    ## Contributing
    ## License
    
    
    Output: ONLY the README content in Markdown format
    """)
    
    response = model.generate_content(prompt)
    return response.text

def write_file(folder_path, filename, content):
    """Write content to file in project directory"""
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filename} in {os.path.basename(folder_path)}")

def main():
    global model
    if len(sys.argv) > 1 and sys.argv[1] == "delete_key":
        delete_api_key()
        return
    
    api_key = ensure_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    # Load environment variables
    print("Project Tools: Select an option")
    print("a. API Test Writer\nb. API Documentation Generator\nc. CyberBackend Security Advisor\nd. README Generator")
    choice = input("User input: ").strip().lower()
    
    if choice not in ('a', 'b', 'c', 'd'):
        print("Invalid choice. Please select a valid option")
        return
    
    # Select project folder
    folder_name = list_folders()
    folder_path = os.path.abspath(folder_name)
    
    # Scan entire project
    print(f"Scanning entire {folder_name} codebase...")
    project_files = scan_entire_project(folder_path)
    print(f"Found {len(project_files)} files")
    
    # Detect tech stack using highest priority files
    print("Analyzing project structure...")
    tech_stack = ai_suggest_framework(project_files)
    print(f"\nDetected Tech Stack:")
    print(f"Language: {tech_stack['language']}")
    print(f"Framework: {tech_stack['framework']}")
    print(f"Libraries: {', '.join(tech_stack['libraries'])}")
    
    # Generate content based on user choice
    if choice == 'a':
        print("Generating API tests...")
        tests = generate_api_tests_batched(project_files, tech_stack)
        write_file(folder_path, "test_apis.py", tests)
    elif choice == 'b':
        print("Generating API documentation...")
        docs = generate_api_docs_batched(project_files, tech_stack)
        write_file(folder_path, "API_DOCUMENTATION.md", docs)
    elif choice == 'c':
        print("Generating security audit and deployment recommendations...")
        audit = generate_security_audit_batched(project_files, tech_stack)
        write_file(folder_path, "SECURITY_REVIEW.md", audit)
    elif choice == 'd':
        print("Generating README with default instructions...")
        readme_content = generate_readme(project_files, tech_stack)
        write_file(folder_path, "AI-README.md", readme_content)

if __name__ == "__main__":
    main()