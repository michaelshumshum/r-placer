import sys
import management

if len(sys.argv) < 4:
    print('Missing arguments')
    sys.exit()

image_dir = sys.argv[1]
image_location = int(sys.argv[2]), int(sys.argv[3])


m = management.manager(image_dir, image_location)
m.run()

while True:
    try:
        if m.state == 'stopped':
            break
    except KeyboardInterrupt:
        m.stop()
        break
