import sys
import math
import random
import argparse
import time

# Install colorama if missing: pip install colorama
try:
    import colorama
except ImportError:
    print("Error: Please install colorama first: pip install colorama")
    sys.exit(1)

# VERSION
version = "2.0 BY NISHANT"

# Initialize colorama 'strip=False' ensures colors are preserved.
colorama.init(strip=False)

class ColourFulPrint:
    def __init__(self, mode=256):
        self.mode = mode

    def rainbow(self, freq, i):
        """
        Generates RGB values using sine waves.
        Math taken exactly from original source to ensure same vibrancy.
        """
        r = math.sin(freq * i) * 127 + 128
        g = math.sin(freq * i + 2 * math.pi / 3) * 127 + 128
        b = math.sin(freq * i + 4 * math.pi / 3) * 127 + 128
        return [r, g, b]

    def get_ansi_color(self, rgb):
        """
        Converts RGB to High-Intensity ANSI 256-color code.
        Formula taken from source [9] to guarantee bright colors.
        """
        # This maps the RGB to the 6x6x6 color cube (Indices 16 to 231)
        color = sum([16] + [int(6 * float(val) / 256) * mod 
                            for val, mod in zip(rgb, [36, 6, 1])])
        
        return f"\x1b[38;5;{color}m"

    def print_line(self, line, options):
        output = []
        line = line.rstrip()
        
        for i, char in enumerate(line):
            # Calculate position in the rainbow wave
            # options.os is the Random Offset that changes every time
            idx = options.os + i / options.spread
            
            # Get RGB
            rgb = self.rainbow(options.freq, idx)
            
            # Convert to ANSI
            color = self.get_ansi_color(rgb)
            
            output.append(color + char)
        
        # Reset color at the end of the line so your terminal doesn't stay colored
        output.append(colorama.Style.RESET_ALL)
        
        # Print the constructed line
        sys.stdout.write(''.join(output) + '\n')
        sys.stdout.flush()

        # Animation delay
        if options.animate:
            time.sleep(1.0 / options.speed)

    def cat(self, input_data, options):
        for line in input_data:
            self.print_line(line, options)
            options.os += 1

def run():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Bright Rainbow Text", epilog='Coded by Nishant !!!')

    parser.add_argument('files', metavar='FILE', nargs='*', help='Files to read')
    parser.add_argument('-p', '--spread', type=float, default=3.0, help='Rainbow spread')
    parser.add_argument('-F', '--freq', type=float, default=0.1, help='Rainbow frequency')
    parser.add_argument('-S', '--seed', type=int, default=0, help='Rainbow seed (0 = random)')
    parser.add_argument('-a', '--animate', action='store_true', help='Enable animation')
    parser.add_argument('-s', '--speed', type=float, default=20.0, help='Animation speed')
    parser.add_argument("-v", "--version", action="store_true", help="show current ColourFulPrint Version")
    
    args = parser.parse_args()

    if args.version:
        print("Version:", version)
        return

    # Initialize ColourFulPrint
    args.os = random.randint(0, 256) if args.seed == 0 else args.seed
    colourfulprint = ColourFulPrint()

    # Handle Input
    try:
        if not args.files:
            if not sys.stdin.isatty():
                # Pipe mode
                colourfulprint.cat(sys.stdin, args)
            else:
                parser.print_help()
        else:
            # File mode
            for filename in args.files:
                with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                    colourfulprint.cat(f, args)
                    
    except KeyboardInterrupt:
        sys.stdout.write(colorama.Style.RESET_ALL + '\n')
        sys.exit(0)

if __name__ == '__main__':
    run()