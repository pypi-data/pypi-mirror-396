'''
Author: 凌逆战 | Never
Date: 2025-08-22 23:41:13
Description: pip install 'markitdown[all]
'''
import os
from markitdown import MarkItDown

from neverlib.utils import get_path_list

source_dir = "./html"
target_dir = "./markdown"
html_path_list = get_path_list(source_dir, end="*.html")

for html_path in html_path_list:
    html_name = os.path.basename(html_path)
    md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
    result = md.convert(html_path)
    # print(result.text_content)
    
    # 写入文件
    with open(os.path.join(target_dir, html_name.replace(".html", ".md")), "w") as f:
        f.write(result.text_content)
    



