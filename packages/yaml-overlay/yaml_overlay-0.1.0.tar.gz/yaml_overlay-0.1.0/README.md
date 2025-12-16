# yaml-overlay

This CLI will overlay the argument YAML values files from lowest to highest precedence, associate a color for each file, and colorize each value in the resulting YAML overlay according to its provenance. This can be very useful when dealing with Kubernetes charts deployments with many different value files (environment values, default values, private values, instance values, etc) to track down where a particular value is defined.

See https://blog.balthazar-rouberol.com/visualizing-a-yaml-value-files-overlay for more details.

## Installation

```console
$ pip install yaml-overlay
$ yaml-overlay [yaml files]
```

## Example

![colorized yaml overlay](https://f003.backblazeb2.com/file/brouberol-blog/yaml-overlay/yaml-overlay.webp)
