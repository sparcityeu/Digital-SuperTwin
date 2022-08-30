from flask import Flask, jsonify

app = Flask(__name__)


nodes = []
edges = []

@app.route('/api/graph/fields')
def fetch_graph_fields():
    nodes_fields = [{"field_name": "id", "type": "string"},
                    {"field_name": "title", "type": "string"}]

                        
    edges_fields = [
        {"field_name": "id", "type": "string"},
        {"field_name": "source", "type": "string"},
        {"field_name": "target", "type": "string"}
    ]
    result = {"nodes_fields": nodes_fields,
              "edges_fields": edges_fields}
    return jsonify(result)


@app.route('/api/graph/data')
def fetch_graph_data():

    global nodes
    global edges
    
    result = {"nodes": nodes, "edges": edges}
    return jsonify(result)


@app.route('/api/health')
def check_health():
    return "API is working well!"

def main(p_nodes, p_edges):

    global nodes
    global edges

    nodes = p_nodes
    edges = p_edges
    
    app.run(host='0.0.0.0', port=5001)
    

if __name__ == "__main__":

    main()
