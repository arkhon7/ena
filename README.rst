# Ena Discord Bot

A multipurpose discord bot for my own server. It uses PostgresSQL database and [hikari.py](https://github.com/hikari-py/hikari) python discord library. This still lacks a lot of features but i'm confident that you can extend it properly.

### Roadmap
|  progress  | plugin |
| --- | --- |
| ![](https://geps.dev/progress/60)  | `reaction role`  |
| ![](https://geps.dev/progress/10)  | `templating` |
| ![](https://geps.dev/progress/0)  | `genshin codes` |
| ![](https://geps.dev/progress/0)  | `code` |

#### Adding plugins
If you are knowledgeable on using hikari, it should be easy to extend the bot with plugins and customizations using the `injectable` decorator of the bot:
```py
# use injectable in a function that takes the bot as parameter and returns the bot.
@injectable
def default_plugins(bot: lb.BotApp):
    
    DEFAULT_PLUGINS = [
        "plugins.debug",
        "plugins.react_role",
    ]
    # you can easily customize the bot here
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
