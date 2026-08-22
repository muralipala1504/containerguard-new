import gradio as gr
import docker
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.core import ContainerGuardAgent

# Connect to Docker
agent = ContainerGuardAgent()

# Path to the shared history file
HISTORY_FILE = "/tmp/containerguard_history.json"

def get_container_status():
    """Get status of all containers"""
    containers = agent.get_all_containers()
    status_list = []
    for c in containers:
        status_list.append({
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else "unknown",
            "id": c.id[:12]
        })
    return status_list

def get_action_history():
    """Get action history from the shared JSON file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                return history
        except:
            return []
    return []

def refresh_dashboard():
    """Refresh the dashboard data"""
    containers = get_container_status()
    history = get_action_history()
    
    # Format container status
    status_text = "## 📦 Container Status\n\n"
    for c in containers:
        icon = "🟢" if c["status"] == "running" else ("🟡" if c["status"] == "restarted" else "🔴")
        status_text += f"{icon} **{c['name']}**: {c['status']} (Image: {c['image']})\n"
    
    # Format action history
    history_text = "## 📜 Action History\n\n"
    if history:
        # Show last 10 actions, most recent first
        for action in history[-10:][::-1]:
            ts = action.get('timestamp', 'N/A')
            act = action.get('action', 'N/A')
            container = action.get('container', 'N/A')
            status = action.get('status', 'N/A')
            history_text += f"**{ts}**: {act} {container} - {status}\n"
    else:
        history_text += "No actions recorded yet."
    
    return status_text, history_text

def restart_container(container_name):
    """Manual restart of a container"""
    container_name = container_name.strip()
    try:
        container = agent.client.containers.get(container_name)
        container.restart()
        return f"✅ Restarted container: {container_name}"
    except Exception as e:
        return f"❌ Failed to restart {container_name}: {e}"

def stop_container(container_name):
    """Manual stop of a container"""
    container_name = container_name.strip()
    try:
        container = agent.client.containers.get(container_name)
        container.stop()
        return f"✅ Stopped container: {container_name}"
    except Exception as e:
        return f"❌ Failed to stop {container_name}: {e}"

# Build Gradio interface
with gr.Blocks(title="ContainerGuard Dashboard", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔐 ContainerGuard Dashboard")
    gr.Markdown("### Autonomous Docker Agent - Monitoring & Auto-Healing")
    
    with gr.Row():
        with gr.Column(scale=2):
            refresh_btn = gr.Button("🔄 Refresh Status")
            status_output = gr.Markdown("Loading...")
            history_output = gr.Markdown("Loading...")
        
        with gr.Column(scale=1):
            gr.Markdown("### 🛠️ Manual Controls")
            container_name = gr.Textbox(label="Container Name", placeholder="e.g., test-nginx")
            with gr.Row():
                restart_btn = gr.Button("🔄 Restart")
                stop_btn = gr.Button("⏹️ Stop")
            action_result = gr.Textbox(label="Action Result", interactive=False)
    
    # Refresh button
    refresh_btn.click(
        refresh_dashboard,
        outputs=[status_output, history_output]
    )
    
    # Manual controls
    restart_btn.click(
        restart_container,
        inputs=[container_name],
        outputs=[action_result]
    )
    stop_btn.click(
        stop_container,
        inputs=[container_name],
        outputs=[action_result]
    )
    
    # Auto-refresh on load
    demo.load(refresh_dashboard, outputs=[status_output, history_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
