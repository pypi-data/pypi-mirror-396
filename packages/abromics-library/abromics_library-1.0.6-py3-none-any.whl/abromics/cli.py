import click
import os
import tomllib
from pathlib import Path
from .client import AbromicsClient
from .utils import FILE_TYPES, SEQUENCING_TYPES

def get_version():
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "unknown"

__version__ = get_version()


def require_client(ctx):
    """Helper function to ensure client is available for API-dependent commands."""
    if ctx.obj['client'] is None:
        click.echo("❌ This command requires an API key. Please provide --api-key or set ABROMICS_API_KEY environment variable.", err=True)
        ctx.exit(1)
    return ctx.obj['client']


@click.group()
@click.option('--api-key', envvar='ABROMICS_API_KEY', help='ABRomics API key')
@click.option('--base-url', envvar='ABROMICS_BASE_URL', default='https://analysis.abromics.fr', help='ABRomics API base URL')
@click.version_option(version=__version__, prog_name='abromics')
@click.pass_context
def cli(ctx, api_key, base_url):
    ctx.ensure_object(dict)
    if api_key:
        ctx.obj['client'] = AbromicsClient(api_key=api_key, base_url=base_url)
    else:
        ctx.obj['client'] = None


@cli.group('project')
@click.pass_context
def project_group(ctx):
    """Manage ABRomics projects."""
    pass


@project_group.command('create')
@click.option('--name', required=True, help='Project name')
@click.option('--template', required=True, type=int, help='Template ID to use')
@click.option('--description', required=False, help='Optional project description')
@click.pass_context
def create_project(ctx, name, template, description):
    """Create a new project."""
    client = require_client(ctx)
    try:
        project = client.projects.create(name=name, template=template, description=description)
        click.echo(f"✅ Created project: {project.name} (ID: {project.id})")
    except Exception as e:
        click.echo(f"❌ Failed to create project: {str(e)}", err=True)







