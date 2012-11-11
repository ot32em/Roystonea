import yaml

def load(filename):
    setting_path = "etc/%s.yaml" %(filename)
    return yaml.load(open(setting_path).read())
