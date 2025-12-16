import click
import json
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
import zipfile
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

from .client import GenifaiClient
from .config import Config, LANGUAGE_CONFIGS
from genifai.client import generate_key, rename_directory, delete_directory

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Genifai - AI-powered test case generator
    """
    pass


@main.command()
@click.option('--api-type', help='Your API type')
@click.option('--genifai-api-key', help='Your Genifai API key')
@click.option('--claude-api-key', help='Your Claude API key')
@click.option('--azure-endpoint', help='Your Azure endpoint')
def configure(api_type: str, genifai_api_key: str, claude_api_key: str, azure_endpoint: str):
    """Configure Genifai environment variables"""
    
    # Prompt for values
    if not api_type:
        api_type = click.prompt('API type', type=str)
    if not genifai_api_key:
        genifai_api_key = click.prompt('Genifai API key', hide_input=True, type=str)
    if not claude_api_key:
        claude_api_key = click.prompt('Claude API key', hide_input=True, type=str)
    if not azure_endpoint:
        azure_endpoint = click.prompt('Azure endpoint (optional, press Enter to skip)', 
                                     default='', show_default=False, type=str)
    
    # Create ~/.genifai/env file
    genifai_dir = Path.home() / '.genifai'
    genifai_dir.mkdir(exist_ok=True)
    env_file = genifai_dir / 'env'
    
    with open(env_file, 'w') as f:
        f.write(f"export GENIFAI_API_TYPE='{api_type}'\n")
        f.write(f"export GENIFAI_API_KEY='{genifai_api_key}'\n")
        f.write(f"export CLAUDE_API_KEY='{claude_api_key}'\n")
        if azure_endpoint:
            f.write(f"export AZURE_ENDPOINT='{azure_endpoint}'\n")


    console.print(f"\n✓ Configuration saved to {env_file}", style="bold green")

    console.print("\n[bold cyan]To apply these settings:[/bold cyan]")
    console.print("\n[bold yellow]Step 1:[/bold yellow] Add to your shell config (one-time setup)")
    console.print(f"  echo 'source {env_file}' >> ~/.bashrc")
    console.print("\n[bold yellow]Step 2:[/bold yellow] Apply changes now")
    console.print("  source ~/.bashrc")

    console.print("\n[dim]Or if using zsh:[/dim]")
    console.print(f"  echo 'source {env_file}' >> ~/.zshrc")
    console.print("  source ~/.zshrc")

    # console.print("\n[dim]After this, settings will automatically load in new terminals.[/dim]")




@main.command()
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              required=True, help='Directory to analyze')
@click.option('--build-script', '-b', type=click.Path(exists=True, file_okay=True, dir_okay=False),
               required=True, help='Path to build script')
@click.option('--language', '-l', help='Programming language')
@click.option('--metadata', '-m', type=click.Path(), required=True, help='Metadata output directory')
@click.option('--output', '-o', type=click.Path(), required=True, help='Output directory')
def analyze(directory: str, language: str, output: str, metadata: str, build_script: str):
    """Analyze directory contents
    
    Shows files, line counts, and code structure.
    """
    
    # Load config
    config = Config()

    # console.print(f"[yellow]Debug: config.api_type = {config.api_type}[/yellow]")
    # console.print(f"[yellow]Debug: os.environ.get('API_TYPE') = {os.environ.get('API_TYPE')}[/yellow]")
    

    if not config.is_claude_configured():
        console.print("❌ API key not configured. Run 'genifai configure' first.", style="bold red")
        return
    
    # Get language
    try:
        lang = config.get_language(language)
    except ValueError as e:
        console.print(f"❌ {str(e)}", style="bold red")
        return
    
    # Validate language
    if lang not in LANGUAGE_CONFIGS:
        console.print(f"❌ Unsupported language: {lang}", style="bold red")
        console.print(f"Supported: {', '.join(LANGUAGE_CONFIGS.keys())}")
        return
    
    lang_config = LANGUAGE_CONFIGS[lang]
    
    # # Get type
    # try:
    #     api_type = config.get_api_type(api_type)
    # except ValueError as e:
    #     console.print(f"❌ {str(e)}", style="bold red")
    #     return


    # Initialize client
    client = GenifaiClient(
        api_type=config.api_type,
        genifai_api_key=config.genifai_api_key,
        claude_api_key=config.claude_api_key,
        azure_endpoint=config.azure_endpoint
    )
    genifai_api_key = config.genifai_api_key

    # Create temporary directory and copy files
    temp_dir = None
    try:

        # Create temporary directory
        # temp_dir = tempfile.mkdtemp(prefix='genifai_')
        # console.print(f"[dim]Created temporary directory: {temp_dir}[/dim]")
        
        # # Copy source directory to temp
        # temp_src_dir = os.path.join(temp_dir, 'source')
        # shutil.copytree(directory, temp_src_dir)
        
        # # Copy build script to temp directory if provided
        # if build_script:
        #     build_script_name = os.path.basename(build_script)
        #     temp_build_script = os.path.join(temp_src_dir, build_script_name)
        #     shutil.copy2(build_script, temp_build_script)
        #     console.print(f"[dim]Copied build script to: {temp_build_script}[/dim]")
        
        
        # Analyze
        console.print(f"[bold blue]Analyzing directory {directory}...[/bold blue]")
        
        with console.status("[bold green]Analyzing..."):
            try:
                result_metadata, zip_data = client.analyze_directory(
                    directory=directory,  #directory=temp_src_dir,  # Use temp directory instead  #directory=directory,
                    language=lang,
                    output=output,
                )

            except Exception as e:
                console.print(f"❌ Error: {str(e)}", style="bold red")
                return
        

    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            console.print(f"[dim]Cleaned up temporary directory[/dim]")


    # Check if output exists and handle it
    if os.path.exists(output):
        if os.path.isfile(output):
            # If it's a file, remove it
            console.print(f"[yellow]⚠ Removing existing file: {output}[/yellow]")
            os.remove(output)
        elif os.path.isdir(output):
            # If it's a directory, ask user or remove
            console.print(f"[yellow]⚠ Directory {output} already exists. Removing...[/yellow]")
            shutil.rmtree(output)
    
    # Create output directory
    os.makedirs(output, exist_ok=True)


    # save the zip
    if zip_data:
        """
        # if output_dir is None:
        project_name = os.path.basename(os.path.abspath(directory))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        # output_dir = f"metadata_{result_metadata['project_id']}"
        output_dir = f"metadata_{project_name}_{timestamp}"
        """

        temp_dir = f"tmp/{genifai_api_key}"
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(temp_dir)
        
        meta_dir = f"tmp/{genifai_api_key}/metadata_{genifai_api_key}"
        work_dir = f"tmp/{genifai_api_key}/workspace_{genifai_api_key}"

        rename_directory(meta_dir, metadata)
        rename_directory(work_dir, output)

        delete_directory(f"tmp") #temp_dir)
        
        console.print(f"📦 Metadata extracted to: {metadata}/", style="bold green")
        console.print(f"📦 Output is saved at: {output}/", style="bold green")

    # Display results
    console.print("\n✓ Analysis complete!", style="bold green")
    console.print(f"\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"  Files: {result_metadata['file_count']}")
    console.print(f"  Total lines: {result_metadata['total_lines']}")
    console.print(f"  Language: {result_metadata['language']}")
    # console.print(f"  Project ID: {result_metadata['project_id']}")  





@main.command()
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              required=True, help='Directory to analyze')
@click.option('--language', '-l', help='Programming language')
@click.option('--metadata', '-m', help='Metadata directory')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def graph(directory: str, language: str, metadata: str, output: str):
    """Analyze directory contents
    
    Shows files, line counts, and code structure.
    """
    
    # Load config
    config = Config()
    if not config.is_claude_configured():
        console.print("❌ API key not configured. Run 'genifai configure' first.", style="bold red")
        return
    
    # Get language
    try:
        lang = config.get_language(language)
    except ValueError as e:
        console.print(f"❌ {str(e)}", style="bold red")
        return
    
    # Validate language
    if lang not in LANGUAGE_CONFIGS:
        console.print(f"❌ Unsupported language: {lang}", style="bold red")
        console.print(f"Supported: {', '.join(LANGUAGE_CONFIGS.keys())}")
        return
    
    lang_config = LANGUAGE_CONFIGS[lang]
    
    # Initialize client
    client = GenifaiClient(
        api_type=config.api_type,
        genifai_api_key=config.genifai_api_key,
        claude_api_key=config.claude_api_key,
        azure_endpoint=config.azure_endpoint
    )
    
    # Analyze
    console.print(f"[bold blue]Analyzing directory {metadata}...[/bold blue]")
    
    with console.status("[bold green]Uploading and analyzing..."):
        try:
            result_metadata, zip_data = client.analyze_graph(
                directory=directory,
                language=lang,
                meta_dir=metadata,
            )

        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="bold red")
            return
    
    # Save the zip
    if zip_data:
        # output_dir = f"metadata_{result_metadata['project_id']}"
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(output)
        
        console.print(f"📦 Metadata extracted to: {output}/", style="bold green")



    # Display results
    console.print("\n✓ Graph analysis complete!", style="bold green")
    console.print(f"\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"  Files: {result_metadata['file_count']}")
    console.print(f"  Total lines: {result_metadata['total_lines']}")
    console.print(f"  Language: {result_metadata['language']}")
    # console.print(f"  Project ID: {result_metadata['project_id']}") 


def validate_target_or_callgraph(ctx, param, value):
    """Validate that either target or callgraph is provided, but not both"""
    # Get the other parameter's value
    other_param = 'callgraph' if param.name == 'target' else 'target'
    other_value = ctx.params.get(other_param)
    
    # If this is the second parameter being processed
    if other_param in ctx.params:
        if value and other_value:
            raise click.BadParameter(
                "Cannot specify both --target and --callgraph. Choose one."
            )
        if not value and not other_value:
            raise click.BadParameter(
                "Must specify either --target or --callgraph."
            )
    
    return value


@main.command()
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              required=True, help='Directory to analyze')
@click.option('--language', '-l', help='Programming language (python, javascript, etc.)')
@click.option('--metadata', '-m', required=True, help='Metadata directory')
@click.option('--target', '-t', callback=validate_target_or_callgraph, 
              help='Target function(s)')
@click.option('--callgraph', '-c', callback=validate_target_or_callgraph,
              help='Call graph path')
@click.option('--output', '-o', type=click.Path(), required=True, help='Output file path')
@click.option('--iteration', '-i', required=True, help='Iteration count')
def generate(
    directory: str,
    language: str,
    metadata: str,
    target: str, 
    callgraph: str,
    output: str,
    iteration: int,
):
    """Generate test cases for a directory"""
    
    # Load config
    config = Config()
    if not config.is_claude_configured():
        console.print("❌ API key not configured. Run 'genifai configure' first.", style="bold red")
        return
    
    # Get language
    try:
        lang = config.get_language(language)
    except ValueError as e:
        console.print(f"❌ {str(e)}", style="bold red")
        return
    
    # Validate language
    if lang not in LANGUAGE_CONFIGS:
        console.print(f"❌ Unsupported language: {lang}", style="bold red")
        console.print(f"Supported: {', '.join(LANGUAGE_CONFIGS.keys())}")
        return
    
    lang_config = LANGUAGE_CONFIGS[lang]

    # Initialize client
    client = GenifaiClient(
        api_type=config.api_type,
        genifai_api_key=config.genifai_api_key,
        claude_api_key=config.claude_api_key,
        azure_endpoint=config.azure_endpoint
    )

    # Generate tests
    if target:
        mode = "target function"
        mode_value = target
        console.print(f"[bold blue]Generating tests for target function: {target}[/bold blue]")
    else:  # callgraph
        mode = "callgraph"
        mode_value = callgraph
        console.print(f"[bold blue]Generating tests using callgraph: {callgraph}[/bold blue]")
    
    # Generate tests
    # console.print(f"[bold blue]Generating {lang_config['display_name']} tests for {directory}...[/bold blue]")
    
    with console.status("[bold green]Processing..."):
        try:
            result_metadata, zip_data = client.generate_from_directory(
                directory=directory,
                language=lang,
                meta_dir=metadata,
                target=target,
                callgraph=callgraph,
                save_zip_to=output,
                count=iteration,
            )
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="bold red")
            return

    # if zip_data:
    #     # output = f"output_{result_metadata['project_id']}"
    #     with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
    #         zf.extractall(output)
        
    #     console.print(f"📦 Saved to: {output}/", style="bold green")


    # Display results
    console.print("\n✓ Generation complete!", style="bold green")
    # console.print(f"\n[bold cyan]Summary:[/bold cyan]")
    # console.print(f"  Project ID: {result_metadata['project_id']}") 

    


@main.command()
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              required=True, help='Directory to analyze')
@click.option('--metadata', '-m', help='Metadata directory')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def translate_config(
    directory: str,
    metadata: str,
    output: str
):

    # Load config
    config = Config()
    if not config.is_claude_configured():
        console.print("❌ API key not configured. Run 'genifai configure' first.", style="bold red")
        return
    

    # Initialize client
    client = GenifaiClient(
        api_type=config.api_type,
        genifai_api_key=config.genifai_api_key,
        claude_api_key=config.claude_api_key,
        azure_endpoint=config.azure_endpoint
    )
    
    # Start

    with console.status("[bold green]Processing..."):
        try:
            result_metadata, zip_data = client.translate_config(
                directory=directory,
                language=lang,
                meta_dir=metadata,
                callgraph=callgraph
            )
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="bold red")
            return
    
    if zip_data:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(output)
        
        console.print(f"📦 Saved to: {output}/", style="bold green")


    # Display results
    console.print("\n✓ Translation complete!", style="bold green")
    console.print(f"\n[bold cyan]Summary:[/bold cyan]")
    # console.print(f"  Project ID: {result_metadata['project_id']}") 



@main.command()
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              required=True, help='Directory to analyze')
@click.option('--metadata', '-m', help='Metadata directory')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def translate(
    directory: str,
    metadata: str,
    output: str
):

    # Load config
    config = Config()
    if not config.is_claude_configured():
        console.print("❌ API key not configured. Run 'genifai configure' first.", style="bold red")
        return
    

    # Initialize client
    client = GenifaiClient(
        api_type=config.api_type,
        genifai_api_key=config.genifai_api_key,
        claude_api_key=config.claude_api_key,
        azure_endpoint=config.azure_endpoint
    )
    
    # Start

    with console.status("[bold green]Processing..."):
        try:
            result_metadata, zip_data = client.translate_config(
                directory=directory,
                language=lang,
                meta_dir=metadata,
                callgraph=callgraph
            )
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="bold red")
            return
    
    if zip_data:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(output)
        
        console.print(f"📦 Saved to: {output}/", style="bold green")


    # Display results
    console.print("\n✓ Translation complete!", style="bold green")
    console.print(f"\n[bold cyan]Summary:[/bold cyan]")
    # console.print(f"  Project ID: {result_metadata['project_id']}") 

    
    

@main.command()
def languages():
    """List supported programming languages"""
    
    table = Table(title="Supported Languages")
    table.add_column("Language", style="cyan")
    table.add_column("Code", style="green")
    table.add_column("Default Framework", style="yellow")
    # table.add_column("Extensions", style="dim")
    
    for code, config in sorted(LANGUAGE_CONFIGS.items()):
        table.add_row(
            config['display_name'],
            code,
            config['default_framework'],
            #', '.join(config['extensions'])
        )
    
    console.print(table)
    console.print("\n[dim]Specify language via:[/dim]")
    console.print("  --language option:    genifai generate --language python")
    console.print("  Environment variable: export GENIFAI_LANGUAGE=python")
    console.print("  Config file:          genifai configure --default-language c")


@main.command()
def status():
    """Check configuration and API connection status"""
    config = Config()
    
    # Check configuration
    console.print("\n[bold cyan]Configuration Status:[/bold cyan]")
    console.print(f"Config file: {config.CONFIG_FILE}")
    console.print(f"Genifai API key: {'✓ Configured' if config.genifai_api_key else '❌ Not configured'}")
    console.print(f"Claude API key: {'✓ Configured' if config.claude_api_key else '❌ Not configured'}")
    console.print(f"Azure endpoint (if necessary): {'✓ Configured' if config.azure_endpoint else '❌ Not configured'}")
    
    if config.default_language:
        console.print(f"Default language: {config.default_language}")
    

    # Check API connection
    if config.is_claude_configured():
        console.print("\n[bold cyan]API Status:[/bold cyan]")
        client = GenifaiClient(
            api_type=config.api_type,
            genifai_api_key=config.genifai_api_key,
            claude_api_key=config.claude_api_key,
            azure_endpoint=config.azure_endpoint
        )
        
        with console.status("[bold green]Checking connection..."):
            is_healthy = client.health_check()
        
        if is_healthy:
            console.print("✓ API is accessible", style="bold green")
        else:
            console.print("❌ Cannot connect to API", style="bold red")


@main.group()
def keys():
    """Manage API keys and identifiers"""
    pass


@keys.command('generate')
def keys_generate():
    """Generate a new API key"""
    try:
        result, _ = generate_key()
        
        result_key = result.get('api_key')
        key_id = result.get('key_id')
        
        click.echo(f"✓ API Key generated successfully!")
        #click.echo(f"Key ID: {key_id}")
        click.echo(f"API Key: {result_key}")
        click.echo(f"\nPlease save this key securely. You won't be able to see it again.")
        
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()