@cli.command('complete-upload-workflow')
@click.option('--metadata-tsv', required=True, help='Path to TSV metadata file')
@click.option('--data-dir', required=True, help='Directory containing data files to upload')
@click.pass_context
def complete_upload_workflow(ctx, metadata_tsv, data_dir):
    """Complete workflow: create samples from TSV and upload files automatically."""
    import os
    
    client = require_client(ctx)
    
    tsv_path = metadata_tsv
    
    if not os.path.exists(tsv_path):
        click.echo(f"❌ TSV file not found: {tsv_path}", err=True)
        return
    
    try:
        click.echo("🚀 Starting complete workflow...")
        click.echo(f"   TSV file: {tsv_path}")
        click.echo(f"   Data directory: {data_dir}")
        
        # Step 1: Parse TSV file and detect file type
        click.echo("\n📊 Step 1: Processing TSV file...")
        samples_data = client.batch.tsv_processor._parse_tsv(tsv_path)
        total_samples_expected = len(samples_data)
        
        if not samples_data:
            click.echo("❌ No data found in TSV file", err=True)
            return
        
        file_type = "fastq"  # default
        file_pattern = "*.fastq.gz"  # default
        sample_columns = samples_data[0].keys() if samples_data else []
        
        if any('r1' in col.lower() or 'r2' in col.lower() for col in sample_columns):
            file_type = "fastq"
            file_pattern = "*.fastq.gz"
            click.echo(f"   📁 Detected file type: FASTQ (found R1/R2 columns)")
        elif any('fasta' in col.lower() for col in sample_columns):
            file_type = "fasta"
            file_pattern = "*.fasta"
            click.echo(f"   📁 Detected file type: FASTA")
        else:
            click.echo(f"   📁 Using default file type: FASTQ")
        
        click.echo(f"   📁 File pattern: {file_pattern}")

        if not any('project' in sample for sample in samples_data):
            click.echo("❌ TSV must contain the required column 'Project Name*'.", err=True)
            return
        
        projects_data = {}
        duplicate_sample_names_by_project = {}
        for sample_data in samples_data:
            project_name = sample_data.get('project', 'Default Project')
            if project_name not in projects_data:
                projects_data[project_name] = []
                duplicate_sample_names_by_project[project_name] = set()
            projects_data[project_name].append(sample_data)
        
        click.echo(f"Found {len(projects_data)} projects: {', '.join(projects_data.keys())}")
        
        # Step 2: Find existing projects
        click.echo("\n📁 Step 2: Finding existing projects...")
        project_lookup = {}
        missing_projects = set()
        
        all_projects = []
        page = 1
        page_size = 100
        
        try:
            while True:
                response = client.get('/api/project/', params={
                    'detailed_project': 'true',
                    'ordering': '-create_time',
                    'page': page,
                    'page_size': page_size
                })
                data = response.json()
                
                if 'results' in data:
                    api_projects_data = data['results']
                else:
                    api_projects_data = data if isinstance(data, list) else [data]
                
                if not api_projects_data:
                    break
                
                from abromics.models.project import Project
                projects = [Project.from_dict(project) for project in api_projects_data]
                all_projects.extend(projects)
                
                if len(projects) < page_size:
                    break
                page += 1
        except Exception as e:
            click.echo(f"❌ Error fetching projects: {str(e)}", err=True)
            return
        
        for project_name in projects_data.keys():
            click.echo(f"Looking for project: {project_name}")
            
            matching_projects = [p for p in all_projects if p.name.lower() == project_name.lower()]
            
            if len(matching_projects) == 0:
                click.echo(f"  ❌ Project '{project_name}' not found. Please create this project first.", err=True)
                missing_projects.add(project_name)
                continue
            elif len(matching_projects) > 1:
                click.echo(f"  ❌ Multiple projects found with name '{project_name}':", err=True)
                for i, project in enumerate(matching_projects, 1):
                    click.echo(f"    {i}. ID: {project.id}, Name: '{project.name}'", err=True)
                click.echo(f"  Please rename one of these projects to avoid conflicts.", err=True)
                continue
            else:
                project = matching_projects[0]
                project_lookup[project_name] = project.id
                click.echo(f"  ✅ Found project: {project.name} (ID: {project.id})")
        
        click.echo("\n🧬 Step 3: Creating experiments with samples...")
        total_samples = 0
        for project_name, samples in projects_data.items():
            if project_name not in project_lookup:
                continue
                
            project_id = project_lookup[project_name]
            click.echo(f"Creating {len(samples)} experiment(s) with sample(s) for project: {project_name}")
            
            for i, sample_data in enumerate(samples):
                sample_id = sample_data.get('original_sample_id', sample_data.get('sample_name', f'sample_{i+1}'))
                click.echo(f"  Creating experiment {i+1}/{len(samples)}: {sample_id}")
                
                try:
                    sample = client.samples.create(
                        project_id=project_id,
                        metadata=sample_data
                    )
                    click.echo(f"    ✅ Created experiment with sample {sample_id} (Sample ID: {sample.sample_id}, Experiment ID: {sample.id})")
                    total_samples += 1
                except Exception as e:
                    if 'Pair association of Sample ID and Strain ID already exists' in str(e):
                        click.echo(f"    ⚠️  Sample {sample_id} already exists, will upload files to existing sample", err=False)
                        duplicate_sample_names_by_project[project_name].add(sample_id)
                    else:
                        click.echo(f"    ❌ Failed to create experiment {sample_id}: {str(e)}", err=True)
        
        click.echo(f"\n✅ Successfully created {total_samples} experiment(s) with samples across {len(project_lookup)} project(s)")
        
        filename_context = {}
        try:
            for sd in samples_data:
                proj = sd.get('project')
                sname = sd.get('sample_name')
                for key in ('r1_fastq_filename', 'r2_fastq_filename', 'fasta_filename'):
                    fn = sd.get(key)
                    if fn:
                        filename_context[os.path.basename(fn)] = {
                            'project': proj,
                            'sample_name': sname
                        }
        except Exception:
            filename_context = {}

        # Step 4: Upload files
        click.echo("\n📁 Step 4: Uploading files...")
        total_uploaded = 0
        total_skipped = 0
        total_files_attempted = 0
        for project_name, project_id in project_lookup.items():
            click.echo(f"Uploading files for project: {project_name} (ID: {project_id})")
            
            try:
                def progress_callback(current, total, filename):
                    click.echo(f"  Uploading {current}/{total}: {filename}")
                
                results = client.batch.upload_files_for_project(
                    project_id=project_id,
                    files_directory=data_dir,
                    file_pattern=file_pattern,
                    progress_callback=progress_callback,
                    tsv_data=samples_data,
                    exclude_sample_names=[] 
                )
                
                # Show results
                total_files_attempted += len(results)
                successful = [r for r in results if r['success']]
                failed = [r for r in results if not r['success']]
                skipped = [r for r in results if not r['success'] and 'already uploaded' in r.get('error', '').lower()]
                actual_failures = [r for r in results if not r['success'] and 'already uploaded' not in r.get('error', '').lower()]
                
                click.echo(f"  ✅ Successfully uploaded {len(successful)} files")
                if skipped:
                    click.echo(f"  ⏭️  Skipped {len(skipped)} files (already uploaded)")
                    total_skipped += len(skipped)
                if actual_failures:
                    click.echo(f"  ❌ Failed to upload {len(actual_failures)} files:")
                    for fr in actual_failures[:20]:
                        path = fr.get('file_path')
                        err_msg = fr.get('error')
                        sample_name = fr.get('sample_name')
                        derived_project = None
                        if path:
                            filename = os.path.basename(path)
                            ctx = filename_context.get(filename)
                            if ctx:
                                derived_project = ctx.get('project')
                                if not sample_name:
                                    sample_name = ctx.get('sample_name')
                        context_parts = []
                        if derived_project:
                            context_parts.append(f"project: {derived_project}")
                        if sample_name:
                            context_parts.append(f"sample: {sample_name}")
                        context = f" [" + ", ".join(context_parts) + "]" if context_parts else ""
                        click.echo(f"    - {path or 'unknown'}: {err_msg}{context}")
                    if len(actual_failures) > 20:
                        click.echo(f"    ... and {len(actual_failures) - 20} more")
                
                total_uploaded += len(successful)
                
            except Exception as e:
                click.echo(f"  ❌ Error uploading files for project {project_name}: {e}", err=True)
        
        click.echo("\n######## Recap ########")
        click.echo(f"\n🎉 Complete workflow finished!")
        click.echo(f"   Projects found: {len(project_lookup)}")
        click.echo(f"   Experiments created: {total_samples}/{total_samples_expected}")
        click.echo(f"   Files uploaded successfully: {total_uploaded}/{total_files_attempted}")
        if total_skipped > 0:
            click.echo(f"   Files skipped (already uploaded): {total_skipped}")
        click.echo(f"   File type detected: {file_type.upper()}")

        if missing_projects:
            click.echo("\n⚠️  Missing projects detected (files for these projects were skipped):", err=True)
            for p in sorted(missing_projects):
                click.echo(f"   - {p}", err=True)
            click.echo("\n👉 Create the missing projects, for example:")
            for p in sorted(missing_projects):
                click.echo(f"   abromics --api-key <API_KEY> --base-url <BASE_URL> project create --name '{p}' --template <TEMPLATE_ID>")

        
    except Exception as e:
        click.echo(f"❌ Error in complete workflow: {e}", err=True)







if __name__ == '__main__':
    cli()
