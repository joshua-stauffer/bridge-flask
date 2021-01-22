def node_to_json(data, link_1_strength=0.7, link_2_strength=0.1):
    """
    transforms sqlalchemy Node object into json
    params
        data: Node instance
        link_1_strength: float
        link_2_strength: float
    returns
        dict
    """

    result = init_Node_dict(data.title, link_1_strength)
    result['title'] = data.title
    result['example'] = data.example
    result['definition'] = data.definition
    result['order'] = data.order
    
    for s in data.synonyms:
        result['links'].append(add_link('synonym', s, link_2_strength))
        result['nodes'].append(add_node(s, 1, s, 2))
    for a in data.antonyms:
        result['links'].append(add_link('antonym', a, link_2_strength))
        result['nodes'].append(add_node(a, 2, a, 2))

    return result
    

def init_Node_dict(title, link_1_strength):
    d = dict()
    d['nodes'] = []
    d['links'] = []

    d['links'].append(add_link('root', 'synonym', link_1_strength))
    d['links'].append(add_link('root', 'antonym', link_1_strength))
    d['nodes'].append(add_node('root', 0, title, 0))
    d['nodes'].append(add_node('synonym', 1, '', 1))
    d['nodes'].append(add_node('antonym', 2, '', 1))

    return d


def add_node(id, group, label, level):
    return {'id': id, 'group': group, 'label': label, 'level': level}

def add_link(target, source, strength):
    return {'target': target, 'source': source, 'strength': strength}