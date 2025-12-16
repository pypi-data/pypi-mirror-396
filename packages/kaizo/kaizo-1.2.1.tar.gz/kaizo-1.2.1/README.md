# Kaizo

## YML file config reader and runner

The parser in `utils/parser.py` makes experiments highly flexible. Each YAML file may contain:

- **Direct values**: simple scalars (e.g., `epochs: 10`)
- **Resolvable values**: dictionaries specifying `module`, `source`, `call`, `args`, and optional `lazy`
- **References**: re-use values defined earlier in the config (`args.variable_name`)
- **Local modules**: custom Python files specified by `local` to extend functionality

This design lets you declaratively define entire experiments.

### Example Config

Below is the example config file:

```yaml
node01:
  module: trainer.models
  source: Trainer
  args:
    prefix: notebooks
    model_type: sde
    img_size: 32
    in_channels: 1
    batch_size: 64
    shuffle: True
    save_freq: 50
    dataset_path: ./notebooks/data
    beta_min: 0.1
    beta_max: 1
    target_transform:
    download: True
    loader:
      module: loaders
      source: DatasetLoader
      call: False
```
