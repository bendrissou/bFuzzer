import sys
import itertools
import random
from stateless.status import *
from stateless.exceptions import *

SET_OF_BYTES = [i for i in range(256)]
SEEN_AT = []

def init_set_of_bytes(s_bytes):
    global SET_OF_BYTES
    SET_OF_BYTES = s_bytes

def logit(v):
    print(v, file=sys.stderr)

def new_byte(choices):
     v = random.choice(choices)
     if isinstance(v, tuple): return v
     return (v,)

def backtrack(prev_bytes, all_choices):
    global SEEN_AT
    if not prev_bytes:
        raise Exception('Cant backtrack beyond zero index')
    # backtrack one byte
    seen = SEEN_AT[len(prev_bytes)-1]
    SEEN_AT = SEEN_AT[:-1]
    last_byte = prev_bytes[-1]
    logit('backtracking %d %s' % (len(prev_bytes), last_byte))
    #assert (last_byte,) in seen
    prev_bytes = prev_bytes[:-1]
    choices = [i for i in all_choices if i not in seen]
    if not choices:
        return backtrack(prev_bytes, all_choices)
    return seen, prev_bytes, choices

def till_n_length_choices(my_choices, rs):
    all_choices = []
    for r in range(1, rs+1):
        v = [tuple(i) for i in itertools.product(my_choices, repeat=r)]
        all_choices.extend(v)
    return all_choices


def generate(validate, prev_bytes=None):
    global SEEN_AT
    all_choices = [(i,) for i in SET_OF_BYTES]
    if prev_bytes is None: prev_bytes = []
    seen = set()
    while True:
        choices = [i for i in all_choices if i not in seen]
        if not choices:
            seen, prev_bytes, choices = backtrack(prev_bytes, all_choices)

        byte = new_byte(choices)
        cur_bytes = prev_bytes + list(byte)
        l_cur_bytes = len(cur_bytes)

        ib = MyBytearray(cur_bytes)
        logit('%s..%s, %s' % (ib.b[0:20], ib.b[-10:], len(ib.b)))

        #rv: Complete, Incomplete Incorrect
        #n: the index of the character -1 if not applicable
        #c: the character where error happened  "" if not applicable
        rv, n, _c = validate(ib)
        if rv == Status.Complete:
            return ib
        elif rv == Status.Incomplete:
            seen.add(byte)  # dont explore this byte again
            prev_bytes = cur_bytes
            assert len(prev_bytes) >= len(SEEN_AT)
            assert len(prev_bytes)- len(SEEN_AT) == 1
            SEEN_AT.append(seen)
            seen = set()

            # reset this if it was modified by incorrect
            all_choices = [(i,) for i in SET_OF_BYTES]
        elif rv == Status.Incorrect:
            seen.add(byte)
            if n is None or n == -1:
                continue
            else:
                rs = len(cur_bytes) - n
                all_choices = till_n_length_choices(SET_OF_BYTES, rs)
        else:
            raise Exception(rv)
    return None

class MyBytearray:
    def __init__(self, int_arr):
        self.b = bytearray(int_arr)

    def __len__(self):
        return len(self.b)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            if len(self.b) <= idx:
                raise NeedMoreException()
            return bytes([self.b[idx]])
        elif isinstance(idx, slice):
            if idx.start >= len(self.b):
                raise NeedMoreException()
            if idx.stop is not None and idx.stop > len(self.b):
                raise NeedMoreException()
            return MyBytearray(self.b[idx])
        else:
            assert False, idx

    def __repr__(self):
        return 'MyBytearray[%s]' % repr(self.b)

