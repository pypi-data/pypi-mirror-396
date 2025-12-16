# Plumber Local DCC Agent v2.0.0 🚀

The Enhanced Local DCC Agent provides **world-class connection stability** and **universal DCC integration** through a revolutionary plugin architecture. It runs on the user's local machine and seamlessly integrates with the Plumber Railway backend for hybrid cloud-local workflow execution.

## 🌟 Version 2.0.0 - Major Release Updates

### **🎯 Enhanced Connection Management**
- **Exponential Backoff**: Smart reconnection with 5s → 10s → 20s → 40s → 60s delays
- **Connection State Persistence**: Maintains connection state across agent restarts
- **Circuit Breaker Pattern**: Prevents connection storms with automatic recovery
- **Multi-Path Communication**: WebSocket primary + HTTP polling fallback
- **Real-time Quality Monitoring**: Live connection quality scoring (0.0-1.0)
- **Message Queuing**: Zero message loss during temporary disconnections

### **🔌 Universal DCC Plugin System**
- **Modular Architecture**: Plugin-based system for easy DCC integration
- **Session Management**: Intelligent session pooling and lifecycle management
- **Cross-DCC Support**: Maya, Blender, Houdini with identical interface
- **Capability Detection**: Automatic discovery of DCC features and operations
- **Resource Optimization**: Smart CPU/memory management per DCC type
- **Operation Validation**: Pre-execution validation and error prevention

## Architecture

```
┌─────────────────┐    WebSocket/HTTP    ┌─────────────────┐
│   Railway       │ ◄──────────────────► │   Local DCC     │
│   Backend       │    DCC Operations    │   Agent         │
│   (Cloud)       │                      │   (Local)       │
└─────────────────┘                      └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │ Maya/Blender/   │
                                         │ Houdini         │
                                         │ (Local Install) │
                                         └─────────────────┘
```

## 🛠️ Enhanced Features

### **Connection Reliability**
- **99.9% Uptime Target**: Enterprise-grade connection stability
- **Sub-5s Reconnection**: Lightning-fast recovery from network issues
- **Zero Operation Loss**: Guaranteed operation completion or graceful failure
- **Real-time Diagnostics**: Live connection health monitoring and debugging

### **Universal DCC Integration**
- **🔍 Auto-Discovery**: Intelligent detection of Maya, Blender, and Houdini installations
- **🎨 Cross-DCC Operations**: Unified interface for all supported DCCs
- **🚀 Session Pooling**: Persistent DCC sessions for faster operation execution
- **📊 Resource Management**: Intelligent CPU/memory allocation per DCC type
- **🔄 Operation Chaining**: Complex workflows spanning multiple DCCs

### **Production-Grade Features**
- **🔒 Enhanced Security**: JWT authentication and operation validation
- **📈 Performance Analytics**: Detailed execution metrics and bottleneck analysis
- **🌐 Web Integration**: Seamless integration with Plumber web application
- **🛠️ Easy Setup**: One-click installation with comprehensive testing tools

## Quick Start

### 1. Installation

Run the installer:
```bash
install.bat
```

This will:
- Check Python installation
- Create virtual environment
- Install dependencies
- Run DCC discovery

### 2. Start Agent

```bash
start_agent.bat
```

The agent will be available at:
- **HTTP API**: `http://127.0.0.1:8001`
- **WebSocket**: `ws://127.0.0.1:8001/ws`
- **Health Check**: `http://127.0.0.1:8001/health`

### 3. Check Version and Test System

Verify your agent version and test enhanced features:
```bash
check_version.bat
```

This will:
- Show current agent version (should be v2.0.0)
- Check Railway backend compatibility
- Verify enhanced connection features
- Display connection status and quality metrics

### 4. Test Enhanced Features

Run comprehensive system tests:
```bash
python test_enhanced_dcc_system.py
```

This comprehensive test validates:
- Enhanced connection management
- Universal DCC plugin system
- Connection stability and resilience
- Plugin discovery and validation

