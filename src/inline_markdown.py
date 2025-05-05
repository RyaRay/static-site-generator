from textnode import  *
from htmlnode import *
import re
from enum import Enum, auto

class BlockType(Enum):
    HEADING = auto()
    CODE = auto()
    QUOTE = auto()
    UNORDERED_LIST = auto()
    ORDERED_LIST = auto()
    PARAGRAPH = auto()

def block_to_block_type(block: str) -> BlockType:
    lines = block.split('\n')

    # Check for code block
    if block.startswith('```') and block.endswith('```'):
        return BlockType.CODE

    # Check for heading
    if re.match(r'#{1,6} ', lines[0]):
        return BlockType.HEADING

    # Check for quote block
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE

    # Check for unordered list
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST

    # Check for ordered list
    if all(re.match(fr'{i+1}\. ', line) for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST

    # Default: paragraph
    return BlockType.PARAGRAPH


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images(text):
    pattern = r"!\[(.*?)\]\((.*?)\)"  # Capture both alt text and URL
    matches = re.findall(pattern, text)
    return matches  # Return tuples of (alt text, URL)

def extract_markdown_links(text):
    pattern = r"\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    return [(match[0], match[1]) for match in matches]

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        text = old_node.text
        pattern = r"!\[(.*?)\]\((.*?)\)"
        last_index = 0
        for match in re.finditer(pattern, text):
            start, end = match.span()
            if start > last_index:
                new_nodes.append(TextNode(text[last_index:start], TextType.TEXT))
            alt_text, url = match.groups()
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            last_index = end
        if last_index < len(text):
            new_nodes.append(TextNode(text[last_index:], TextType.TEXT))
    return new_nodes
    

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        pattern = r"\[(.*?)\]\((.*?)\)"
        last_index = 0
        
        for match in re.finditer(pattern, text):
            start, end = match.span()
            # Add text before the link
            if start > last_index:
                new_nodes.append(TextNode(text[last_index:start], TextType.TEXT))
            
            # Add the link
            link_text, url = match.groups()
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            
            last_index = end
        
        # Add any remaining text after the last link
        if last_index < len(text):
            new_nodes.append(TextNode(text[last_index:], TextType.TEXT))
    
    return new_nodes

def text_to_textnodes(text):
    # Start with basic text nodes
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Process images first (they have higher precedence)
    nodes = split_nodes_image(nodes)
    
    # Process links
    nodes = split_nodes_link(nodes)
    
    # Process bold text
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    
    # Process italic text
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

    # process code text
    ndoes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes

def markdown_to_blocks(markdown):
    # Split the markdown by blank lines
    blocks = []
    lines = markdown.split("\n")
    current_block = []
    
    for line in lines:
        if line.strip() == "":
            if current_block:
                blocks.append("\n".join(current_block))
                current_block = []
        else:
            current_block.append(line)
    
    if current_block:
        blocks.append("\n".join(current_block))
    
    return blocks

def inline_markdown_to_text_nodes(text):    
    # Convert a text string with inline markdown to a list of TextNode objects
    blocks = markdown_to_blocks(text)
    text_nodes = []
    for block in blocks:        
        text_nodes.extend(text_to_textnodes(block))
    return text_nodes
def text_to_children(text):
    # Convert a text string with inline markdown to a list of HTMLNode objects
    text_nodes = inline_markdown_to_text_nodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        html_nodes.append(html_node)
    return html_nodes

def count_heading_level(block):
    # Count the number of '#' at the beginning of the block
    level = 0
    for char in block:
        if char == '#':
            level += 1
        else:
            break
    return min(level, 6)  # HTML supports h1 to h6

def extract_code_block_content(block):
    # Remove the triple backticks and extract the code content
    lines = block.split('\n')
    # Remove the first and last line (which contain the ```)
    code_lines = lines[1:-1]
    return '\n'.join(code_lines)

def markdown_to_html_node(markdown):
    # Split markdown into blocks
    blocks = markdown_to_blocks(markdown)

    # Create parent HTML node
    parent_node = HTMLNode("div", None, None, [])
    parent_node.children = []
    
    # Loop over each block
    for block in blocks:
        # Determine block type
        block_type = block_to_block_type(block)
        
        # Based on block type, create appropriate HTML node
        if block_type == BlockType.PARAGRAPH:
            node = HTMLNode("p", None)
            # Add children through text_to_children
            node.children = text_to_children(block)
            parent_node.children.append(node)
        elif block_type == BlockType.HEADING:
            level = count_heading_level(block)
            node = HTMLNode(f"h{level}", None)
            # Strip the '#' characters and leading/trailing spaces
            text = block.replace('#', '', level).strip()
            node.children = text_to_children(text)
            parent_node.children.append(node)
        # Handle other block types...
        elif block_type == BlockType.CODE:
            # Special case for code blocks
            pre_node = HTMLNode("pre", None)
            code_node = HTMLNode("code", None)
            # Don't parse inline markdown for code blocks
            # Strip the ``` markers and add raw text
            code_text = extract_code_block_content(block)
            text_node = TextNode(code_text, TextType.TEXT)
            code_node.children = [text_node_to_html_node(text_node)]
            pre_node.children = [code_node]
            parent_node.children.append(pre_node)

        elif block_type == BlockType.QUOTE:
            node = HTMLNode("blockquote", None)
            # Remove '>' characters from the beginning of each line
            text = '\n'.join([line.lstrip('>').strip() for line in block.split('\n')])
            node.children = text_to_children(text)
            parent_node.children.append(node)

        elif block_type == BlockType.UNORDERED_LIST:
            ul_node = HTMLNode("ul", None)
            ul_node.children = []
            # Split block into list items and remove the leading '- ' or '* '
            list_items = [line.lstrip('- *').strip() for line in block.split('\n') if line.strip()]
            
            for item in list_items:
                li_node = HTMLNode("li", None)
                li_node.children = text_to_children(item)
                ul_node.children.append(li_node)
            
            parent_node.children.append(ul_node)

        elif block_type == BlockType.ORDERED_LIST:
            ol_node = HTMLNode("ol", None)
            ol_node.children = []
            # Split block into list items and remove the leading numbers and periods
            list_items = []
            for line in block.split('\n'):
                if line.strip():
                    # Find the index after the period and strip
                    parts = line.split('. ', 1)
                    if len(parts) > 1:
                        list_items.append(parts[1].strip())
            
            for item in list_items:
                li_node = HTMLNode("li", None)
                li_node.children = text_to_children(item)
                ol_node.children.append(li_node)
            
            parent_node.children.append(ol_node)

    return parent_node
