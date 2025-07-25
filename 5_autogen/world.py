from __future__ import annotations

import asyncio

import messages
from agent import Agent
from autogen_core import AgentId
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost
from creator import Creator

HOW_MANY_AGENTS = 3

async def create_and_message(worker, creator_id, i: int):
    try:
        result = await worker.send_message(messages.Message(content=f"agent{i}.py"), creator_id)
        with open(f"idea{i}.md", 'w') as f:
            f.write(result.content)
    except Exception as e:
        print(f"Failed to run worker {i} due to exception: {e}")

async def main():
    host = GrpcWorkerAgentRuntimeHost(address='localhost:50051')
    host.start()
    worker = GrpcWorkerAgentRuntime(host_address='localhost:50051')
    await worker.start()
    await Creator.register(worker, 'Creator', lambda: Creator('Creator'))
    creator_id = AgentId('Creator', 'default')
    coroutines = [create_and_message(worker, creator_id, i) for i in range(1, HOW_MANY_AGENTS+1)]
    await asyncio.gather(*coroutines)
    try:
        await worker.stop()
        await host.stop()
    except Exception as e:
        print(e)




if __name__ == '__main__':
    asyncio.run(main())
