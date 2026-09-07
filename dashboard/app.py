import sys
import os
import gradio as gr
import docker
import json
import time
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audit import log_action, get_audit_logs, export_audit_logs

# Docker connection
def get_docker_client():
    docker_host = os.getenv('DOCKER_HOST', 'unix:///var/run/docker.sock')
    return docker.DockerClient(base_url=docker_host)

def get_containers():
    try:
        client = get_docker_client()
        containers = client.containers.list(all=True)
        result = []
        for c in containers:
            result.append({
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else "unknown",
                "id": c.id[:12]
            })
        return result
    except Exception as e:
        return [{"name": "Error", "status": str(e), "image": "", "id": ""}]

def auto_heal():
    try:
        client = get_docker_client()
        containers = client.containers.list(all=True)
        actions = []
        for c in containers:
            if c.status == "exited":
                c.start()
                log_action("system", "auto-heal", c.name, "Container auto-restarted", "success")
                actions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "container": c.name,
                    "action": "restarted"
                })
        return actions
    except Exception as e:
        return [{"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "container": "error", "action": str(e)}]

def refresh():
    heal_actions = auto_heal()
    containers = get_containers()
    
    node_text = "## 🖥️ Nodes\n\n"
    node_text += "Control Plane: Ready\n"
    
    pod_text = "## 📦 Containers\n\n"
    for c in containers:
        icon = "🟢" if c["status"] == "running" else ("🟡" if c["status"] == "restarted" else "🔴")
        pod_text += f"{icon} **{c['name']}**: {c['status']} ({c['image']})\n"
    
    # Audit logs
    audit_logs = get_audit_logs(10)
    history_text = "## 📜 Recent Actions\n\n"
    if audit_logs:
        for log in audit_logs[-10:]:
            history_text += f"**{log['timestamp']}** — {log['user']} — {log['action']} {log['resource']} — {log['status']}\n"
    else:
        history_text += "No actions recorded yet."
    
    return node_text, pod_text, history_text

def restart_container(name):
    try:
        client = get_docker_client()
        container = client.containers.get(name)
        container.restart()
        log_action("user", "restart", name, "Container restarted manually", "success")
        return f"✅ Restarted {name}"
    except Exception as e:
        log_action("user", "restart", name, f"Failed: {e}", "failed")
        return f"❌ Failed: {e}"

# Build the UI
with gr.Blocks(theme=gr.themes.Soft(), title="ContainerGuard") as demo:
    gr.Markdown("# 🔐 ContainerGuard Dashboard")
    gr.Markdown("Auto-heal · Monitor · Optimize")
    
    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh")
    
    with gr.Row():
        with gr.Column(scale=1):
            nodes_output = gr.Markdown("Loading...")
        with gr.Column(scale=2):
            pods_output = gr.Markdown("Loading...")
    
    with gr.Row():
        history_output = gr.Markdown("Loading...")
    
    with gr.Row():
        container_name = gr.Textbox(label="Container Name", placeholder="e.g., test-nginx")
        restart_btn = gr.Button("🔄 Restart Container")
        restart_result = gr.Textbox(label="Result", interactive=False)
    
    refresh_btn.click(refresh, outputs=[nodes_output, pods_output, history_output])
    restart_btn.click(restart_container, inputs=[container_name], outputs=[restart_result])
    demo.load(refresh, outputs=[nodes_output, pods_output, history_output])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
