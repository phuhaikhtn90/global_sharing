import requests
import json

TOKEN = 'YOUR_FIGMA_TOKEN'
headers = {
    "X-Figma-Token": TOKEN
}

file_key = "lciV4feePMcVoQA0Bywfzz"
node_id = "2-96"


url = f"https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}"
resp = requests.get(url, headers=headers)

data = resp.json()
with open('extract_figma_component_tokens.json', 'w') as f:
    json.dump(data, f, indent=2)

node_id_json = "2:96"
# Chỉ lấy phần document từ node cần thiết
raw_node = data["nodes"][node_id_json]["document"]

# Các trường cần giữ lại (có thể mở rộng tùy use case)
KEEP_FIELDS = {
    "id", "name", "type", "children", "fills", "strokes", "strokeWeight", "strokeAlign",
    "absoluteBoundingBox", "constraints", "characters", "lineIndentations", "style",
    "componentId", "overrides", "clipsContent", "effects", "interactions", "backgroundColor"
}

def extract_padding(parent_box, child_box):
    px, py, pw, ph = parent_box["x"], parent_box["y"], parent_box["width"], parent_box["height"]
    cx, cy, cw, ch = child_box["x"], child_box["y"], child_box["width"], child_box["height"]

    return {
        "left": round(cx - px, 2),
        "top": round(cy - py, 2),
        "right": round((px + pw) - (cx + cw), 2),
        "bottom": round((py + ph) - (cy + ch), 2)
    }

def is_same_row(box1, box2, tolerance=2):
    return abs(box1["y"] - box2["y"]) < tolerance

def is_same_column(box1, box2, tolerance=2):
    return abs(box1["x"] - box2["x"]) < tolerance

def calc_distance(box1, box2, relation):
    if relation == "sameRow":
        return abs(box1["x"] - box2["x"])
    elif relation == "sameColumn":
        return abs(box1["y"] - box2["y"])
    return None

def process_siblings(children):
    for i, node_i in enumerate(children):
        box_i = node_i.get("absoluteBoundingBox")
        if not box_i:
            continue
        siblings_info = []
        for j, node_j in enumerate(children):
            if i == j:
                continue
            box_j = node_j.get("absoluteBoundingBox")
            if not box_j:
                continue

            if is_same_row(box_i, box_j):
                siblings_info.append({
                    "targetId": node_j.get("id"),
                    "relation": "sameRow",
                    "distance": round(calc_distance(box_i, box_j, "sameRow"), 2)
                })
            elif is_same_column(box_i, box_j):
                siblings_info.append({
                    "targetId": node_j.get("id"),
                    "relation": "sameColumn",
                    "distance": round(calc_distance(box_i, box_j, "sameColumn"), 2)
                })
        if siblings_info:
            node_i["siblingsLayout"] = siblings_info

def filter_node(node, parent_box=None):
    new_node = {}
    current_box = node.get("absoluteBoundingBox")

    for key, value in node.items():
        if key in KEEP_FIELDS:
            if key == "children":
                new_children = [filter_node(child, current_box) for child in value]
                process_siblings(new_children)
                new_node[key] = new_children
            else:
                new_node[key] = value

    if parent_box and current_box:
        new_node["padding"] = extract_padding(parent_box, current_box)

    return new_node

# Xử lý
raw_node = data["nodes"][node_id_json]["document"]
clean_node = filter_node(raw_node)

# Ghi file
with open('clean_figma_output.json', 'w') as f:
    json.dump(clean_node, f, indent=2)