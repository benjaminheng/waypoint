SELECT_START_NODE = 'Select your current position'
SELECT_END_NODE = 'Select your destination'
SELECT_CONFIRMATION = 'You have selected {0}, {1}, {2}, and {3}, {4}, {5}'
INVALID_NODE = 'Invalid selection: {0}, {1}, {2}'
INITIAL_ORIENTATION = 'Please turn to face the next location'
PROMPT_TO_START_NAVIGATION = 'Press the star key to start'

# 90 degree turns
TURN = '{0}'
TURN_SLIGHTLY = 'Slight {0}'
TURN_BY_DEGREES = 'Turn {0} {1} degrees'

STOP = 'Stop!'
OBSTACLE_DETECTED = 'Obstacle'
OBSTACLE_DETECTED_DIRECTION = 'Obstacle {0}'
OBSTACLE_CLEARED = 'Obstacle cleared. Proceed forward.'
PROCEED_FORWARD = 'Proceed forward.'
PROCEED_FORWARD_STEPS = 'Proceed forward {0} steps.'
DESTINATION_REACHED = 'Destination reached'
STAIRCASE_AHEAD = 'Staircase ahead'
CURRENT_POSITION = 'You are at {0}, {1}, {2}'

YOU_ARE_THE_BEST = 'Congratulations. You are the best.'

PRIORITY_MAP = {
    STOP: 5,
    TURN: 10,
    TURN_SLIGHTLY: 10,
    TURN_BY_DEGREES: 10,

    OBSTACLE_DETECTED: 10,
    OBSTACLE_DETECTED_DIRECTION: 10,
    OBSTACLE_CLEARED: 10,

    PROCEED_FORWARD: 10,
    PROCEED_FORWARD_STEPS: 10,

    DESTINATION_REACHED: 5,
    YOU_ARE_THE_BEST: 5,

    STAIRCASE_AHEAD: 10,
    CURRENT_POSITION: 10,
}
