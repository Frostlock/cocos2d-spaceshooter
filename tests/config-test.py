from spaceshooter.config import load_config, save_config

config = load_config()
assert isinstance(config, dict)

save_config(config)