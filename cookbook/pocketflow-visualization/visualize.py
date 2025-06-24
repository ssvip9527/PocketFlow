# %%

import json
import os
import http.server
import socketserver
import threading
import webbrowser
import time
import socket
import importlib
import sys
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from pocketflow import Flow

from async_flow import order_pipeline


def build_mermaid(start):
    ids, visited, lines = {}, set(), ["graph LR"]
    ctr = 1

    def get_id(n):
        nonlocal ctr
        return (
            ids[n] if n in ids else (ids.setdefault(n, f"N{ctr}"), (ctr := ctr + 1))[0]
        )

    def link(a, b, action=None):
        if action:
            lines.append(f"    {a} -->|{action}| {b}")
        else:
            lines.append(f"    {a} --> {b}")

    def walk(node, parent=None, action=None):
        if node in visited:
            return parent and link(parent, get_id(node), action)
        visited.add(node)
        if isinstance(node, Flow):
            node.start_node and parent and link(parent, get_id(node.start_node), action)
            lines.append(
                f"\n    subgraph sub_flow_{get_id(node)}[{type(node).__name__}]"
            )
            node.start_node and walk(node.start_node)
            for act, nxt in node.successors.items():
                node.start_node and walk(nxt, get_id(node.start_node), act) or (
                    parent and link(parent, get_id(nxt), action)
                ) or walk(nxt, None, act)
            lines.append("    end\n")
        else:
            lines.append(f"    {(nid := get_id(node))}['{type(node).__name__}']")
            parent and link(parent, nid, action)
            [walk(nxt, nid, act) for act, nxt in node.successors.items()]

    walk(start)
    return "\n".join(lines)


def flow_to_json(start):
    """将流程转换为适合 D3.js 可视化的 JSON 格式。

    此函数遍历流程图并构建一个包含以下内容的结构：
    - nodes: 所有非流程节点及其组归属
    - links: 同一组内节点之间的连接
    - group_links: 不同组之间的连接（用于流程间连接）
    - flows: 用于组标签的流程信息

    返回：
        dict: 包含 'nodes' 和 'links' 数组的 JSON 序列化字典。
    """
    nodes = []
    links = []
    group_links = []  # 用于组之间的连接（流程到流程）
    ids = {}
    node_types = {}
    flow_nodes = {}  # 跟踪流程节点
    ctr = 1

    def get_id(n):
        nonlocal ctr
        if n not in ids:
            ids[n] = ctr
            node_types[ctr] = type(n).__name__
            if isinstance(n, Flow):
                flow_nodes[ctr] = n  # 存储流程引用
            ctr += 1
        return ids[n]

    def walk(node, parent=None, group=None, parent_group=None, action=None):
        """递归遍历流程图以构建可视化数据。

        参数：
            node: 当前正在处理的节点
            parent: 连接到此节点的父节点 ID
            group: 此节点所属的组（流程）ID
            parent_group: 父节点的组 ID
            action: 从父节点到此节点的边上的动作标签
        """
        node_id = get_id(node)

        # 如果节点不在节点列表中且不是流程，则添加节点
        if not any(n["id"] == node_id for n in nodes) and not isinstance(node, Flow):
            node_data = {
                "id": node_id,
                "name": node_types[node_id],
                "group": group or 0,  # 默认组
            }
            nodes.append(node_data)

        # 如果存在父节点，则添加来自父节点的链接
        if parent and not isinstance(node, Flow):
            links.append(
                {"source": parent, "target": node_id, "action": action or "default"}
            )

        # 处理不同类型的节点
        if isinstance(node, Flow):
            # 这是一个流程节点 - 它成为一个组容器
            flow_group = node_id  # 使用流程的 ID 作为包含节点的组

            # 如果此流程有父组，则添加组到组的链接
            # 这会创建嵌套流程之间的连接
            if parent_group is not None and parent_group != flow_group:
                # 检查此链接是否已存在
                if not any(
                    l["source"] == parent_group and l["target"] == flow_group
                    for l in group_links
                ):
                    group_links.append(
                        {
                            "source": parent_group,
                            "target": flow_group,
                            "action": action or "default",
                        }
                    )

            if node.start_node:
                # 处理此流程的起始节点
                walk(node.start_node, parent, flow_group, parent_group, action)

                # 处理流程起始节点的后继节点
                for next_action, nxt in node.successors.items():
                    walk(
                        nxt,
                        get_id(node.start_node),
                        flow_group,
                        parent_group,
                        next_action,
                    )
        else:
            # 处理常规节点的后继节点
            for next_action, nxt in node.successors.items():
                if isinstance(nxt, Flow):
                    # 此节点连接到流程 - 跟踪组关系
                    flow_group_id = get_id(nxt)
                    walk(nxt, node_id, None, group, next_action)
                else:
                    # 常规节点到节点的连接
                    walk(nxt, node_id, group, parent_group, next_action)

    # 开始遍历
    walk(start)

    # 后处理：根据不同组之间的节点连接生成组链接
    # 这确保当不同组中的节点连接时，我们显示组到组的链接
    # 而不是直接的节点到节点的链接
    node_groups = {n["id"]: n["group"] for n in nodes}
    filtered_links = []

    for link in links:
        source_id = link["source"]
        target_id = link["target"]
        source_group = node_groups.get(source_id, 0)
        target_group = node_groups.get(target_id, 0)

        # 如果源和目标在不同的组中且两个组都有效
        if source_group != target_group and source_group > 0 and target_group > 0:
            # 如果组链接中不存在，则添加
            # 这会创建连接组框的虚线
            if not any(
                gl["source"] == source_group and gl["target"] == target_group
                for gl in group_links
            ):
                group_links.append(
                    {
                        "source": source_group,
                        "target": target_group,
                        "action": link["action"],
                    }
                )
            # 跳过将此链接添加到 filtered_links - 我们不希望跨组的直接节点连接
        else:
            # 保留同一组内的链接
            filtered_links.append(link)

    return {
        "nodes": nodes,
        "links": filtered_links,  # 使用过滤后的链接而不是所有链接
        "group_links": group_links,
        "flows": {str(k): v.__class__.__name__ for k, v in flow_nodes.items()},
    }


