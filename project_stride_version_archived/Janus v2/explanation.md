# Janus v2: The Awakening

Welcome to the next evolution. If you’ve wondered why this project is called "Janus," keep wondering. I’ll reveal the significance of the two-faced god in Janus v3. For now, focus on the facts.

*Janus v1* was a starting point but it was incomplete in many ways, it could talk but it couldn't touch the world. To undestand what am I talking about, go and read *Janus v1* `explanation.md`, anyways
*Janus v2* was needed now it has a big advantage over v1 and that is new Janus has **tools** real time tools.

# Tools In Janus: The Power of MCP

Before I discovered MCP,  I was using standard Langchain `@tool` decorators to create tools they work but they lack a dedicated infrastructure to touch grass I mean to touch the world.

I am introducing Janus v2 with **MCP tools** and the very first tool for this version is `datetime`. Now, Janus doesn't juess guess what day or time it is based on training data, it queries the host system directly You can ask Janus for today's date or time given where you are and it may give you right answer.

You see there are two way's to achieve tools in MCP before I explain that let's get a quick explanation about MCP.

# What is MCP?

MCP stands for *Model Context Protocol*. It is a robust moethod introduced in Langchain to connect external services to your or our model. 
Without it you would have to write your own configuration which is pain to deal with and prone to lot's of error. MCP provide a library called
`FastMCP` from fastmcp.server. This library does all the heavy lifting for you from creating session's to handling handshake with the client.

MCP provides a unified way to handle:
              
              1. Discovery: The model "asks" what the server can do.
              2.Execution: The model "calls" a tool.
              3.Transport: How the data moves

MCP has two ways to handle transport.
1. StreamingHTTP
2. stdio

To know more about MCP go to `MCP` folder in Langchain repo.

Note : Janus uses the stdio (Standard Input/Output) transport. This means the server lives locally on the machine, providing zero-latency, private, and secure access to system resources.

# Standard Method

Creating MCP tool require's *client* - *server* method. In which `Janus_v2.py` is the client, client stays where your main model is defined.
Server can be anywhere in your system since we're working with *stdio* transport basically it's the server stays locally in your computer instead of internet. 

# The Twist
Most people use the FastMCP library because it does the heavy lifting—handling sessions and handshakes automatically. Janus v2 does not use FastMCP.

Instead, I have created my own server using **Standard Low-Level Method**, I wrote the JSON-RPC configurations and the handshake logic by hand. 

You ask, why? 

# The Reason

Well I m not a ~~Masochist~~(mostly) who love to deal with syntax errors, but I believe to truly understand the power of your model (Car) I have to understand the "Engine", By writing the server from scarch, I have total control over the "Switchboard logic"

In short : Janus is about **Native Programming**

# Current Janus Capabilities:
1. **Custom Multi-Model Router**: It has a self-written (ofcourse by me) heuristic engine that decides between a "Fast model and a "Smart" model without LLM overhead.
2. **Standard MCP Server**: A low level enginer currently hosting our `datetime` tool, built for scalability.
   

# What's next?
*Janus v2* does not have very drastic changes yet but it finally has hand's now and it's not a just a useless bot anymore.
I m going to explain how `janus-server` work in great detail in MCP folder.

*Janus v3* is already in forge, it will have drastic changes. 

Stay tuned.

