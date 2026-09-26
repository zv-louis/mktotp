# encoding: utf-8

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cairosvg>=2.8.2",
#     "fastmcp>=2.11.3",
#     "filelock>=3.18.0",
#     "opencv-python>=4.12.0.88",
#     "pillow>=10.0.0",
#     "pydantic>=2.11.7",
#     "pyotp>=2.9.0",
# ]
# ///

'''
EntryPoint for Claude plugin MCP Server
'''

from mktotp.__main__ import main

if __name__ == "__main__":
    main()