def create_d3_visualization(
    json_data,
    output_dir="./viz",
    filename="flow_viz",
    html_title="PocketFlow Visualization",
):
    """Create a D3.js visualization from JSON data.

    Args:
        json_data: The JSON data for the visualization
        output_dir: Directory to save the files
        filename: Base filename (without extension)
        html_title: Title for the HTML page

    Returns:
        str: Path to the HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON data to file
    json_path = os.path.join(output_dir, f"{filename}.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)

    # Create HTML file with D3.js visualization
    html_content = r"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TITLE_PLACEHOLDER</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        svg {
            width: 100vw;
            height: 100vh;
        }
        .links path {
            fill: none;
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }
        .group-links path {
            fill: none;
            stroke: #333;
            stroke-opacity: 0.8;
            stroke-width: 2px;
            stroke-dasharray: 5,5;
        }
        .nodes circle {
            stroke: #fff;
            stroke-width: 1.5px;
        }
        .node-labels {
            font-size: 12px;
            pointer-events: none;
        }
        .link-labels {
            font-size: 10px;
            fill: #666;
            pointer-events: none;
        }
        .group-link-labels {
            font-size: 11px;
            font-weight: bold;
            fill: #333;
            pointer-events: none;
        }
        .group-container {
            stroke: #333;
            stroke-width: 1.5px;
            stroke-dasharray: 5,5;
            fill: rgba(200, 200, 200, 0.1);
            rx: 10;
            ry: 10;
        }
        .group-label {
            font-size: 14px;
            font-weight: bold;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <svg id="graph"></svg>
    <script>
        // Load data from file
        d3.json("FILENAME_PLACEHOLDER.json").then(data => {
            const svg = d3.select("#graph");
            const width = window.innerWidth;
            const height = window.innerHeight;
            
            // Define arrow markers for links
            svg.append("defs").append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 25) // Position the arrow away from the target node
                .attr("refY", 0)
                .attr("orient", "auto")
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("xoverflow", "visible")
                .append("path")
                .attr("d", "M 0,-5 L 10,0 L 0,5")
                .attr("fill", "#999");
                
            // Define thicker arrow markers for group links
            svg.append("defs").append("marker")
                .attr("id", "group-arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 3) // Position at the boundary of the group
                .attr("refY", 0)
                .attr("orient", "auto")
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("xoverflow", "visible")
                .append("path")
                .attr("d", "M 0,-5 L 10,0 L 0,5")
                .attr("fill", "#333");
            
            // Color scale for node groups
            const color = d3.scaleOrdinal(d3.schemeCategory10);
            
            // Process the data to identify groups
            const groups = {};
            data.nodes.forEach(node => {
                if (node.group > 0) {
                    if (!groups[node.group]) {
                        // Use the flow name instead of generic "Group X"
                        const flowName = data.flows && data.flows[node.group] ? data.flows[node.group] : `Flow ${node.group}`;
                        groups[node.group] = {
                            id: node.group,
                            name: flowName,
                            nodes: [],
                            x: 0,
                            y: 0,
                            width: 0,
                            height: 0
                        };
                    }
                    groups[node.group].nodes.push(node);
                }
            });
            
            // Create a force simulation
            const simulation = d3.forceSimulation(data.nodes)
                // Controls the distance between connected nodes
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                // Controls how nodes repel each other - lower values bring nodes closer
                .force("charge", d3.forceManyBody().strength(-30))
                // Centers the entire graph in the SVG
                .force("center", d3.forceCenter(width / 2, height / 2))
                // Prevents nodes from overlapping - acts like a minimum distance
                .force("collide", d3.forceCollide().radius(50));
            
            // Group forces - create a force to keep nodes in the same group closer together
            // This creates the effect of nodes clustering within their group boxes
            const groupForce = alpha => {
                for (let i = 0; i < data.nodes.length; i++) {
                    const node = data.nodes[i];
                    if (node.group > 0) {
                        const group = groups[node.group];
                        if (group && group.nodes.length > 1) {
                            // Calculate center of group
                            let centerX = 0, centerY = 0;
                            group.nodes.forEach(n => {
                                centerX += n.x || 0;
                                centerY += n.y || 0;
                            });
                            centerX /= group.nodes.length;
                            centerY /= group.nodes.length;
                            
                            // Move nodes toward center
                            const k = alpha * 0.3; // Increased from 0.1 to 0.3
                            node.vx += (centerX - node.x) * k;
                            node.vy += (centerY - node.y) * k;
                        }
                    }
                }
            };
            
            // Additional force to position groups in a more organized layout (like in the image)
            // This arranges the groups horizontally/vertically based on their connections
            const groupLayoutForce = alpha => {
                // Get group centers
                const groupCenters = Object.values(groups).map(g => {
                    return { id: g.id, cx: 0, cy: 0 };
                });
                
                // Calculate current center positions
                Object.values(groups).forEach(g => {
                    if (g.nodes.length > 0) {
                        let cx = 0, cy = 0;
                        g.nodes.forEach(n => {
                            cx += n.x || 0;
                            cy += n.y || 0;
                        });
                        
                        const groupCenter = groupCenters.find(gc => gc.id === g.id);
                        if (groupCenter) {
                            groupCenter.cx = cx / g.nodes.length;
                            groupCenter.cy = cy / g.nodes.length;
                        }
                    }
                });
                
                // Apply forces to position groups
                const k = alpha * 0.05;
                
                // Try to position groups in a more structured way
                // Adjust these values to change the overall layout
                for (let i = 0; i < data.group_links.length; i++) {
                    const link = data.group_links[i];
                    const source = groupCenters.find(g => g.id === link.source);
                    const target = groupCenters.find(g => g.id === link.target);
                    
                    if (source && target) {
                        // Add a horizontal force to align groups
                        const desiredDx = 300; // Desired horizontal distance between linked groups
                        const dx = target.cx - source.cx;
                        const diff = desiredDx - Math.abs(dx);
                        
                        // Apply forces to group nodes
                        groups[source.id].nodes.forEach(n => {
                            if (dx > 0) {
                                n.vx -= diff * k;
                            } else {
                                n.vx += diff * k;
                            }
                        });
                        
                        groups[target.id].nodes.forEach(n => {
                            if (dx > 0) {
                                n.vx += diff * k;
                            } else {
                                n.vx -= diff * k;
                            }
                        });
                    }
                }
            };
            
            simulation.force("group", groupForce);
            simulation.force("groupLayout", groupLayoutForce);
            
            // Create links with arrow paths instead of lines
            const link = svg.append("g")
                .attr("class", "links")
                .selectAll("path")
                .data(data.links)
                .enter()
                .append("path")
                .attr("stroke-width", 2)
                .attr("stroke", "#999")
                .attr("marker-end", "url(#arrowhead)");  // Add the arrowhead marker
            
            // Create group containers (drawn before nodes)
            const groupContainers = svg.append("g")
                .attr("class", "groups")
                .selectAll("rect")
                .data(Object.values(groups))
                .enter()
                .append("rect")
                .attr("class", "group-container")
                .attr("fill", d => d3.color(color(d.id)).copy({opacity: 0.2}));
            
            // Create group links between flows
            const groupLink = svg.append("g")
                .attr("class", "group-links")
                .selectAll("path")
                .data(data.group_links || [])
                .enter()
                .append("path")
                .attr("stroke-width", 2)
                .attr("stroke", "#333")
                .attr("marker-end", "url(#group-arrowhead)");
                
            // Create group link labels
            const groupLinkLabel = svg.append("g")
                .attr("class", "group-link-labels")
                .selectAll("text")
                .data(data.group_links || [])
                .enter()
                .append("text")
                .text(d => d.action)
                .attr("font-size", "11px")
                .attr("font-weight", "bold")
                .attr("fill", "#333");
            
            // Create group labels
            const groupLabels = svg.append("g")
                .attr("class", "group-labels")
                .selectAll("text")
                .data(Object.values(groups))
                .enter()
                .append("text")
                .attr("class", "group-label")
                .text(d => d.name)  // Now using the proper flow name
                .attr("fill", d => d3.color(color(d.id)).darker());
            
            // Create link labels
            const linkLabel = svg.append("g")
                .attr("class", "link-labels")
                .selectAll("text")
                .data(data.links)
                .enter()
                .append("text")
                .text(d => d.action)
                .attr("font-size", "10px")
                .attr("fill", "#666");
            
            // Create nodes
            const node = svg.append("g")
                .attr("class", "nodes")
                .selectAll("circle")
                .data(data.nodes)
                .enter()
                .append("circle")
                .attr("r", 15)
                .attr("fill", d => color(d.group))
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // Create node labels
            const nodeLabel = svg.append("g")
                .attr("class", "node-labels")
                .selectAll("text")
                .data(data.nodes)
                .enter()
                .append("text")
                .text(d => d.name)
                .attr("text-anchor", "middle")
                .attr("dy", 25);
            
            // Add tooltip on hover
            node.append("title")
                .text(d => d.name);
            
            // Update positions on each tick
            simulation.on("tick", () => {
                // Update links with straight lines
                link.attr("d", d => {
                    return `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`;
                });
                
                // Update nodes
                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);
                
                // Update node labels
                nodeLabel
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
                
                // Position link labels at midpoint
                linkLabel
                    .attr("x", d => (d.source.x + d.target.x) / 2)
                    .attr("y", d => (d.source.y + d.target.y) / 2);
                
                // Update group containers
                groupContainers.each(function(d) {
                    // If there are nodes in this group
                    if (d.nodes.length > 0) {
                        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                        
                        // Find the bounding box for all nodes in the group
                        d.nodes.forEach(n => {
                            minX = Math.min(minX, n.x - 30);
                            minY = Math.min(minY, n.y - 30);
                            maxX = Math.max(maxX, n.x + 30);
                            maxY = Math.max(maxY, n.y + 40); // Extra space for labels
                        });
                        
                        // Add padding
                        const padding = 20;
                        minX -= padding;
                        minY -= padding;
                        maxX += padding;
                        maxY += padding;
                        
                        // Save group dimensions
                        d.x = minX;
                        d.y = minY;
                        d.width = maxX - minX;
                        d.height = maxY - minY;
                        d.centerX = minX + d.width / 2;
                        d.centerY = minY + d.height / 2;
                        
                        // Set position and size of the group container
                        d3.select(this)
                            .attr("x", minX)
                            .attr("y", minY)
                            .attr("width", d.width)
                            .attr("height", d.height);
                        
                        // Update group label position (top-left of group)
                        groupLabels.filter(g => g.id === d.id)
                            .attr("x", minX + 10)
                            .attr("y", minY + 20);
                    }
                });
                
                // Update group links between flows
                groupLink.attr("d", d => {
                    const sourceGroup = groups[d.source];
                    const targetGroup = groups[d.target];
                    
                    if (!sourceGroup || !targetGroup) return "";
                    
                    // Find intersection points with group boundaries
                    // This ensures links connect to the group's border rather than its center
                    
                    // Calculate centers of groups
                    const sx = sourceGroup.centerX;
                    const sy = sourceGroup.centerY;
                    const tx = targetGroup.centerX;
                    const ty = targetGroup.centerY;
                    
                    // Calculate angle between centers - used to find intersection points
                    const angle = Math.atan2(ty - sy, tx - sx);
                    
                    // Calculate intersection points with source group borders
                    // We cast a ray from center in the direction of the target
                    let sourceX, sourceY;
                    const cosA = Math.cos(angle);
                    const sinA = Math.sin(angle);
                    
                    // Check intersection with horizontal borders (top and bottom)
                    const ts_top = (sourceGroup.y - sy) / sinA;
                    const ts_bottom = (sourceGroup.y + sourceGroup.height - sy) / sinA;
                    
                    // Check intersection with vertical borders (left and right)
                    const ts_left = (sourceGroup.x - sx) / cosA;
                    const ts_right = (sourceGroup.x + sourceGroup.width - sx) / cosA;
                    
                    // Use the closest positive intersection (first hit with the boundary)
                    let t_source = Infinity;
                    if (ts_top > 0) t_source = Math.min(t_source, ts_top);
                    if (ts_bottom > 0) t_source = Math.min(t_source, ts_bottom);
                    if (ts_left > 0) t_source = Math.min(t_source, ts_left);
                    if (ts_right > 0) t_source = Math.min(t_source, ts_right);
                    
                    // Target group: Find intersection in the opposite direction
                    // We cast a ray from target center toward the source
                    let targetX, targetY;
                    const oppositeAngle = angle + Math.PI;
                    const cosOpp = Math.cos(oppositeAngle);
                    const sinOpp = Math.sin(oppositeAngle);
                    
                    // Check intersections for target group
                    const tt_top = (targetGroup.y - ty) / sinOpp;
                    const tt_bottom = (targetGroup.y + targetGroup.height - ty) / sinOpp;
                    const tt_left = (targetGroup.x - tx) / cosOpp;
                    const tt_right = (targetGroup.x + targetGroup.width - tx) / cosOpp;
                    
                    // Use the closest positive intersection
                    let t_target = Infinity;
                    if (tt_top > 0) t_target = Math.min(t_target, tt_top);
                    if (tt_bottom > 0) t_target = Math.min(t_target, tt_bottom);
                    if (tt_left > 0) t_target = Math.min(t_target, tt_left);
                    if (tt_right > 0) t_target = Math.min(t_target, tt_right);
                    
                    // Calculate actual border points using parametric equation:
                    // point = center + t * direction
                    if (t_source !== Infinity) {
                        sourceX = sx + cosA * t_source;
                        sourceY = sy + sinA * t_source;
                    } else {
                        sourceX = sx;
                        sourceY = sy;
                    }
                    
                    if (t_target !== Infinity) {
                        targetX = tx + cosOpp * t_target;
                        targetY = ty + sinOpp * t_target;
                    } else {
                        targetX = tx;
                        targetY = ty;
                    }
                    
                    // Create a straight line between the border points
                    return `M${sourceX},${sourceY} L${targetX},${targetY}`;
                });
                
                // Update group link labels
                groupLinkLabel.attr("x", d => {
                    const sourceGroup = groups[d.source];
                    const targetGroup = groups[d.target];
                    if (!sourceGroup || !targetGroup) return 0;
                    return (sourceGroup.centerX + targetGroup.centerX) / 2;
                })
                .attr("y", d => {
                    const sourceGroup = groups[d.source];
                    const targetGroup = groups[d.target];
                    if (!sourceGroup || !targetGroup) return 0;
                    return (sourceGroup.centerY + targetGroup.centerY) / 2 - 10;
                });
            });
            
            // Drag functions
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        });
    </script>
</body>
</html>
"""

    # Replace the placeholders with the actual values
    html_content = html_content.replace("FILENAME_PLACEHOLDER", filename)
    html_content = html_content.replace("TITLE_PLACEHOLDER", html_title)

    # Write HTML to file
    html_path = os.path.join(output_dir, f"{filename}.html")
    with open(html_path, "w") as f:
        f.write(html_content)

    print(f"Visualization created at {html_path}")
    return html_path


