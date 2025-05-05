from textnode import  *
from htmlnode import *
import re

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
        split_nodes = []
        sections = extract_markdown_links(old_node.text)
        for section in sections:
            text, url = section
            split_nodes.append(TextNode(text, TextType.LINK, url))
        new_nodes.extend(split_nodes)
    return new_nodes

def text_to_textnodes(text):
    text = text.replace("\n", " ")
    text = text.replace("\r", "")
    text = text.replace("\t", "")
    text = text.strip()
    if len(text) == 0:
        return []
    return [TextNode(text, TextType.TEXT)]

def markdown_to_blocks(markdown):
    text_nodes = text_to_textnodes(markdown)
    text_nodes = split_nodes_link(text_nodes)
    text_nodes = split_nodes_image(text_nodes)
    text_nodes = split_nodes_delimiter(text_nodes, "**", TextType.BOLD)
    text_nodes = split_nodes_delimiter(text_nodes, "_", TextType.ITALIC)
    text_nodes = split_nodes_delimiter(text_nodes, "`", TextType.CODE)
    return [text_node_to_html_node(text_node) for text_node in text_nodes]