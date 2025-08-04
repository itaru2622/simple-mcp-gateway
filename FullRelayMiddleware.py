from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext
from fastmcp.tools.tool import Tool
from fastmcp.prompts.prompt import Prompt
from fastmcp.resources.resource import Resource
from fastmcp.resources.template import ResourceTemplate
from fastmcp.utilities.logging import get_logger
import mcp.types as mt

import logging

from typing import Any

logger = get_logger(__name__)

#cf. https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/middleware/middleware.py

class FullRelayMiddleware(Middleware):

    def __init__(self):
        pass

    def logging(self, fname: str='', msg: str='', log_level: int=logging.INFO) -> None:
        heading = f'{self.__class__.__name__}::{fname}'
        logger.log(log_level, f'{heading} {msg}')


    async def on_message(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        #return await call_next(context)
        fname='on_message'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_request(
        self,
        context: MiddlewareContext[mt.Request],
        call_next: CallNext[mt.Request, Any],
    ) -> Any:
        #return await call_next(context)
        fname='on_request'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_notification(
        self,
        context: MiddlewareContext[mt.Notification],
        call_next: CallNext[mt.Notification, Any],
    ) -> Any:
        #return await call_next(context)
        fname='on_notification'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, mt.CallToolResult],
    ) -> mt.CallToolResult:
        #return await call_next(context)
        fname='on_call_tool'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_read_resource(
        self,
        context: MiddlewareContext[mt.ReadResourceRequestParams],
        call_next: CallNext[mt.ReadResourceRequestParams, mt.ReadResourceResult],
    ) -> mt.ReadResourceResult:
        #return await call_next(context)
        fname='on_read_resource'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_get_prompt(
        self,
        context: MiddlewareContext[mt.GetPromptRequestParams],
        call_next: CallNext[mt.GetPromptRequestParams, mt.GetPromptResult],
    ) -> mt.GetPromptResult:
        #return await call_next(context)
        fname='on_get_prompt'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_list_tools(
        self,
        context: MiddlewareContext[mt.ListToolsRequest],
        call_next: CallNext[mt.ListToolsRequest, list[Tool]],
    ) -> list[Tool]:
        #return await call_next(context)
        fname='on_list_tools'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_list_resources(
        self,
        context: MiddlewareContext[mt.ListResourcesRequest],
        call_next: CallNext[mt.ListResourcesRequest, list[Resource]],
    ) -> list[Resource]:
        #return await call_next(context)
        fname='on_list_resources'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_list_resource_templates(
        self,
        context: MiddlewareContext[mt.ListResourceTemplatesRequest],
        call_next: CallNext[mt.ListResourceTemplatesRequest, list[ResourceTemplate]],
    ) -> list[ResourceTemplate]:
        #return await call_next(context)
        fname='on_list_resource_templates'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result


    async def on_list_prompts(
        self,
        context: MiddlewareContext[mt.ListPromptsRequest],
        call_next: CallNext[mt.ListPromptsRequest, list[Prompt]],
    ) -> list[Prompt]:
        #return await call_next(context)
        fname='on_list_prompts'
        self.logging(fname, f'starts: {context=}', log_level=logging.DEBUG)
        result = await call_next(context)
        self.logging(fname, f'ends: {context=} {result=}')
        return result
