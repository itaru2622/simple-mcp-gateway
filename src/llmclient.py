#!/usr/bin/env python3

# starts workaround : add  code to ignore warning
import warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1 functionality isn't compatible with.*")
# ends workaround : add  code to ignore warning

from   langchain_mcp_adapters.client import MultiServerMCPClient
#from   langchain_openai import AzureChatOpenAI
#from   langgraph.prebuilt import create_react_agent
#from   langchain_core.prompts import ChatPromptTemplate
#from   langchain_core.output_parsers import PydanticOutputParser
from   pydantic import BaseModel
from   typing import Any
import asyncio
import sys
import argparse
import json
from utils.conf import load


async def test(conf:dict[str,Any]={}, msg:dict[str,Any]={}, **kwargs: Any) -> Any:
    '''partial process of LLM x MCP with langchain

    Arg:
      - conf (dict): config

    Returns:
      - Any: result
    '''

    client = MultiServerMCPClient( conf.get('mcpServers') )
    tools = await client.get_tools()

    # apiKey = os.environ['CHATAI_API_KEY']
    # apiURL = os.environ['CHATAI_URL']
    # llm = AzureChatOpenAI( api_key=apiKey, azure_endpoint=apiURL, openai_api_version='DUMMY',)
    # agent = create_react_agent(llm, tools, **kwargs)
    # resp = await agent.ainvoke(msg)
    # content = resp['messages'][-1].content
    # outputParser = PydanticOutputParser(pydantic_object=BaseModel)
    # rtn = outputParser.parse(content)
    # return rtn

    return tools


def get_event_loop() -> Any:
    '''get async event loop'''

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


if __name__ =='__main__':

    parser = argparse.ArgumentParser()  
    parser.add_argument('-c', '--config',       help='config file path(yaml)', default='/dev/stdin')
    opts = parser.parse_args()

    conf = load(opts.config)

    loop = get_event_loop()
    resp = loop.run_until_complete(asyncio.gather( test(conf)))[0]
    resp = [ r.model_dump(exclude=['func','coroutine']) for r in resp ] # jsonable data by excluding func,coroutine
    print(json.dumps(resp, indent=2, ensure_ascii=False))
