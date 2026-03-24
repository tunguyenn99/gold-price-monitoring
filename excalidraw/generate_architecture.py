import json
import base64
import urllib.request
import os

def fetch_base64_logo(url):
    if not url: return None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read()
            b64 = base64.b64encode(data).decode('utf-8')
            mime = "image/svg+xml" if url.endswith(".svg") else "image/png"
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}")
        return None

def main():
    nodes = [
        # The surrounding wrapper
        {
            "id": "b8", "x": 40, "y": 40, "text": "GitHub Actions (Orchestration Layer)", 
            "color": "#e67700", "bg": "#fff3bf", "dashed": True, 
            "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg",
            "is_container": True
        },
        # Row 1 (Left to Right)
        {"id": "b1", "x": 100, "y": 150, "text": "24h.com.vn", "color": "#1864ab", "bg": "#d0ebff", "logo": "https://icdn.24h.com.vn/images/2023/logo-24h-new.svg", "phase": "Source"},
        {"id": "b2", "x": 440, "y": 150, "text": "Python Scraper", "color": "#2b8a3e", "bg": "#d3f9d8", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg", "phase": "Scrape"},
        {"id": "b3", "x": 780, "y": 150, "text": "MongoDB Atlas", "color": "#087f5b", "bg": "#c3fae8", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mongodb/mongodb-original.svg", "phase": "Dump"},
        {"id": "b4", "x": 1120, "y": 150, "text": "dlt (Ingest)", "color": "#5f3dc4", "bg": "#e5dbff", "logo": "https://raw.githubusercontent.com/dlt-hub/dlt/devel/docs/website/static/img/dlt-logo.svg", "phase": "Extract"},
        
        # Row 2 (Right to Left)
        {"id": "b5", "x": 1120, "y": 350, "text": "Supabase\n(Postgres)", "color": "#0b7285", "bg": "#c5f6fa", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-original.svg", "phase": "Load"},
        {"id": "b6", "x": 780, "y": 350, "text": "dbt (Transform)", "color": "#e8590c", "bg": "#ffe8cc", "logo": "https://vectorseek.com/wp-content/uploads/2023/09/Dbt-Logo-Vector.svg-.png", "phase": "Transform"},
        {"id": "b7", "x": 440, "y": 350, "text": "Python\nAnalytics & Charts", "color": "#2b8a3e", "bg": "#d3f9d8", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg", "phase": "Usage"},
    ]

    elements = []
    files = {}

    for i, node in enumerate(nodes):
        nid = node["id"]
        x, y = node["x"], node["y"]
        color, bg = node["color"], node["bg"]
        text = node["text"]
        dashed = node.get("dashed", False)
        logo_url = node["logo"]
        phase = node.get("phase")
        is_container = node.get("is_container", False)

        if is_container:
            box_w = 1400  # width of container
            box_h = 450   # height of container
        else:
            box_w = 260
            box_h = 80

            # Draw Phase Header text if exists
            if phase:
                elements.append({
                    "type": "text", "id": nid + "_phase", "x": x, "y": y - 40,
                    "width": box_w, "height": 30, "strokeColor": "#868e96",
                    "backgroundColor": "transparent", "fillStyle": "hachure", "strokeWidth": 1,
                    "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [],
                    "strokeSharpness": "sharp", "seed": 1, "version": 1, "versionNonce": 1,
                    "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
                    "text": phase.upper(), "fontSize": 18, "fontFamily": 1, "textAlign": "center",
                    "verticalAlign": "middle", "baseline": 20
                })

        # Background Box
        elements.append({
            "type": "rectangle", "id": nid, "x": x, "y": y, "width": box_w, "height": box_h,
            "strokeColor": color, "backgroundColor": "transparent" if is_container else bg, "fillStyle": "solid",
            "strokeWidth": 3 if is_container else 2, "strokeStyle": "dashed" if dashed else "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "strokeSharpness": "round",
            "seed": 1, "version": 1, "versionNonce": 1, "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None
        })

        # Fetch and add Logo
        text_x = (x + 10) if not is_container else (x + 20)
        text_y = (y + 10 if '\n' in text else y + 25) if not is_container else (y + 25)
        
        if logo_url:
            data_url = fetch_base64_logo(logo_url)
            if data_url:
                file_id = f"logo_file_{i}"
                files[file_id] = {
                    "mimeType": "image/svg+xml" if data_url.startswith("data:image/svg") else "image/png",
                    "id": file_id,
                    "dataURL": data_url,
                    "created": 1, "lastRetrieved": 1
                }
                
                img_x = (x + 15) if not is_container else (x + 20)
                img_y = (y + 20) if not is_container else (y + 20)
                
                elements.append({
                    "type": "image", "id": f"img_{nid}", "x": img_x, "y": img_y,
                    "width": 40, "height": 40, "fileId": file_id,
                    "strokeColor": "transparent", "backgroundColor": "transparent",
                    "fillStyle": "hachure", "strokeWidth": 1, "strokeStyle": "solid",
                    "roughness": 1, "opacity": 100, "groupIds": [], "strokeSharpness": "sharp",
                    "seed": 1, "version": 1, "versionNonce": 1, "isDeleted": False,
                    "boundElements": [], "updated": 1, "link": None, "status": "saved"
                })
                text_x = img_x + 50

        # Text
        text_w = box_w - (text_x - x) - 10
        elements.append({
            "type": "text", "id": nid + "_text", "x": text_x, "y": text_y,
            "width": text_w, "height": 40, "strokeColor": "#000000",
            "backgroundColor": "transparent", "fillStyle": "hachure", "strokeWidth": 1,
            "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [],
            "strokeSharpness": "sharp", "seed": 1, "version": 1, "versionNonce": 1,
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "text": text, "fontSize": 24 if is_container else 18, "fontFamily": 1, "textAlign": "left",
            "verticalAlign": "middle", "baseline": 22
        })

    def create_arrow(aid, x, y, dx, dy, s_id, e_id, text=None, dashed=False):
        out = [{
            "type": "arrow", "id": aid, "x": x, "y": y, "width": abs(dx), "height": abs(dy),
            "strokeColor": "#000000", "backgroundColor": "transparent", "fillStyle": "hachure",
            "strokeWidth": 2, "strokeStyle": "dashed" if dashed else "solid", "roughness": 1, "opacity": 100,
            "groupIds": [], "strokeSharpness": "round", "seed": 1, "version": 1,
            "versionNonce": 1, "isDeleted": False, "boundElements": [], "updated": 1,
            "link": None, "points": [[0, 0], [dx, dy]], "lastCommittedPoint": None,
            "startBinding": {"elementId": s_id, "focus": 0, "gap": 5},
            "endBinding": {"elementId": e_id, "focus": 0, "gap": 5},
            "startArrowhead": None, "endArrowhead": "arrow"
        }]
        if text:
            # Adjust text position based on arrow direction
            text_x = x + dx/2 - 40
            text_y = y + dy/2 - 15
            
            out.append({
                "type": "text", "id": aid + "_text", "x": text_x, "y": text_y,
                "width": 80, "height": 20, "strokeColor": "#000000", "backgroundColor": "transparent",
                "fillStyle": "hachure", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "strokeSharpness": "sharp",
                "seed": 1, "version": 1, "versionNonce": 1, "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "text": text,
                "fontSize": 14, "fontFamily": 1, "textAlign": "center", "verticalAlign": "top",
                "baseline": 14
            })
        return out

    # Edges (U-shape Data Flow)
    elements += create_arrow("a1", 360, 190, 80, 0, "b1", "b2", "Scrape")
    elements += create_arrow("a2", 700, 190, 80, 0, "b2", "b3", "Save")
    elements += create_arrow("a3", 1040, 190, 80, 0, "b3", "b4", "Read")
    
    # Down arrow connecting row 1 to row 2
    elements += create_arrow("a4", 1250, 230, 0, 120, "b4", "b5", "Write")
    
    # Right to Left arrows in row 2
    elements += create_arrow("a5", 1120, 390, -80, 0, "b5", "b6", "Views")
    elements += create_arrow("a6", 780, 390, -80, 0, "b6", "b7", "Query")
    

    doc = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": files
    }

    # Save to the new excalidraw folder and original requested paths
    output_path_new = "excalidraw/project_architecture_with_logos.excalidraw"
    os.makedirs("excalidraw", exist_ok=True)
    with open(output_path_new, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    
    # Ensure it's inside images folder too per original request
    output_path_images = "images/project_architecture.excalidraw"
    with open(output_path_images, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)

    print(f"Generated {output_path_new} and {output_path_images}")

if __name__ == "__main__":
    main()