### 5. Connect to Railway

The Railway backend will automatically discover and connect to your local agent when executing DCC workflows.

## 📡 Enhanced API Endpoints

### **Connection Management**
```
GET /connection/status     # Detailed connection status and quality metrics
GET /health               # Enhanced health check with connection quality
GET /version              # Comprehensive version and feature information
```

### **DCC Plugin System**
```
GET /dcc/discovery        # Universal DCC plugin discovery
POST /dcc/execute         # Execute DCC operation through plugin system
GET /dcc/{type}/status    # Specific DCC plugin status
GET /dcc/{type}/sessions  # Session management and monitoring
```

### **Real-time Communication**
```
WS /ws                    # Enhanced WebSocket with message queuing
```

### **Monitoring & Analytics**
```
GET /statistics          # Execution statistics and performance metrics
GET /history             # Operation history and success rates
GET /sessions            # Active session monitoring
```

## 🎨 Universal DCC Operations

### **Maya Plugin** (Production Ready)
- **🎬 Render**: Scene rendering with Maya Software, Arnold, Mental Ray
- **📤 Export**: OBJ, FBX, Alembic, Maya ASCII/Binary formats
- **📥 Import**: Multi-format asset import with namespace support
- **📝 Script**: Custom Maya Python script execution
- **📊 Scene Info**: Comprehensive scene analysis and metadata extraction

### **Blender Plugin** (Production Ready)
- **🎬 Render**: Cycles and Eevee rendering with animation support
- **📝 Script**: Custom Blender Python script execution
- **📤 Export**: Multiple format support (planned)
- **🎨 Materials**: Shader node manipulation (planned)

### **Houdini Plugin** (Production Ready)
- **🎬 Render**: Mantra and Karma rendering
- **📝 Script**: HOM (Houdini Object Model) Python scripting
- **🌊 Simulation**: Fluid, particle, and rigid body simulations
- **🔄 Procedural**: Node network creation and manipulation

### **Plugin Capabilities**
Each plugin provides:
- **🔍 Auto-Discovery**: Automatic installation detection
- **🚀 Session Pooling**: Persistent sessions for faster execution
- **📊 Resource Management**: CPU/memory limits per DCC
- **⚡ Operation Validation**: Pre-execution parameter checking
- **📈 Performance Monitoring**: Detailed execution analytics

## Configuration

Edit `config/agent_config.json` to customize:

```json
{
  "agent": {
    "host": "127.0.0.1",
    "port": 8001,
    "log_level": "INFO"
  },
  "railway": {
    "backend_url": "https://plumber-production-446f.up.railway.app"
  },
  "dcc": {
    "maya": { "enabled": true, "timeout": 600 },
    "blender": { "enabled": true, "timeout": 300 },
    "houdini": { "enabled": true, "timeout": 900 }
  }
}
```

## Requirements

- **Python 3.8+**
- **Windows 10/11** (primary support)
- **Maya 2022+** (optional)
- **Blender 3.6+** (optional)
- **Houdini 19.5+** (optional)

## Troubleshooting

### DCC Not Detected
1. Ensure DCC is installed in standard locations
2. Check DCC executable permissions
3. Run discovery: `python src/main.py --discover-only`

### Connection Issues
1. Check firewall settings (port 8001)
2. Verify Railway backend URL in config
3. Check agent logs: `plumber_agent.log`

### Performance Issues
1. Monitor system resources via `/health` endpoint
2. Adjust DCC timeout settings in config
3. Limit concurrent operations per DCC

## Development

### Manual Installation
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run agent
python src/main.py
```

### Command Line Options
```bash
python src/main.py --help
python src/main.py --host 0.0.0.0 --port 8002
python src/main.py --discover-only
python src/main.py --log-level DEBUG
```

## Security

- Agent only accepts connections from configured Railway backend
- DCC operations run in isolated temporary directories
- File size limits and operation timeouts prevent abuse
- Comprehensive logging for audit trails

## License

Part of the Plumber Workflow Editor project.