def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def start_http_server(directory, port=None):
    """Start an HTTP server in the given directory.

    Args:
        directory: Directory to serve files from
        port: Port to use (finds a free port if None)

    Returns:
        tuple: (server_thread, port)
    """
    if port is None:
        port = find_free_port()

    # Get the absolute path of the directory
    directory = str(Path(directory).absolute())

    # Change to the directory to serve files
    os.chdir(directory)

    # Create HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)

    # Start server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = (
        True  # This makes the thread exit when the main program exits
    )
    server_thread.start()

    print(f"Server started at http://localhost:{port}")
    return server_thread, port


def serve_and_open_visualization(html_path, auto_open=True):
    """Serve the HTML file and open it in a browser.

    Args:
        html_path: Path to the HTML file
        auto_open: Whether to automatically open the browser

    Returns:
        tuple: (server_thread, url)
    """
    # Get the directory and filename
    directory = os.path.dirname(os.path.abspath(html_path))
    filename = os.path.basename(html_path)

    # Start the server
    server_thread, port = start_http_server(directory)

    # Build the URL
    url = f"http://localhost:{port}/{filename}"

    # Open the URL in a browser
    if auto_open:
        print(f"Opening {url} in your browser...")
        webbrowser.open(url)
    else:
        print(f"Visualization available at {url}")

    return server_thread, url


