# Advanced Tool Use for Factory.ai Droid CLI

Research and implementation of advanced tool use patterns to enhance Factory.ai Droid CLI capabilities.

## Goal

Implement cutting-edge tool use patterns from Anthropic and Cloudflare research to make Droid CLI more efficient, capable of handling larger tool libraries, and better at complex multi-step workflows.

## Key Concepts

| Pattern | Description | Benefit |
|---------|-------------|---------|
| **Code Mode** | Have Claude write code to call tools instead of direct tool calling | LLMs handle complex tools better as code APIs |
| **Tool Search Tool** | Dynamic tool discovery with semantic search | 85-90% reduction in context usage |
| **Programmatic Tool Calling** | Execute tools from code in sandbox | Filter results before context, reduce latency |
| **Tool Use Examples** | Provide input_examples for better patterns | Improved tool usage accuracy |
| **Code Execution with MCP** | Present MCP servers as code APIs | Unlimited tool libraries, efficient orchestration |

## Research References

- [Code Mode: The Better Way to Use MCP](https://blog.cloudflare.com/code-mode/) - Cloudflare
- [Advanced Tool Use on Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use) - Anthropic
- [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) - Anthropic
- [Tool Search Tool Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)
- [Programmatic Tool Calling Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)
- [Tool Use Examples](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use#providing-tool-use-examples)

### Cookbooks

- [Tool Search with Embeddings](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/tool_search_with_embeddings.ipynb)
- [Programmatic Tool Calling](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/programmatic_tool_calling_ptc.ipynb)

## Status

**Phase**: Research & Goal Definition
