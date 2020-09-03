import yaml
from kubism.util import greek, represent
from kubism.util.ref_dicts import registry, recipe


_DEBUG_ = False

# Naming Convention
def parse_name(name, assume_id=True):
    path = None
    base = None
    kind = None
    id = None
    if name is not None:
        if '/' in name:
            path, name = name.split('/')[:-2]
        if path is not None:
            base = path.split('/')[-1]
        if not ':' in name:
            kind = name
            if assume_id:
                id = '0'
                name = f'{kind}:{id}'
        else: 
            kind, id = name.split(':')
    return {'path':path, 'base':base, 'kind':kind, 'id':id, 'name':name}



class _scope_core_:

    name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope = {}


    def add_to_scope(self, obj):
        # Update dictionary
        self.scope.update({obj.name:obj})


    def get_scope_dict(self, pretty=False):
        scope_cascade = {}
        subs = []
        for obj in self.scope:
            subs.append({obj:self.scope[obj].get_scope_dict(pretty=False)[obj]})
        scope_cascade.update({self.name:subs})
        if pretty:
            return represent.cascade(scope_cascade)
        return scope_cascade


    def get_subs(self):
        subs = []
        objs = []
        for sub in self.scope:
            subs.append(sub)
            objs.append(self.scope[sub])
            subs_, objs_ = self.scope[sub].get_subs()
            for sub, obj in zip(subs_, objs_):
                subs.append(sub)
                objs.append(obj)
        return subs, objs



class _registry_core_:

    _registry_ = registry()

    @classmethod
    def register(cls, self):
        cls._registry_.update({self.kind:(self.name, self)})



class _deploy_core_:

    name = None

    _app_dir_ = '/app/'
    _kubism_dir_ = './kubism'
    _kubism_ = ['./kubism/deploy/kubio.py']
    _required_ = ['asyncio']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = None
        self._required = []
        self.add_files = None
        self.parent_image = None
        self.host = None
        self.yaml = None
        self.mapping = {}


    def set_deployment(self,
            app, 
            add_files=None,
            required=[],
            parent_image='python:latest',
            host=None,
            volumes=None
            ):
        self.app = app
        self.add_files = add_files
        self.parent_image = parent_image
        self.host = host
        self._volumes = volumes


    def add_map(self, field):
        self.update_map(field)


    def update_map(self, field):
        self.mapping.update(
            {field.name:{
                'FIELD':field.name, 
                'TYPE':field.type, 
                'PROPERTY':field.property}})


    def get_yaml(self):
        data = {'OBJECT':self.name}
        # Add deployment instructions
        data.update(self._get_deployment())
        # Add mapping of properties to fields
        data.update(self._get_mapping())
        return yaml.dump(data, default_flow_style=False)


    def _get_deployment(self):
        deployment = {'APP':self.app, 'APP_DIR':self._app_dir_}

        def if_incl(key, value=None):
            if value is None: value = self.__getattribute__(key.lower())
            if value is not None: deployment.update({key:value})

        if_incl('KUBISM', 
            {'DIR':self._kubism_dir_, 'FILES':self._kubism_})
        if_incl('REQUIRED', self.required)

        if_incl('PARENT_IMAGE')
        if_incl('HOST')
        if_incl('VOLUMES')
        return {'DEPLOYMENT':deployment}


    def _get_mapping(self):
        return {'MAPPING':list(map(
            lambda x: {'FIELD':{
            'NAME':self.mapping[x]['FIELD'], 
            'TYPE':self.mapping[x]['TYPE'], 
            'PROPERTY':self.mapping[x]['PROPERTY']}},
            self.mapping))}

    
    def write_yaml(self):
        pass


    @property
    def required(self):
        return [*self._required_, *self._required]


    @property
    def volumes(self):
        vols = self._volumes
        if isinstance(vols, (list, tuple, str)):
            mode = 'ro'
            if isinstance(vols, list):
                if len(vols) == 3:
                    mount, bind, mode = vols
                elif len(vols) == 2:
                    mount, mode = vols
                    bind = mount
                elif len(vols) == 1:
                    mount = bind = vols[0]
            else:
                mount = bind = vols
            return {'MOUNT':mount, 'BIND':bind, 'MODE':mode}
        return None


