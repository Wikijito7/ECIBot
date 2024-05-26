class Radio:
    def __init__(self, radio_name: str, radio_url: str):
        self.__radio_name = radio_name
        self.__radio_url = radio_url

    def get_radio_name(self):
        return self.__radio_name

    def get_radio_url(self):
        return self.__radio_url

    def __str__(self):
        return f"Radio({self.__radio_name}, {self.__radio_url})"
