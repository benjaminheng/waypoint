import time
import RPi.GPIO as GPIO

RESET_GPIO_PIN = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RESET_GPIO_PIN, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)


def reset_arduino():
    GPIO.output(RESET_GPIO_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(RESET_GPIO_PIN, GPIO.LOW)
