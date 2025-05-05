from textnode import TextNode, TextType
from htmlnode import HTMLNode
from inline_markdown import *
import os
import shutil


def main():
    static_to_public()
    generate_page(
        "content/index.md",
        "template.html",
        "public/index.html"
    )

#write a recursive func that moves static file to public
def static_to_public():
    #delete all contents of public
    if os.path.exists("public"):
        shutil.rmtree("public")
    #create public if it does not exist
    os.mkdir("public")
    #copy all files from static to public
    copy_recursive("static", "public")

def copy_recursive(src, dest):
    for file in os.listdir(src):
        src_file = os.path.join(src, file)
        dest_file = os.path.join(dest, file)
        if os.path.isdir(src_file):
            os.mkdir(dest_file)
            copy_recursive(src_file, dest_file)
        else:
            shutil.copy(src_file, dest_file) 

def extract_title(markdown):
    for line in markdown.splitlines():
        line = line.strip()
        if line.startswith("# ") and not line.startswith("##"):  # Check for H1 header
            return line.lstrip("#").strip()  # Remove '#' and extra spaces
    raise ValueError("No H1 header found in the markdown")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    with open(from_path, 'r') as markdown_file:
        markdown_content = markdown_file.read()
    
    # Read the template file
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract the title
    title = extract_title(markdown_content)
    
    # Replace placeholders in the template
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Write the full HTML to the destination file
    with open(dest_path, 'w') as dest_file:
        dest_file.write(full_html)

if __name__ == "__main__":
    main()