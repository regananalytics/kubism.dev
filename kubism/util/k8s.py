from os import path
import yaml
from kubernetes import client, config

from kubism.core import core
from kubism.util.ref_dicts import registry


class K8s(core._scope_core_, core._registry_core_):

    def __init__(self, namespace=None):
        config.load_kube_config() # Load K8s configuration
        self.namespace = 'default' if namespace is None else namespace


    def add_deployment(self):
        pass


    def change_deployment(self):
        pass


    def remove_deployment(self):
        pass
    

    def add_service(self):
        pass

    
    def change_service(self):
        pass


    def remove_service(self):
        pass



class K8s_element:

    api = None


    def __init__(self, yaml, name, namespace='default'):
        self.name = name
        self.yaml = yaml
        self.namespace = namespace


    def get_body(self):
        with open(self.yaml, 'r') as f:
            body = yaml.safe_load(f)
        body['metadata']['name'] = self.name
        return body


    def apply(self):
        # "Apply" from yaml
        # Try to create it, and if it already exists, patch it instead
        try:
            return self.create()
        except:
            return self.patch()


    def create(self):
        return self.create_fcn(body=self.get_body(), namespace=self.namespace)

    def patch(self):
        return self.patch_fcn(self.name, body=self.get_body(), namespace=self.namespace)

    def delete(self):
        return self.delete_fcn(self.name, namespace=self.namespace)


    def create_fcn(self, *args, **kwargs):
        return None

    def patch_fcn(self, *args, **kwargs):
        return None

    def delete_fcn(self, *args, **kwargs):
        return None



class K8s_Deployment(K8s_element):

    api = client.AppsV1Api()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def create_fcn(self, *args, **kwargs):
        return self.api.create_namespaced_deployment(*args, **kwargs)

    def patch_fcn(self, *args, **kwargs):
        return self.api.patch_namespaced_deployment(*args, **kwargs)

    def delete_fcn(self, *args, **kwargs):
        return self.api.delete_namespaced_deployment(*args, **kwargs)



class K8s_Service(K8s_element):

    api = client.CoreV1Api()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def create_fcn(self, *args, **kwargs):
        return self.api.create_namespaced_service(*args, **kwargs)

    def patch_fcn(self, *args, **kwargs):
        return self.api.patch_namespaced_service(*args, **kwargs)

    def delete_fcn(self, *args, **kwargs):
        return self.api.delete_namespaced_service(*args, **kwargs)