import hikari as hk
import typing as t


class EmbedBuilder:
    def __init__(self) -> None:
        self.embed: t.Optional[hk.Embed] = None

    def add_title(self, title: str):

        if self.embed is None:
            self.embed = hk.Embed()

        self.embed.title = title
        return self

    def add_url(self, url: str):

        if self.embed is None:
            self.embed = hk.Embed()

        self.embed.url = url
        return self

    def add_description(self, description: str):
        if self.embed is None:
            self.embed = hk.Embed()

        self.embed.description = description
        return self

    def add_color(self, color: hk.Color):
        if self.embed is None:
            self.embed = hk.Embed()

        self.embed.color = color
        return self

    def add_image(self, resource: hk.Resourceish):
        if self.embed is None:
            self.embed = hk.Embed()

        self.embed.set_image(resource)
        return self

    def add_thumbnail(self, resource: hk.Resourceish):

        if self.embed is None:
            self.embed = hk.Embed()

        self.embed.set_thumbnail(resource)
        return self

    def build(self):

        return self.embed
