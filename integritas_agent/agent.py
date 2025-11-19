# import os
import io
import json
import hashlib
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools import ToolContext

# _allowed_path = os.path.dirname(os.path.abspath(__file__))

async def get_file_hash(tool_context: ToolContext) -> str:
    """
    This tool is used to get the hash of the file content from the artifact.
    Args:
        tool_context: ToolContext
    Returns:
        str: The hash of the file content
    """
    artifact_ids = await tool_context.list_artifacts()
    artifact_id = artifact_ids[0]
    
    try:
        print( "The document type is: ", artifact_id )
        artifact_content = await tool_context.load_artifact(artifact_id)
        
        # Get the file content as bytes
        file_bytes = artifact_content.inline_data.data
        
        # Generate SHA3-256 hash
        hash_obj = hashlib.sha3_256()
        hash_obj.update(file_bytes)
        file_hash = hash_obj.hexdigest()
        
        # Return the hash as a string (you can also return both content and hash if needed)
        return file_hash
    except Exception as e:
        return f"Error getting artifact content: {e}"

async def get_json_proof(tool_context: ToolContext) -> str:
    """
    This tool is used to get the json proof from the artifact.
    Args:
        tool_context: ToolContext
    Returns:
        str: The json proof as a string
    """
    artifact_ids = await tool_context.list_artifacts()
    artifact_id = artifact_ids[0]
    

    print( "--------------------------------")
    print( "Starting to get the json proof..." )
    print( "--------------------------------")
    try:
        print( "The document type is: ", artifact_id )
        artifact_content = await tool_context.load_artifact(artifact_id)
        

        # Get the file content as bytes
        file_bytes = artifact_content.inline_data.data
        print( "--------------------------------")
        print( "The file bytes are: ", file_bytes )
        print( "--------------------------------")

        # Parse the JSON data
        json_proof = json.loads(file_bytes)
        print( "--------------------------------")
        print( "The json proof is: ", json_proof )
        print( "--------------------------------")
        # Return the JSON data as a string
        return str(json_proof)
    except Exception as e:
        return f"Error getting json proof: {e}"

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='integritas_agent',
    instruction=f"""\
        You are Integritas Agent — an assistant that securely verifies and stamps digital files using the Minima MCP service.

        IMPORTANT:
        Never modify user files directly.
        Always explain each action clearly before performing it.

        Your have two main tasks:

        1. Stamp_data (stamp the files hash):
        When the user uploads a non-json file, run the get_file_hash tool. Use the returned hash to and send it to stamp_data tool to stamp the file.
  

        2. Verify_data (verify the files hash):
        When the user uploads a json file, run the get_json_proof tool. Use the returned json proof and send it to verify_data tool to verify the file.
    
    """,
    tools=[
        get_file_hash,
        get_json_proof,
        MCPToolset(
            connection_params=SseConnectionParams(
                url='https://integritas.minima.global/mcp-sse/',
                #url='http://127.0.0.1:8787/sse',
                # headers={'Accept': 'text/event-stream'},
            ),
            # don't want agent to do write operation
            # you can also do below
            # tool_filter=lambda tool, ctx=None: tool.name
            # not in [
            #     'write_file',
            #     'edit_file',
            #     'create_directory',
            #     'move_file',
            # ],
            tool_filter=[
                'stamp_data',
                'verify_data',
                'auth_set_api_key',
                'auth_get_api_key',
                'auth_clear_api_key',
                'ready',
                'health',
            ],
        )
    ],
)
