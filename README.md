# Ena Discord Bot

A multipurpose discord bot for my own server. It uses PostgresSQL database and [hikari.py](https://github.com/hikari-py/hikari) python discord library. This still lacks a lot of features but i'm confident that you can extend it properly.

### Roadmap

|  progress  | plugin |
| --- | --- |
| ![](https://geps.dev/progress/0)  | `embed_utils`  |
| ![](https://geps.dev/progress/0)  | `saucenao api` |
| ![](https://geps.dev/progress/0)  | `genshin codes` |

#### Adding plugins
It should be easy to extend the bot with plugins and customizations using `hikari.py` plugins. You can use `injectable` decorator of the bot to modify it based to your liking:
```py
# use injectable in a function that takes the bot as parameter and returns the bot.

from your_plugins import your_nice_plugin

@injectable
def default_plugins(bot: lb.BotApp):
    
    DEFAULT_PLUGINS = [
        your_nice_plugin # a lightbulb.Plugin instance
    ]
    
    # you can easily customize the bot like this
    for plugin in DEFAULT_PLUGINS:
        bot.load_extensions(plugin)

    return bot
```
Hook it up on a main decorating function
```py
@default_plugins
def ena(bot: lb.BotApp) -> lb.BotApp:
    return bot
```
And then use it to decorate your main bot instance
```py
bot = ena(lb.BotApp(token=TOKEN))
```