def visualize_flow(
    flow: Flow,
    flow_name: str,
    serve: bool = True,
    auto_open: bool = True,
    output_dir: str = "./viz",
    html_title: Optional[str] = None,
) -> Union[str, Tuple[str, Any, str]]:
    """Helper function to visualize a flow with both mermaid and D3.js

    Args:
        flow: Flow object to visualize
        flow_name: Name of the flow (used for filename and display)
        serve: Whether to start a server for the visualization
        auto_open: Whether to automatically open in browser
        output_dir: Directory to save visualization files
        html_title: Custom title for the HTML page (defaults to flow_name if None)

    Returns:
        str or tuple: Path to HTML file, or (path, server_thread, url) if serve=True
    """
    print(f"\n--- {flow_name} Mermaid Diagram ---")
    print(build_mermaid(start=flow))

    print(f"\n--- {flow_name} D3.js Visualization ---")
    json_data = flow_to_json(flow)

    # Create the visualization
    output_filename = f"{flow_name.lower().replace(' ', '_')}"

    # Use flow_name as the HTML title if not specified
    if html_title is None:
        html_title = f"PocketFlow: {flow_name}"

    html_path = create_d3_visualization(
        json_data,
        output_dir=output_dir,
        filename=output_filename,
        html_title=html_title,
    )

    # Serve and open if requested
    if serve:
        server_thread, url = serve_and_open_visualization(html_path, auto_open)
        return html_path, server_thread, url

    return html_path


