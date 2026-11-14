# encoding: utf-8

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cairosvg>=2.9.1",
#     "fastmcp>=3.4.10",
#     "filelock>=3.20.3",
#     "opencv-python>=4.12.0.88",
#     "pillow>=13.0.0",
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
