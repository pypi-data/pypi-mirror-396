"""
CLI interface for PyStruct using Click.
"""

import sys
from pathlib import Path
import click

from pyclassstruct.analyzer import analyze_file, analyze_folder, can_detect_structure
from pyclassstruct.generator import generate_structure, check_needs_user_input
from pyclassstruct.reporter import generate_report, generate_classes_txt
from pyclassstruct.utils import check_file_exists, is_python_file, is_directory


@click.group()
@click.version_option(version="1.0.0", prog_name="pystruct")
def main():
    """
    PyClassStruct - Convert Python scripts to class-based structures.
    
    Use 'pyclassstruct analyze' to analyze files and generate reports.
    Use 'pyclassstruct convert' to convert scripts to structured classes.
    """
    pass


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output directory for reports')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing report.txt and classes.txt')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def analyze(path, output, force, verbose):
    """
    Analyze Python file(s) and generate report.txt and classes.txt.
    
    PATH can be a single Python file or a directory containing Python files.
    
    Examples:
    
        pystruct analyze ./my_script.py
        
        pystruct analyze ./my_folder
        
        pystruct analyze ./my_folder --force
    """
    path = Path(path).resolve()
    
    # Determine output directory
    if output:
        output_dir = Path(output)
    elif path.is_file():
        output_dir = path.parent
    else:
        output_dir = path
    
    report_path = output_dir / "report.txt"
    classes_path = output_dir / "classes.txt"
    
    # Check for existing files
    if not force:
        if report_path.exists():
            click.echo(click.style(f"⚠ report.txt already exists at {report_path}", fg='yellow'))
            click.echo("  Please delete it or use --force to overwrite.")
            # Continue to print report but don't save
            save_report = False
        else:
            save_report = True
            
        if classes_path.exists():
            click.echo(click.style(f"⚠ classes.txt already exists at {classes_path}", fg='yellow'))
            click.echo("  Please delete it or use --force to overwrite.")
            save_classes = False
        else:
            save_classes = True
    else:
        save_report = True
        save_classes = True
    
    # Perform analysis
    click.echo(click.style(f"\n📂 Analyzing: {path}", fg='blue'))
    
    try:
        if path.is_file():
            if not is_python_file(str(path)):
                click.echo(click.style(f"✗ Not a Python file: {path}", fg='red'))
                sys.exit(1)
            analysis = analyze_file(str(path))
            click.echo(f"  Found {len(analysis.functions)} functions")
            click.echo(f"  Found {len(analysis.global_vars)} global variables")
        else:
            analysis = analyze_folder(str(path))
            click.echo(f"  Analyzed {analysis.total_files} Python files")
            click.echo(f"  Found {len(analysis.all_functions)} functions")
            click.echo(f"  Found {len(analysis.all_global_vars)} global variables")
    except Exception as e:
        click.echo(click.style(f"✗ Error during analysis: {e}", fg='red'))
        sys.exit(1)
    
    # Check if structure can be detected
    if not can_detect_structure(analysis):
        click.echo(click.style("\n⚠ Could not automatically detect class structure.", fg='yellow'))
        click.echo("  Please define your classes in classes.txt manually.")
    else:
        click.echo(click.style(f"\n✓ Detected {len(analysis.class_proposals)} possible classes", fg='green'))
    
    # Generate report
    report_content = generate_report(analysis)
    
    click.echo("\n" + "=" * 60)
    click.echo(report_content)
    click.echo("=" * 60)
    
    if save_report:
        report_path.write_text(report_content, encoding='utf-8')
        click.echo(click.style(f"\n✓ Report saved to: {report_path}", fg='green'))
    
    # Generate classes.txt
    classes_content = generate_classes_txt(analysis)
    
    if verbose:
        click.echo("\n--- classes.txt content ---")
        click.echo(classes_content)
        click.echo("---")
    
    if save_classes:
        classes_path.write_text(classes_content, encoding='utf-8')
        click.echo(click.style(f"✓ Classes definition saved to: {classes_path}", fg='green'))
    
    click.echo("\n" + click.style("Next steps:", fg='cyan'))
    click.echo("  1. Review and edit classes.txt if needed")
    click.echo(f"  2. Run: pystruct convert {path}")