class _object_core_(_scope_core_,
                    _deploy_core_):
    '''
    kubism_core Abstract class
        base class for Model and Object classes
        attaches Model and Objects to State and Cluster
    '''

    _PREFIX_ = greek.KAPPA


    def __init__(self, *args, yaml=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_attached = False
        if yaml is not None:
            self.from_yaml(yaml)


    def from_yaml(self, yaml):
        pass


    def attach(self, base):
        '''
        Attach object core to state and cluster
        '''
        # Set base
        self.base = base
        # Set state and cluster
        self.state = base.state
        self.cluster = base.cluster
        # Initialize
        self.init_state()
        self.init_pod()
        self._is_attached = True


    def init_state(self):
        '''
        Initialize the state tables
            Γ - scope table
            Δ - data table
            Λ - model table
        '''
        self.create_delta_table()
        self.create_gamma_table()
        self.create_lambda_table()


    def init_pod(self):
        '''
        Initialize Object pod
        '''
        pass

    #### SCOPE METHODS ####
    #
    #
    def add_sub(self, obj):
        # Attach to base
        obj.attach(self)
        # Add sub to scope
        self.add_to_scope(obj)
        # Add obj to lambda table
        self.state.insert_row(self.lambda_table, 
            {'t_idx':self.state.t_idx, 
            'subs':obj.name, 
            'action':'ADD'}, 
            debug=_DEBUG_)
        # Add obj to gamma table
        self.state.insert_row(self.gamma_table, {'subs':obj.name}, debug=_DEBUG_)
        return obj
    #
    #
    #### / SCOPE METHODS ####


    ##### STATE METHODS #####
    #
    #
    def create_delta_table(self):
        table_idx = 't_idx'
        self.state.create_table(self.delta_table, index=table_idx, debug=_DEBUG_)


    def create_gamma_table(self):
        table_cols = ['subs TEXT', 'ports INTEGER']
        self.state.create_table(self.gamma_table, table_cols, index=True, debug=_DEBUG_)


    def create_lambda_table(self):
        table_cols = ['t_idx INTEGER', 'subs TEXT', 'fields TEXT', 'action TEXT']
        self.state.create_table(self.lambda_table, table_cols, index=False, debug=_DEBUG_)

    
    @property
    def delta_table(self):
        return f'{_object_core_._PREFIX_}_{self.fullname}_{greek.DELTA}'

    @property
    def gamma_table(self):
        return f'{_object_core_._PREFIX_}_{self.fullname}_{greek.GAMMA}'

    @property
    def lambda_table(self):
        return f'{_object_core_._PREFIX_}_{self.fullname}_{greek.LAMBDA}'


    def drop_tables(self):
        # Gather tables
        tables = [self.delta_table, self.gamma_table, self.lambda_table]
        for table in tables:
            # Drop table from state database
            self.state.drop_table(table, debug=_DEBUG_)
    #
    #
    #### / STATE TABLES ####


    #### RETRIEVAL METHODS
    #
    #
    def get(self, name):
        # Parse name
        name = parse_name(name)['name']
        # Check scope for name
        subs, objs = self.get_subs()
        if name in subs:
            idx = subs.index(name)
            return objs[idx]
        # Return if exists
        return False
    #
    #
    #### / RETRIEVAL METHODS ####

    def __add__(self, obj):
        '''
        Add object as sub ( + operator )
        '''
        self.add_sub(obj)
        return self


    def __truediv__(self, obj):
        '''
        Add object as sub ( / operator )
        '''
        self.add_sub(obj)
        return self


    @property
    def fullname(self):
        return self.name



class _sync_core_:

    _recipes_ = recipe()


    @classmethod
    def _sync_objects(cls, object):

        def apply_recipe(obj, kind_recipe):
            # Check if recipe already matches
            # Diff recipe with current fields
            old_names = [field.name for field in obj._fields]
            old_types = [field.type for field in obj._fields]
            for name, type_ in kind_recipe:
                matched = False
                if name in old_names:
                    if old_types[old_names.index(name)] == type_:
                        matched = True
                        old_names.remove(name)
                        old_types.remove(type_)
                # Apply Difference
                if not matched:
                    field = obj._add_field(name, type_)
                    obj._add_field_to_state(field)

        # Get recipe
        kind_recipe = cls._recipes_[object.kind]
        if kind_recipe != []:
            for _, obj in object._registry_[object.kind]:
                apply_recipe(obj, kind_recipe)

            


    @classmethod
    def synchronize(cls, object):
        cls._update_recipe(object)
        cls._sync_objects(object)


    @classmethod
    def _update_recipe(cls, object):
        if not object.kind in cls._recipes_:
            cls._recipes_.update({object.kind:object.fields})
        else:
            for field in object._fields:
                cls._recipes_.update(
                    {object.kind:(field.name, field.type)})

