# 📁 Claude Desktop MCP Configuration File Location

## 🎯 Where to Add Your MCP Server Config

Claude Desktop reads MCP servers from a specific JSON configuration file:

### **macOS Location:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### **Windows Location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

## 📝 Configuration File Format

Create or edit the file with this structure:

```json
{
  "mcpServers": {
    "database-search": {
      "command": "python3",
      "args": ["mcp_database_server.py"],
      "cwd": "/Users/yuvraj/Desktop/Quilt"
    }
  }
}
```

## 🛠️ Step-by-Step Setup

### 1. Create the config directory (if needed):
```bash
# macOS
mkdir -p ~/Library/Application\ Support/Claude

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"
```

### 2. Create the configuration file:
```bash
# macOS
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "database-search": {
      "command": "python3",
      "args": ["mcp_database_server.py"],
      "cwd": "/Users/yuvraj/Desktop/Quilt"
    }
  }
}
EOF
```

### 3. Restart Claude Desktop

### 4. Test it!
Open Claude and ask: "Search my database for machine learning"

## 🔧 Multiple Servers Example

If you want multiple MCP servers:

```json
{
  "mcpServers": {
    "database-search": {
      "command": "python3",
      "args": ["mcp_database_server.py"],
      "cwd": "/Users/yuvraj/Desktop/Quilt"
    },
    "file-system": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
    }
  }
}
```

## ✅ Verify Setup

1. **Check file exists:**
   ```bash
   # macOS
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   dir "%APPDATA%\Claude\claude_desktop_config.json"
   ```

2. **Check file contents:**
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Test in Claude:**
   - Open new conversation
   - Ask: "What tools do you have access to?"
   - Should mention database search tools

## 🚨 Troubleshooting

### Config file not working?
1. **Check JSON syntax** (use a JSON validator)
2. **Restart Claude Desktop completely**
3. **Check file permissions**
4. **Verify Python path:** `which python3`

### Python/script issues?
1. **Test the MCP server directly:**
   ```bash
   cd /Users/yuvraj/Desktop/Quilt
   python3 mcp_database_server.py
   ```

2. **Check dependencies:**
   ```bash
   pip3 list | grep mcp
   ```

### Still not working?
1. **Check Claude's logs** (if available in app)
2. **Try absolute paths** instead of relative ones
3. **Test with a simple MCP server first**
