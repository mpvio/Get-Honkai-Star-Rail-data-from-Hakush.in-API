class TreeNode(dict): #unused
    def __init__(self, id, root=True, trace=None, value=None, children=None, params=None):
        super().__init__()
        self.__dict__ = self
        self.Id = id
        self.Root = root
        if trace != None: self.Name = trace
        if value != None: 
            if trace != None and trace in ["A2", "A4", "A6"]: self.Desc = value
            else: self.Value = value
        if params != None: self.Params = params
        self.Unlocks = list(children) if children is not None else []

    def add_child(self, child):
        self.Unlocks.append(child)

    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        node = TreeNode(dict_['effect'], dict_['children'])
        #the below two functions are equivalent
        #node.children = [TreeNode.from_dict(child) for child in node.children]
        node.Unlocks = list(map(TreeNode.from_dict, node.Unlocks))
        return node