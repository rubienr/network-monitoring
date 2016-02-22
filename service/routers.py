class MonitoringDataRouter(object):

    verbose = False

    def __init__(self):
        self.monitorDataLabel = "service"
        self.dbName = "data-db"

    def db_for_read(self, model, **hints):
        if self.verbose:
            print("R app label: %s" % (model._meta.app_label))
        if model._meta.app_label == self.monitorDataLabel:
            return self.dbName
        return None

    def db_for_write(self, model, **hints):
        if self.verbose:
            print("W app label: %s" % (model._meta.app_label))
        if model._meta.app_label == self.monitorDataLabel:
            return self.dbName
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if self.verbose:
            print("REL app label: %s" % (obj1._meta.app_label))
        if obj1._meta.app_label == self.monitorDataLabel or obj2._meta.app_label == self.monitorDataLabel:
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if self.verbose:
            print("MIGRATE app label: %s" % (app_label))
        if app_label == self.monitorDataLabel:
            return db == self.dbName
        return None