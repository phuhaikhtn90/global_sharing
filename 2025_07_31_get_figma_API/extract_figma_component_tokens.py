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

# Hàm lọc trường
def filter_node(node):
    new_node = {}
    for key, value in node.items():
        if key in KEEP_FIELDS:
            if key == "children":
                new_node[key] = [filter_node(child) for child in value]
            else:
                new_node[key] = value
    return new_node

# Tiến hành lọc dữ liệu
clean_node = filter_node(raw_node)

# Ghi ra file
with open('clean_figma_output.json', 'w') as f:
    json.dump(clean_node, f, indent=2)