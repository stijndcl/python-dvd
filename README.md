# python-dvd
Python tool that bounces a DVD logo around your terminal

## Usage

The project doesn't have any dependencies, so you can just run it directly without installing anything:

```sh
$ python3 dvd.py
```

The `delay` option sets the delay between screen updates in milliseconds, and defaults to `1000` (1 second). To make the logo faster or slower, pass a value for this option:
```sh
# Faster
$ python3 dvd.py --delay 250

# Slower
$ python3 dvd.py --delay 2000
```
