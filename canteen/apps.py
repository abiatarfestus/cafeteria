from django.apps import AppConfig

#
class StoreConfig(AppConfig):
    name = "canteen"

    def ready(self):
        import canteen.signals
