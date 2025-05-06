import os
from pathlib import Path
from markdown_blocks import markdown_to_html_node


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir_path, exist_ok=True)
    
    for item in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, item)
        
        # If it's a file
        if os.path.isfile(source_path):
            # Only process markdown files
            if source_path.endswith('.md'):
                # Change extension from .md to .html while preserving the path
                file_name = os.path.basename(item)
                html_file_name = os.path.splitext(file_name)[0] + '.html'
                dest_file_path = os.path.join(dest_dir_path, html_file_name)
                
                # Generate the HTML page
                generate_page(source_path, template_path, dest_file_path, basepath)
        
        # If it's a directory, recurse into it
        else:
            # Create corresponding subdirectory in destination
            new_source_dir = source_path
            new_dest_dir = os.path.join(dest_dir_path, item)
            
            # Recursively process the subdirectory
            generate_pages_recursive(new_source_dir, template_path, new_dest_dir, basepath)


def generate_page(from_path, template_path, dest_path, basepath):
    print(f" * {from_path} {template_path} -> {dest_path}")
    from_file = open(from_path, "r")
    markdown_content = from_file.read()
    from_file.close()

    template_file = open(template_path, "r")
    template = template_file.read()
    template_file.close()

    node = markdown_to_html_node(markdown_content)
    html = node.to_html()

    title = extract_title(markdown_content)
    
    # Replace content and title
    complete_html = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    # Replace URLs
    complete_html = complete_html.replace('href="/', f'href="{basepath}')
    complete_html = complete_html.replace('src="/', f'src="{basepath}')

    # Create directory if needed
    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
        
    # Write to file
    to_file = open(dest_path, "w")
    to_file.write(complete_html)  # Use complete_html, not template
    to_file.close()  # Don't forget to close the file


def extract_title(md):
    lines = md.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:]
    raise ValueError("no title found")