@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', default='structured', help='Output directory name')
@click.option('--classes', '-c', default=None, help='Path to classes.txt file')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing output')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def convert(path, output, classes, force, verbose):
    """
    Convert Python file(s) to structured class-based code.
    
    PATH can be a single Python file or a directory containing Python files.
    
    If classes.txt exists in the directory, it will be used.
    Otherwise, automatic structure detection will be attempted.
    
    Examples:
    
        pystruct convert ./my_script.py
        
        pystruct convert ./my_folder
        
        pystruct convert ./my_folder --classes ./custom_classes.txt
    """
    path = Path(path).resolve()
    
    # Perform analysis
    click.echo(click.style(f"\n📂 Analyzing: {path}", fg='blue'))
    
    try:
        if path.is_file():
            if not is_python_file(str(path)):
                click.echo(click.style(f"✗ Not a Python file: {path}", fg='red'))
                sys.exit(1)
            analysis = analyze_file(str(path))
            base_dir = path.parent
        else:
            analysis = analyze_folder(str(path))
            base_dir = path
    except Exception as e:
        click.echo(click.style(f"✗ Error during analysis: {e}", fg='red'))
        sys.exit(1)
    
    # Find classes.txt
    classes_txt_path = None
    if classes:
        classes_txt_path = Path(classes).resolve()
        if not classes_txt_path.exists():
            click.echo(click.style(f"✗ classes.txt not found: {classes_txt_path}", fg='red'))
            sys.exit(1)
    else:
        # Check for classes.txt in the directory
        default_classes_path = base_dir / "classes.txt"
        if default_classes_path.exists():
            classes_txt_path = default_classes_path
            click.echo(f"  Using classes.txt from: {classes_txt_path}")
    
    # Check if we can proceed
    needs_input = check_needs_user_input(analysis)
    if needs_input and not classes_txt_path:
        click.echo(click.style("\n⚠ Cannot automatically detect class structure.", fg='yellow'))
        click.echo("  Please create a classes.txt file to define the structure.")
        click.echo("\n  Run 'pystruct analyze' first to generate a template classes.txt")
        click.echo("\n  Format for classes.txt:")
        click.echo("    ClassName: function1, function2, function3")
        click.echo("    OtherClass: func4, func5")
        sys.exit(1)
    
    # Check output directory
    output_path = base_dir / output
    if output_path.exists() and not force:
        click.echo(click.style(f"\n⚠ Output directory already exists: {output_path}", fg='yellow'))
        if not click.confirm("Do you want to overwrite it?"):
            click.echo("Aborted.")
            sys.exit(0)
    
    # Generate structure
    click.echo(click.style("\n🔧 Generating structured code...", fg='blue'))
    
    try:
        success, message = generate_structure(
            analysis,
            output_dir=output,
            classes_txt_path=str(classes_txt_path) if classes_txt_path else None
        )
        
        if success:
            click.echo(click.style(f"\n✓ {message}", fg='green'))
            
            # List generated files
            if verbose:
                click.echo("\nGenerated files:")
                for f in output_path.glob("*.py"):
                    click.echo(f"  - {f.name}")
        else:
            click.echo(click.style(f"\n✗ {message}", fg='red'))
            sys.exit(1)
            
    except Exception as e:
        click.echo(click.style(f"\n✗ Error during conversion: {e}", fg='red'))
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    click.echo("\n" + click.style("Done!", fg='cyan'))
    click.echo(f"  Structured code generated in: {output_path}")


@main.command()
@click.argument('path', type=click.Path(exists=True))
def info(path):
    """
    Show quick information about a Python file or folder.
    
    Examples:
    
        pystruct info ./my_script.py
        
        pystruct info ./my_folder
    """
    path = Path(path).resolve()
    
    click.echo(click.style(f"\n📊 Quick Info: {path}\n", fg='blue'))
    
    try:
        if path.is_file():
            if not is_python_file(str(path)):
                click.echo(click.style(f"✗ Not a Python file: {path}", fg='red'))
                sys.exit(1)
            analysis = analyze_file(str(path))
            
            click.echo(f"  Type:           Single file")
            click.echo(f"  Functions:      {len(analysis.functions)}")
            click.echo(f"  Global vars:    {len(analysis.global_vars)}")
            click.echo(f"  Imports:        {len(analysis.imports)}")
            click.echo(f"  Classes found:  {len(analysis.class_proposals)}")
            
            if analysis.functions:
                click.echo(f"\n  Functions:")
                for f in analysis.functions[:10]:
                    click.echo(f"    • {f.name}")
                if len(analysis.functions) > 10:
                    click.echo(f"    ... and {len(analysis.functions) - 10} more")
        else:
            analysis = analyze_folder(str(path))
            
            click.echo(f"  Type:           Directory")
            click.echo(f"  Python files:   {analysis.total_files}")
            click.echo(f"  Functions:      {len(analysis.all_functions)}")
            click.echo(f"  Global vars:    {len(analysis.all_global_vars)}")
            click.echo(f"  Classes found:  {len(analysis.class_proposals)}")
            
            if analysis.file_analyses:
                click.echo(f"\n  Files:")
                for fa in analysis.file_analyses[:5]:
                    click.echo(f"    • {Path(fa.filepath).name}: {len(fa.functions)} functions")
                if len(analysis.file_analyses) > 5:
                    click.echo(f"    ... and {len(analysis.file_analyses) - 5} more")
                    
    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


if __name__ == "__main__":
    main()
