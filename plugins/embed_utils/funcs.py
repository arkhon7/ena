import hikari as hk

# import typing as t


class EmbedBuilder(hk.Embed):
    def __init__(self) -> None:
        self.embed: hk.Embed = hk.Embed()

    def add_title(self, title: str):

        self.embed.title = title
        return self

    def add_url(self, url: str):

        self.embed.url = url
        return self

    def add_description(self, description: str):

        self.embed.description = description
        return self

    def add_color(self, color: hk.Color):

        self.embed.color = color
        return self

    def add_image(self, resource: hk.Resourceish):

        self.embed.set_image(resource)
        return self

    def add_thumbnail(self, resource: hk.Resourceish):

        self.embed.set_thumbnail(resource)
        return self

    def build(self):

        return self.embed
