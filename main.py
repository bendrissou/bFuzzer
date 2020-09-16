import stateless.generate as G
import examples.jpegdecoder as decoder

def create_valid_inputs(n=1):
    i = 0
    parray = []
    while True:
        created_bits = G.generate(decoder.validate, parray)
        if created_bits is not None:
            print(repr(created_bits), file=sys.stderr)
            with open('file.x', 'wb+') as f:
                f.write(created_bits.b)
            i += 1
            if (i >= n):
                break

if __name__ == "__main__":
    import sys
    create_valid_inputs()
