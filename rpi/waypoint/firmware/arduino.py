import time
import RPi.GPIO as GPIO

RESET_GPIO_PIN = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(RESET_GPIO_PIN, GPIO.OUT)

# Initialize to LOW
GPIO.output(RESET_GPIO_PIN, GPIO.LOW)


def reset_arduino():
    GPIO.output(RESET_GPIO_PIN, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(RESET_GPIO_PIN, GPIO.LOW)
