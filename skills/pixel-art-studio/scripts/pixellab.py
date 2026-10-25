"""Optional PixelLab MCP client: discover live tools and submit explicit requests."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import sys


async def run(args):
    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    token=os.environ.get('PIXELLAB_API_KEY')
    if not token:
        raise ValueError('Set PIXELLAB_API_KEY to your PixelLab API token.')
    async with httpx.AsyncClient(headers={'Authorization':'Bearer '+token},
                                 timeout=httpx.Timeout(60,read=300),follow_redirects=False) as client:
        async with streamable_http_client('https://api.pixellab.ai/mcp',http_client=client) as (read,write,_):
            async with ClientSession(read,write) as session:
                await session.initialize()
                if args.command in ('list','schema'):
                    available=[]
                    cursor=None
                    while True:
                        result=await session.list_tools(cursor=cursor)
                        available.extend(result.tools)
                        cursor=result.nextCursor
                        if not cursor:break
                    if args.command=='list':
                        return [{'name':tool.name,'description':tool.description} for tool in available]
                    matches=[tool.model_dump(mode='json') for tool in available if tool.name==args.tool]
                    if not matches:raise ValueError('Tool is unavailable; run list to discover the current catalog.')
                    return matches[0]
                arguments=json.loads(args.arguments.read_text(encoding='utf-8'))
                result=await session.call_tool(args.tool,arguments=arguments)
                data=result.model_dump(mode='json',exclude_none=True)
                if result.isError:
                    print(json.dumps(data,ensure_ascii=False,indent=2),file=sys.stderr)
                    raise ValueError('PixelLab returned a tool error.')
                return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list',help='List live tools and descriptions')
    p=sub.add_parser('schema',help='Read a live tool input schema');p.add_argument('tool')
    p=sub.add_parser('call',help='Call a tool; generation requests consume account credits')
    p.add_argument('tool');p.add_argument('arguments',type=Path)
    args=parser.parse_args()
    try:print(json.dumps(asyncio.run(run(args)),ensure_ascii=False,indent=2))
    except ImportError:parser.exit(2,'Install the optional requirements-pixellab.txt dependencies first.\n')
    except (OSError,ValueError) as error:parser.exit(2,f'Error: {error}\n')


if __name__=='__main__':main()
