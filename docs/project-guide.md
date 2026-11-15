# Reviewer guide

## Embedded source collection

- [`RCWS_v1.ino`](../firmware/arduino-mega/RCWS_v1/RCWS_v1.ino): original Arduino Mega sketch.
- The same source folder also contains the original `Communication`, `Motor`, `Limits` and `ESCControl` files. Their inclusion is not a claim that every file is used by the sketch.
- [`Arduino_Code.ino`](../firmware/arduino-mega/Arduino_Code/Arduino_Code.ino): separately preserved Arduino experiment.
- [`ESP32_Code.ino`](../firmware/esp32/ESP32_Code/ESP32_Code.ino): ESP32 application, including embedded interface markup.

## Python source collection

| File | Role in the source collection |
| --- | --- |
| [`dual_camera_detector.py`](../software/balloon-vision/src/dual_camera_detector.py) | Balloon image processing application |
| [`hsv_tuner.py`](../software/balloon-vision/src/hsv_tuner.py) | RealSense color/depth camera processing script |
| [`test_camera_cv.py`](../software/balloon-vision/src/test_camera_cv.py) | OpenCV camera check script |

Names are preserved from the original project. Filenames alone should not be interpreted as verified feature claims. In particular, the archived camera images do not document a successful detection demonstration.

## Electronic documents

The [`FG1000 Altium folder`](../hardware/altium/FG1000/) contains the `.PrjPcb` project, three `.SchDoc` documents and two local `.SchLib` libraries. The separate [`vendor-libraries`](../hardware/altium/vendor-libraries/) folder contains third-party symbols and footprints. A footprint library is not a completed board layout.

## Evidence boundaries

This repository contains source and design artifacts. It does not provide a test report, verified release, measured performance results, demonstration video. No such evidence is implied by the presentation artwork.

## Authorship scope

[FurkanUstaoglu](https://github.com/FurkanUstaoglu) developed the electronics, hardware design and software presented here as part of a graduation project. Third-party component libraries are identified separately and are not claimed as original work.
