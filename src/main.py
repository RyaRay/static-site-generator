from textnode import TextNode, TextType
from htmlnode import HTMLNode
from inline_markdown import *
import os
import shutil


def main():
    text_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(text_node)
    static_to_public()

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
     

if __name__ == "__main__":
    main()