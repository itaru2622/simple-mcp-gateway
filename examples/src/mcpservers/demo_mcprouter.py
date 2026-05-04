#!/usr/bin/env python

from fastmcp import FastMCP
from utils.mcprouter import MCPRouter

# in development, create and use MCPRouter instance, instead of FastMCP instance
router = MCPRouter()

@router.tool
def echo_tool(text: str) -> str:
    """Echo the input text"""
    return text


@router.resource("echo://static")
def echo_resource() -> str:
    return "Echo!"


@router.resource("echo://{text}")
def echo_template(text: str) -> str:
    """Echo the input text"""
    return f"Echo: {text}"


@router.prompt("echo")
def echo_prompt(text: str) -> str:
    return text

# for deployment, register components in router to specific FastMCP instance.
mcp = FastMCP()
router.register_to(mcp)
