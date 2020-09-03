# Copyright 2020 Regan Analytics

from kubism.core import core
from kubism.core.schedule import Backlog
from kubism.client.state import State
from kubism.client.cluster import Cluster
from kubism.util import greek, represent
from kubism.util.ref_dicts import registry


_DEBUG_ = False


class Model(core._object_core_):

    _ids_ = {}

    def __init__(self, name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = '_' if name is None else name
        self.create_base()


    def create_base(self):
        '''
        Create Model base for attachment
        '''
        # Set state and cluster
        self.state = State()
        self.cluster = Cluster()
        # Initialize
        self.init_state()
        self.init_pod()
        self._is_attached = True


    def cleanup(self):
        # Get all objects
        _, objs = self.get_subs()
        for obj in objs:
            # Drop tables for all objects
            obj.drop_tables()


    def __del__(self):
        print('Cleaning Up Databases')
        self.drop_tables()



class Object(core._object_core_, 
            core._registry_core_, 
            core._sync_core_
            ):

    _registry_ = registry()

    sync = True

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._kind = ''
        self._fields = []
        self.id = 0
        self.backlog = Backlog()
        self.name = name



    @Backlog.condition
    def attach(self, base):
        super().attach(base)


    def add_sub(self, obj):
        if isinstance(obj, str):
            obj = Object(obj)
        super().add_sub(obj)


    def add_field(self, field, type='TEXT'):
        field = self._add_field(field, type)
        self._add_field_to_state(field)
        Object.synchronize(self) 
        return field


    @Backlog.method(condition='_is_attached', trigger='Object.attach')
    def _add_field_to_state(self, field):
        # Add field to lamda table
        self.state.insert_row(self.lambda_table, 
            {'t_idx':self.state.t_idx, 
            'fields':field.name, 
            'action':'ADD'}, 
            debug=_DEBUG_)
        # Add field to delta table
        self.state.add_column(self.delta_table, 
            {field.name:field.type},
            debug=_DEBUG_)



    @property
    def name(self):
        return f'{self.kind}:{self.id}'

    @property
    def fullname(self):
        return f'{self.path}/{self.name}'

    @name.setter
    def name(self, name):
        # Add ID if one hasn't been assigned
        kind = core.parse_name(name)['kind'] #TODO: allow custom ids
        self.kind = kind
        self.id = self.get_next_id()


    @property
    def path(self):
        return self.base.name


    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, kind):
        self._kind = kind
        Object.register(self)
        Object.synchronize(self)



    @property
    def fields(self):
        fields = {}
        for field in self._fields:
            fields.update({field.name:field.value})
        return fields


    def _add_field(self, field, type, property=None):
        if isinstance(field, str):
            field = Field(field, type, property)
        field.base = self
        self._fields.append(field)
        self.add_map(field) #TODO: Should only have one per instance ... Class Metaprogramming?
        return field


    def get_next_id(self):
        # Check for kind in _OBJ_IDS_REF_
        if self.kind in Model._ids_:
            last_id = Model._ids_[self.kind] #TODO: allow custom ids
            id = last_id + 1
        else:
            id = 0
        Model._ids_.update({self.kind:id})
        return id


    def __add__(self, obj_field):
        if isinstance(obj := obj_field, Object):
            self.add_sub(obj)
        elif isinstance(field := obj_field, Field):
            self.add_field(field)
        return self



class Field:

    def __init__(self, name, type='TEXT', property=None):
        self.name = name
        self.type = type
        self.value = []
        self.base = 'TEXT'
        self.property = name if property is None else property