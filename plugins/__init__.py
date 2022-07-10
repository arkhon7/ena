import os

PLUGINS = [name for name in os.listdir("plugins") if os.path.isdir(os.path.join("plugins", name))]

print(PLUGINS)
