# Copyright 2020 Regan Analytics

from kubism.util.k8s import K8s


_NAMESPACE_ = 'kubism'

class Cluster(K8s):

    def __init__(self, namespace=None):
        namespace = _NAMESPACE_ if namespace is not None else namespace
        super().__init__(namespace)


    


if __name__ == '__main__':
    Cluster()