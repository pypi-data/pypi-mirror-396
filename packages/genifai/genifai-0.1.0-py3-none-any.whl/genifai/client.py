import requests
from typing import Dict, Any, Optional, Tuple
import zipfile
import io
import os
import json
from requests_toolbelt.multipart import decoder
import tempfile
from pathlib import Path
import shutil
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
import base64
from datetime import datetime, timedelta


from .config import BASE_URL

def _create_zip_from_directory(directory: str) -> io.BytesIO:
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(directory):
            #dirs[:] = [d for d in dirs if d not in excluded_dirs]
            dirs[:] = [d for d in dirs]
            
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, directory)
                try:
                    zf.write(filepath, arcname)
                except Exception:
                    continue
    
    zip_buffer.seek(0)
    return zip_buffer


def _save_in_directory(callgraph):    
    temp_dir = tempfile.mkdtemp()
    
    callgraph_path = Path(callgraph)
    destination = Path(temp_dir) / callgraph_path.name
    
    shutil.copy2(callgraph_path, destination)
    
    return str(destination), temp_dir



class GenifaiClient:
    """Client for Genifai test case generation API"""


    def __init__(self, api_type: Optional[str] = None, genifai_api_key: Optional[str] = None, 
                 claude_api_key: Optional[str] = None, azure_endpoint: Optional[str] = None):
        """
        Initialize Genifai client
        
        Args:
            api_type: API type (defaults to GENIFAI_API_TYPE env var)
            genifai_api_key: Genifai API key (defaults to GENIFAI_API_KEY env var)
            claude_api_key: Claude API key (defaults to CLAUDE_API_KEY env var)
            azure_endpoint: Azure endpoint (defaults to AZURE_ENDPOINT env var)
        """
        self.api_type = api_type or os.getenv('GENIFAI_API_TYPE')
        self.genifai_api_key = genifai_api_key or os.getenv('GENIFAI_API_KEY')
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        self.azure_endpoint = azure_endpoint or os.getenv('AZURE_ENDPOINT')
        
        if not self.genifai_api_key:
            raise ValueError("genifai_api_key must be provided or set GENIFAI_API_KEY environment variable")
        
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.genifai_api_key}",
            "User-Agent": "genifai/0.1.0"
        })

    def generate_test_cases(
        self,
        method: str,
        endpoint: str,
        language: str,
        framework: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate test cases for an HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint URL
            language: Programming language
            framework: Testing framework (optional)
            headers: Request headers
            body: Request body
            query_params: Query parameters
            description: Additional context
            
        Returns:
            Dictionary containing generated test cases
            
        Raises:
            requests.HTTPError: If the API request fails
        """
        payload = {
            "method": method.upper(),
            "endpoint": endpoint,
            "language": language,
        }
        
        if framework:
            payload["framework"] = framework
        if headers:
            payload["headers"] = headers
        if body:
            payload["body"] = body
        if query_params:
            payload["query_params"] = query_params
        if description:
            payload["description"] = description
        
        try:
            response = self.session.post(
                f"{self.base_url}/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    

    def analyze_directory(
        self,
        directory: str,
        language: str,
        output: str,
        framework: Optional[str] = None,
        save_zip_to: Optional[str] = None 
    ) -> Tuple[Dict[str, Any], bytes]:        
        # 
        directory_name = os.path.basename(os.path.abspath(directory))


        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            for root, dirs, files in os.walk(directory):
                
                # dirs[:] = [d for d in dirs if d not in [
                #     '__pycache__', 'node_modules', '.git', 
                #     'venv', 'env', 'dist', 'build', '.pytest_cache',
                #     'target', 'bin', 'obj'
                # ]]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, directory)
                    try:
                        zf.write(filepath, arcname)
                        file_count += 1
                    except Exception:
                        continue
            
            if file_count == 0:
                raise Exception(f"No {language} files found in {directory}")
        
        zip_buffer.seek(0)
        
        
        files = {
            'archive': ('code.zip', zip_buffer, 'application/zip')
        }
        data = {
            'language': language,
            'api_type': self.api_type,
            'genifai_api_key': self.genifai_api_key,
            'claude_api_key': self.claude_api_key,
            'azure_endpoint' : self.azure_endpoint,
            'directory_name': directory_name
        }
        if framework:
            data['framework'] = framework
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            headers['Authorization'] = f"Bearer {self.genifai_api_key}"
            
            response = requests.post(
                f"{self.base_url}/analyze",
                files=files,
                data=data,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            
            # parse multipart/form-data response
            content_type = response.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                multipart_data = decoder.MultipartDecoder.from_response(response)
                
                metadata = None
                zip_data = None
                
                for part in multipart_data.parts:
                    content_disposition = part.headers.get(b'Content-Disposition', b'').decode()
                    content_type_part = part.headers.get(b'Content-Type', b'').decode()
                    
                    if 'name="metadata"' in content_disposition:
                        metadata = json.loads(part.content.decode('utf-8'))
                    elif 'name="archive"' in content_disposition:
                        zip_data = part.content
                
                if metadata is None or zip_data is None:
                    raise Exception("Invalid multipart response")
                
                
                return metadata, zip_data
            else:
                return response.json(), None

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    


    def analyze_graph(
        self,
        directory: str,
        language: str,
        meta_dir: str,
        framework: Optional[str] = None,
        save_zip_to: Optional[str] = None 
    ) -> Tuple[Dict[str, Any], bytes]:
        
        # 
        directory_name = os.path.basename(os.path.abspath(directory))


        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            for root, dirs, files in os.walk(meta_dir):
                
                dirs[:] = [d for d in dirs]
                #  if d not in [
                #     '__pycache__', 'node_modules', '.git', 
                #     'venv', 'env', 'dist', 'build', '.pytest_cache',
                #     'target', 'bin', 'obj'
                # ]]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, meta_dir)
                    try:
                        zf.write(filepath, arcname)
                        file_count += 1
                    except Exception:
                        continue
            
            if file_count == 0:
                raise Exception(f"No {language} files found in {meta_dir}")
        
        zip_buffer.seek(0)
        
        
        files = {
            'archive': ('code.zip', zip_buffer, 'application/zip')
        }
        data = {
            'language': language,
            'api_type': self.api_type,
            'genifai_api_key': self.genifai_api_key,
            'claude_api_key': self.claude_api_key,
            'azure_endpoint' : self.azure_endpoint,
            'original_dir' : directory,
            'directory_name': directory_name
        }
        if framework:
            data['framework'] = framework
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            headers['Authorization'] = f"Bearer {self.genifai_api_key}"
            
            response = requests.post(
                f"{self.base_url}/graph",
                files=files,
                data=data,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            
            # parse multipart/form-data response
            content_type = response.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                # analyze multipart response
                multipart_data = decoder.MultipartDecoder.from_response(response)
                
                metadata = None
                zip_data = None
                
                for part in multipart_data.parts:
                    content_disposition = part.headers.get(b'Content-Disposition', b'').decode()
                    content_type_part = part.headers.get(b'Content-Type', b'').decode()
                    
                    if 'name="metadata"' in content_disposition:
                        metadata = json.loads(part.content.decode('utf-8'))
                    elif 'name="archive"' in content_disposition:
                        zip_data = part.content
                
                if metadata is None or zip_data is None:
                    raise Exception("Invalid multipart response")
                
                # save the zip
                if save_zip_to:
                    with open(save_zip_to, 'wb') as f:
                        f.write(zip_data)
                
                return metadata, zip_data
            else:
                return response.json(), None

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    

    def generate_from_directory(
        self,
        directory: str,
        language: str,
        meta_dir: str,
        target: str,
        callgraph: str,
        save_zip_to: str,
        count: int,
    ) -> Tuple[Dict[str, Any], bytes]:
        
        console = Console()
        saved_path = None
        graph_directory = None
        
        # 
        directory_name = os.path.basename(os.path.abspath(directory))
        log_dir = "log"

        try:
            # with Progress(
            #     SpinnerColumn(),
            #     TextColumn("[progress.description]{task.description}"),
            #     transient=True
            # ) as progress:
            
            #######

            #task = progress.add_task("Creating ZIP archives...", total=None)
            
            meta_zip_buffer = _create_zip_from_directory(meta_dir)
            code_zip_buffer = _create_zip_from_directory(directory)

            #progress.update(task, description="Processing callgraph...")
            target_type = None
            if target:
                target_type = "specified"
                saved_path, graph_directory = _save_in_directory(target)

            elif callgraph:
                target_type = "centlic"
                saved_path, graph_directory = _save_in_directory(callgraph)

            graph_zip_buffer = _create_zip_from_directory(graph_directory)
            
            #progress.update(task, description="Uploading to server...")
            
            files = {
                'metadata_archive': ('metadata.zip', meta_zip_buffer, 'application/zip'),
                'code_archive': ('code.zip', code_zip_buffer, 'application/zip'),
                'graph_archive': ('graph.zip', graph_zip_buffer, 'application/zip')
            }
            data = {
                'language': language,
                'api_type': self.api_type,
                'target_type' : target_type,
                'genifai_api_key': self.genifai_api_key,
                'claude_api_key': self.claude_api_key,
                'azure_endpoint' : self.azure_endpoint,
                'directory_name': directory_name,
                'count' : count,
            }

            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            headers['Authorization'] = f"Bearer {self.genifai_api_key}"
            
            #progress.update(task, description="Waiting for server response...")
            
            response = requests.post(
                f"{self.base_url}/generate",
                files=files,
                data=data,
                headers=headers,
                stream=True,
                timeout=300
            )
            response.raise_for_status()
            
            #progress.update(task, description="Processing...")
        
            #######

            # show the result
            # console.print("\n[bold cyan]Test Generation Progress:[/bold cyan]\n")
            
            final_metadata = None
            zip_data = None
            multipart_mode = False
            multipart_buffer = io.BytesIO()
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                # in multipart mode
                if multipart_mode:
                    multipart_buffer.write(line + b'\n')
                    continue
                
                try:
                    data = json.loads(line.decode('utf-8'))
                    
                    if data['type'] == 'iteration_start':
                        console.print()
                        console.print(f"[bold]Iteration {data['iteration']}/{data['total']}:[/bold]")
                    
                    elif data['type'] == 'error_retry':
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        os.makedirs(log_dir, exist_ok=True)
                        client_log_file = f"{log_dir}/error_{timestamp}.log"
                        
                        with open(client_log_file, 'w') as f:
                            f.write(data['log_content'])
                        console.print()
                        # console.print(f"  [yellow]✓[/yellow] Error log saved to: {client_log_file}")
                        console.print(f"  [yellow]✗[/yellow] {data['message']} - See detailed logs: {client_log_file}")
                        
                        # console.print(f"  [yellow]✓[/yellow] Retrying with alternative approach...")
                    
                    elif data['type'] == 'execution_success':
                        console.print(f"  [green]✓[/green] {data['message']}")


                    elif data['type'] == 'iteration_result':
                        result = data['result']
                        #new_tests = f" (+{result['new_tests']})" if result.get('new_tests') else ""
                        #console.print(f"  [green]✓[/green] Generated {result['test_count']} test cases{new_tests}")
                        
                        # Function coverage
                        func_max = result['func_max']
                        func = result['func']
                        func_per = round((func / func_max) * 100, 1) if func_max > 0 else 0.0
                        
                        # Branch coverage
                        branch_max = result['branch_max']
                        branch = result['branch']
                        branch_per = round((branch / branch_max) * 100, 1) if branch_max > 0 else 0.0
                        
                        # Line coverage
                        line_max = result['line_max']
                        line = result['line']
                        line_per = round((line / line_max) * 100, 1) if line_max > 0 else 0.0

                        console.print()
                        console.print(
                            f"  [green]✓[/green] Coverage: "
                            f"function {func_per}% ({func}/{func_max}), "
                            f"branch {branch_per}% ({branch}/{branch_max}), "
                            f"line {line_per}% ({line}/{line_max})"
                        )

                    # elif data['type'] == 'result':
                    #     console.print(f"\n[bold green]✓ Complete![/bold green]")
                    
                    elif data['type'] == 'error_fatal':
                        console.print(f"\n[bold red]✗ Error:[/bold red] {data['error']}")
                        console.print(f"[dim]See logs: {data['log_file']}[/dim]")
                        raise Exception(data['error'])

                    elif data['type'] == 'complete':
                        console.print(f"\n[bold green]✓ Complete![/bold green]")
                        final_metadata = data['metadata']
                        download_url = data['download_url']

                        # zip_data = base64.b64decode(data['archive_base64'])
                        
                        # if save_zip_to:
                        #     with open(save_zip_to, 'wb') as f:
                        #         f.write(zip_data)
                        #     console.print(f"[green]✓[/green] Saved archive to: {save_zip_to}")
                
                except json.JSONDecodeError:
                    if multipart_mode:
                        multipart_buffer.write(line + b'\n')
            
            # if multipart_mode:
            #     multipart_buffer.seek(0)
            #     from requests_toolbelt.multipart import decoder
                
            #     class FakeResponse:
            #         def __init__(self, content, boundary):
            #             self.content = content
            #             self.headers = {
            #                 'Content-Type': f'multipart/form-data; boundary={boundary}'
            #             }
                
            #     fake_response = FakeResponse(multipart_buffer.getvalue(), boundary)
            #     multipart_data = decoder.MultipartDecoder.from_response(fake_response)
                
            #     for part in multipart_data.parts:
            #         content_disposition = part.headers.get(b'Content-Disposition', b'').decode()
                    
            #         if 'name="metadata"' in content_disposition:
            #             final_metadata = json.loads(part.content.decode('utf-8'))
            #         elif 'name="archive"' in content_disposition:
            #             zip_data = part.content
                
            #     if save_zip_to and zip_data:
            #         with open(save_zip_to, 'wb') as f:
            #             f.write(zip_data)
            
            if final_metadata is None or download_url is None:
                raise Exception("No result received from server")
            
            console.print(f"[cyan]Downloading results...[/cyan]")
            
            download_response = requests.get(
                f"{self.base_url}{download_url}",
                headers={k: v for k, v in self.session.headers.items()},
                stream=True,
                timeout=300
            )
            download_response.raise_for_status()
            
            zip_data = download_response.content
            
            # console.print(f"[green]✓[/green] Downloaded {len(zip_data)} bytes")
            
            ####
            if save_zip_to:
                os.makedirs(save_zip_to, exist_ok=True)
                
                with tempfile.TemporaryDirectory() as temp_extract_dir:
                    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
                        zf.extractall(temp_extract_dir)
                    
                
                    extracted_items = os.listdir(temp_extract_dir)
                    
                    if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_extract_dir, extracted_items[0])):
                        source_dir = os.path.join(temp_extract_dir, extracted_items[0])
                        
                        project_id = "testcases" #final_metadata['project_id']
                        destination_dir = os.path.join(save_zip_to, project_id)
                        
                        if os.path.exists(destination_dir):
                            shutil.rmtree(destination_dir)
                        
                        shutil.copytree(source_dir, destination_dir)
                        console.print(f"[green]✓[/green] Saved to: {destination_dir}")
                    else:
                        for item in extracted_items:
                            source = os.path.join(temp_extract_dir, item)
                            destination = os.path.join(save_zip_to, item)
                            
                            if os.path.isdir(source):
                                if os.path.exists(destination):
                                    shutil.rmtree(destination)
                                shutil.copytree(source, destination)
                            else:
                                shutil.copy2(source, destination)
                        
                        console.print(f"[green]✓[/green] Saved to: {save_zip_to}/")

            return final_metadata, zip_data

                        

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        
        finally:
            if graph_directory and os.path.exists(graph_directory):
                shutil.rmtree(graph_directory)

    
    def translate(self,
        directory: str,
        meta_dir: str,
        save_zip_to: Optional[str] = None 
    ) -> Tuple[Dict[str, Any], bytes]:

        print("TBA")


    
    def health_check(self) -> bool:
        """Check if the API is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False



def generate_key() -> Tuple[Dict[str, Any], bytes]:
    """Generate a unique key"""
    
    try:
        files = {}
        data = {}

        response = requests.post(
            f"{BASE_URL}/generate_key",
            files=files,
            data=data,
            stream=True,
            timeout=300
        )
        
        response.raise_for_status()

        result = response.json()
        return result, None
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


def rename_directory(old_path, new_path, overwrite=True):

    old_dir = Path(old_path).resolve()
    new_dir = Path(new_path).resolve()
    
    if not old_dir.exists():
        raise FileNotFoundError(f"Directory not found: {old_path}")
    
    if not old_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {old_path}")
    
    if old_dir == new_dir:
        # print(f"Source and destination are the same: {old_path}")
        return str(new_dir)
    
    if new_dir.exists():
        if overwrite:
            # print(f"Removing existing directory: {new_path}")
            shutil.rmtree(new_dir)
        else:
            raise FileExistsError(f"Destination already exists: {new_path}. Use overwrite=True to replace.")
    
    new_dir.parent.mkdir(parents=True, exist_ok=True)
    
    old_dir.rename(new_dir)

    return str(new_dir)


def delete_directory(dir_path):
    try:
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            # print(f"Directory '{dir_path}' has been successfully deleted.")
        #else:
        #    print(f"No such directory: '{dir_path}'")
    except Exception as e:
        print(f"Error deleting directory: {e}")       
