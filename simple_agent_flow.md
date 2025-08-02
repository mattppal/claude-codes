# Simple Agent Flow

```mermaid
flowchart TD
    Start([Start]) --> UserInput[Get User Input]
    UserInput --> Claude[Send to Claude]
    Claude --> NeedsTools{Needs Tools?}
    
    NeedsTools -->|No| ShowResponse[Show Response]
    NeedsTools -->|Yes| ExecuteTools[Execute Tools]
    
    ExecuteTools --> SendResults[Send Results to Claude]
    SendResults --> Claude
    
    ShowResponse --> UserInput
    
    subgraph Tools[Available Tools]
        FileOps[File Operations<br/>view, create, edit]
        WebSearch[Web Search]
        BashCmd[Bash Commands]
    end
    
    ExecuteTools -.-> Tools
```

## Core Structure

The agent is just **two nested loops**:

1. **Outer Loop**: Get user input → Send to Claude → Show response
2. **Inner Loop**: If Claude needs tools → Execute them → Send results back

## Tools

- **File Operations**: Read, create, and edit files
- **Web Search**: Search the internet for information  
- **Bash Commands**: Run shell commands for testing, installation, etc.

That's it! A coding agent in ~200 lines.