def load_flow_from_module(module_path: str, flow_variable: str) -> Flow:
    """Dynamically load a flow from a module.

    Args:
        module_path: Path to the module (e.g., 'my_package.my_module')
        flow_variable: Name of the flow variable in the module

    Returns:
        Flow: The loaded flow object
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, flow_variable)
    except (ImportError, AttributeError) as e:
        print(f"Error loading flow: {e}")
        sys.exit(1)


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize a PocketFlow flow")
    parser.add_argument(
        "--module", default="async_flow", help="Module containing the flow"
    )
    parser.add_argument(
        "--flow", default="order_pipeline", help="Flow variable name in the module"
    )
    parser.add_argument(
        "--name", default="Flow Visualization", help="Name for the visualization"
    )
    parser.add_argument(
        "--output-dir", default="./viz", help="Directory to save visualization files"
    )
    parser.add_argument("--no-serve", action="store_true", help="Don't start a server")
    parser.add_argument(
        "--no-open", action="store_true", help="Don't open browser automatically"
    )
    parser.add_argument("--title", help="Custom HTML title")

    args = parser.parse_args()

    # Load flow from the specified module
    flow_obj = load_flow_from_module(args.module, args.flow)

    # Visualize the flow
    visualize_flow(
        flow=flow_obj,
        flow_name=args.name,
        serve=not args.no_serve,
        auto_open=not args.no_open,
        output_dir=args.output_dir,
        html_title=args.title,
    )

    # Keep server running if serving
    if not args.no_serve:
        try:
            print("\nServer is running. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
