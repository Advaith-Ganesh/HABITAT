"""Isolated parser process; stdin bytes and stdout JSON only. Never execute PDF text."""
import json
import sys
import resource
from backend.document_analysis import analyse, MAX_BYTES

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(3,3))
    # macOS may not enforce address-space limits. The parent always has a wall timeout.
    try: resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    except (ValueError,OSError): pass
    try:
        data=sys.stdin.buffer.read(MAX_BYTES+1)
        result=analyse(data,sys.argv[1],baseline=len(sys.argv)>2 and sys.argv[2]=='baseline')
        print(result.model_dump_json())
    except Exception:
        # Do not return library errors which may echo uploaded content.
        print(json.dumps({'error':'PDF rejected: invalid, encrypted, unmarked, unsupported or resource-limited. Use a marked synthetic PDF, at most 2 MiB and 5 pages.'}))
        sys.exit(2)
if __name__=='__main__':main()
