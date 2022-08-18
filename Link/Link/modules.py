class Module:

    def __init__(self, uid, equipment_kind, role):
        self.uid = uid
        self.equipment_kind = equipment_kind
        self.role = role


class ModulesManager:

    def __init__(self):
        self.modules = []

    def declare_module(self, uid, equipment_kind, role):
        self.modules.append(Module(uid, equipment_kind, role))

    def clear_modules_list(self):
        self.modules.clear()

    def print_modules_list(self):
        i = 0
        for module in self.modules:
            i += 1
            print("Module ", i)
            print("equipment kind : ", module.equipment_kind)
            print("uid : ", module.uid)
            print("role : ", module.role)
