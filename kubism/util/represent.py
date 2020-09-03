import io
import yaml

def cascade(data):
    # We're Cheating. We're just going to use the YAML flow and make modifications
    yaml_flow = yaml.dump(data, default_flow_style=False)
    return yaml_to_kubism(yaml_flow)


def yaml_to_kubism(str):
    str = str.replace(':\n', '/\n')
    str = str.replace(': []', '')
    return str