from src.receive.metadata_object import MetadataObject


class StaticMetadataObject(MetadataObject):

    def __init__(self, item_name, item_dict):
        super().__init__(item_name, item_dict)

    def receive_data(self):
        return self.item_dict['value']

    def get_source_type(self):
        return super().get_source_type()
