# Example Config

Yoorbell uses the *config.yaml* file to source the following configuration information.

## API Token

The API token or key, provided by YO to identify your API account.

```yaml
api-token:  abcdefgh-ijkl-mnop-qrst-uvwxyz012345
```

## Users

There are two types of users Yoorbell needs to know about: *authorized users* and *notify users*.

```yaml
users:
  authorized:
    - USER001
    - USER002
    - USER004
  notify:
    - USER001
    - USER003
    - USER004
```

**Note that all usernames are in ALL CAPS.**

### Authorized Users

These users are authorized to unlock the door via Yoorbell.

### Notify Users

 These users will be notified when someone buzzes/rings the Yoorbell.

## Pins

Two pins are necessary to run Yoorbell: the *buzz* pin and the *door* pin.

```yaml
pins:
  buzz: 24
  door: 23
```

### Buzz Pin

The *buzz* pin is the pin which listens for a signal from the intercom buzzer.

### Door Pin

The *door* pin is the pin which will be signaled when the door must be unlocked.

## Port

Yoorbell runs an HTTP server to receive GET requests from the YO API servers, when a YO is sent to the API account.  *port* identifies the port on which the server should listen.

```yaml
port: 8979
```

## Calibration

There are a few pieces of calibration information Yoorbell uses, relating to ensuring a buzz is properly detected.

```yaml
calibration:
  bouncetime: 200
  samples:  20
  delay:  5
```

### Bouncetime

The *bouncetime* parameter is the time, in ms, which should be used to debounce the signal on the buzz pin.

### Samples

The *samples* parameter is the number of samples which should be taken of the value on the buzz pin, to determine whether the edge detected is a false positive.

### Delay

The *delay* parameter is the delay between samples, in ms.