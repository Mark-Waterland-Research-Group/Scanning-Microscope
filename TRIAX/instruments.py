import pyvisa
from pyvisa.constants import StopBits, Parity
import time

DEBUGMODE = True

class Triax:
    
    def __init__(self):
        self.triax = None
        self.entry_slit_pos = None
        self.exit_slit_pos = None
        
    def flush_buffer(self):
        r_bytes = self.triax.read_raw()  # Read and discard any available bytes
        if DEBUGMODE:
         print('Flushed bytes:', r_bytes)
        return

    def list_resources(self):
        rm = pyvisa.ResourceManager()
        print(rm.list_resources())
        return

    def status(self):
        ''' Returns current status information of Triax NOT
        WORKING. see if pyvisa has this method implemented'''
        if self.triax != None:
            print('Status: connected')
        else:
            print('Status: not connected')

    def open(self):
        '''Starts communication with Triax'''
        rm = pyvisa.ResourceManager()
        if DEBUGMODE:
            print('Available: ', rm.list_resources())
        self.triax = rm.open_resource('ASRL1::INSTR')
        self.triax.baud_rate = 4800
        self.triax.parity = Parity.none
        self.triax.data_bits = 8
        self.triax.stop_bits = StopBits.one
        self.triax.read_termination = '\r'
        time.sleep(0.5)
        self.flush_buffer()
        self.triax.write_raw(b'\xf8\xde')
        time.sleep(0.5)
        self.flush_buffer()
        n_bytes = 0
        restart = 0
        while n_bytes <= 0:
            self.triax.write_raw(b' ')
            time.sleep(0.5)
            n_bytes = self.triax.bytes_in_buffer
            restart += 1
            if restart == 3:
                self.triax.close()
                print('''Could not establish communication
                with Monochromator''')  # finish the code execution
                return
            if DEBUGMODE:
                print('Answered <space>')
                print('Bytes to read ', n_bytes)
            ans = self.triax.read_bytes(1)
            if DEBUGMODE:
                print('Answer is ', ans)
            restart = 0
            while ans != b'F':
                if ans == b'*':
                    if DEBUGMODE:
                        print('Went into *')
                    self.flush_buffer()
                    self.triax.write_raw(b' \xf7 ')
                    time.sleep(0.5)
                    # returns b'='
                    self.flush_buffer()
                elif ans == b'B':
                    if DEBUGMODE:
                        print('Went into B')
                    self.triax.write_raw(b'O2000 \x00 ')
                    time.sleep(0.5)
                    # returns b'*', it means we already are in F
                    if (self.triax.bytes_in_buffer > 0):
                        if (self.triax.read_bytes(1) == b'*'):
                            break
                elif ans == b'\x1B':
                    if DEBUGMODE:
                        print('<escape>')
                    self.flush_buffer()
                    self.triax.write_raw(b'\xf8')
                elif ans == b'ERROR':
                    if restart < 3:
                        if DEBUGMODE:
                            print('Error, restart ', restart)
                        self.triax.write_raw(b'\xf8\xde')
                    else:
                        if DEBUGMODE:
                            print('Error, close')
                        self.triax.close()
                        print('''Could not establish communication
                        with Monochromator''')  # finish the code execution
                        return
                time.sleep(0.5)
                self.triax.write_raw(b' ')
                time.sleep(0.5)
                n_bytes = self.triax.bytes_in_buffer
                if DEBUGMODE:
                    print('Bytes after <space>? ', n_bytes)
                if n_bytes > 0:
                    ans = self.triax.read_bytes(1)
                    self.flush_buffer()
                else:
                    ans = b'ERROR'
                restart += 1
                if DEBUGMODE:
                    print('Answer: ', ans)
            print('Communication with Triax established!')
            self.init_motor()
            return

    def init_motor(self):
        self.triax.write_raw(b'A')
        print('Initializing Triax motors, please wait 30 seconds...')
        self.motor_busy_check()
        self.init_slits()
        self.motor_busy_check()
        ans = self.triax.read_bytes(1)  ##deberia comprobar antes el buffer?
        if DEBUGMODE:
            print(ans)
        print('Triax initialized!')
        return

    def close(self):
        self.triax.close()
        print('Communication with Triax terminated!')
        return

    def read_motor_pos(self, bool_print=True):
        while self.motor_busy_check():
            pass
        self.triax.write_raw(b'H0 \x0d ')
        self.wait_OK()
        ans = self.triax.read()
        ans = int(ans)
        if bool_print:
            print('Motor step position = ', ans)
            wavelen = (ans - 4010) / 7 + 556
            print('Wavelength = ', wavelen, 'nm')
        return ans

    def set_motor_pos(self, pos):
        '''Corrects stored "motor position" value. Does NOT move
        motor.
        Param:
        pos (int): New position value. Motor position range 2218
        to 7818 steps
        Returns:
        true if confirmation "o" is received from triax'''
        # it checks if new position is inside limits
        if pos < 2218 or 7818 < pos:
            print('Error: Motor position outside limits (range: 2218 to 7818 steps)')
            return False
        s_instruction = 'G0,' + str(pos) + ' \x0d '
        b_instruction = bytes(s_instruction, 'utf-8')
        if DEBUGMODE:
            print('sending: ')
            print(b_instruction)
        self.triax.write_raw(b_instruction)
        ans = self.wait_OK()
        return ans

    def move_motor(self, move_steps):
        '''Moves motor position. Function waits for motor to stop to
        continue.
        Param:
        move_steps (int): Steps to move (+/-). Motor position
        range 2218 to 7818 steps
        Returns:
        true if confirmation "o" is received from triax'''
        ##habria que tener en cuenta el backlash para movimientos negativos
        # it checks if movement is inside limits
        current_pos = self.read_motor_pos(False)
        final_pos = current_pos + move_steps
        if final_pos < 2218 or 7818 < final_pos:
            print('Error: Motor moves outside limits (range: 2218 to 7818 steps)')
            return False
        while self.motor_busy_check():
            pass
        s_instruction = 'F0,' + str(move_steps) + ' \x0d '
        b_instruction = bytes(s_instruction, 'utf-8')
        if DEBUGMODE:
            print('sending: ')
            print(b_instruction)
        self.triax.write_raw(b_instruction)
        ans = self.wait_OK()
        return ans

    def swipe_motor(self, lambda_i, lambda_f, stepsize):
        '''Swipes motor from "lambda_ i" to "lambda_f" with steps of
        size "stepsize".
        Param:
        lambda_i (int): Initial position in nm 300-1100nm
        lambda_f (int): Final position in nm 300-1100nm
        stepsize (int): Step size in nm 5-50nm'''
        if lambda_i < 300 or lambda_i > 1100 or lambda_f < 300 or lambda_f > 1100:
            print('Error: Values off limits. Swipe range: 300-1100nm')
            return
        if stepsize < 5 or stepsize > 50:
            print('Error: Stepsize has to be between 5-50nm')
            return
        lambda_i = nm_to_step(lambda_i)
        lambda_f = nm_to_step(lambda_f)
        stepsize = stepsize * 7
        if DEBUGMODE:
            print('i: ', lambda_i, ' f: ', lambda_f, ' step: ', stepsize)
        print('Starting swipe...')
        current_pos = self.read_motor_pos(False)
        self.move_motor(lambda_i - current_pos)
        if DEBUGMODE:
            self.read_motor_pos()
        for i in range(lambda_i, lambda_f, stepsize):
            if i + stepsize > lambda_f:
                break
            self.move_motor(stepsize)
            if DEBUGMODE:
                print('Expected: ', i + stepsize, '. Real: ', self.read_motor_pos(False))
        current_pos = self.read_motor_pos(False)
        self.move_motor(lambda_f - current_pos)
        if DEBUGMODE:
            print('Expected: ', i + stepsize, '. Real: ', self.read_motor_pos(False))
        print('Swipe completed!')
        return

    def wait_OK(self):
        '''Waits for Triax's 'o' confirmation, if the answer is different
        the buffer is flushed'''
        n_bytes = 0
        while n_bytes < 1:
            time.sleep(0.1)
            n_bytes = self.triax.bytes_in_buffer
        ## a lo mejor aqui podria poner una rutina de timeout y restart
        ans = self.triax.read_bytes(1)
        if ans == b'o':
            # if DEBUGMODE: print('"o" received')
            return True
        if DEBUGMODE:
            print('Something different from "o" received')
        ## algo a hacer si no se recibe ok?
        self.flush_buffer()
        return False

    def motor_busy_check(self):
        '''Polls Triax to check if motor (also slit motor) movement
        is completed or still in progress
        Returns:
        True: Motor busy
        False: Motor free'''
        self.triax.write_raw(b'E')
        if self.wait_OK():
            ans = self.triax.read_bytes(1)
            if ans == b'z':
                return False
            return True

    def init_slits(self):
        while self.motor_busy_check():
            pass
        self.entry_slit_pos = 500
        s_instruction = 'k0,0,500 \x0d '
        b_instruction = bytes(s_instruction, 'utf-8')
        self.triax.write_raw(b_instruction)
        if DEBUGMODE:
            print(self.wait_OK())
        time.sleep(1)
        self.exit_slit_pos = 20
        s_instruction = 'k0,2,20 \x0d '
        b_instruction = bytes(s_instruction, 'utf-8')
        self.triax.write_raw(b_instruction)
        if DEBUGMODE:
            print(self.wait_OK())
        return

    def move_entry_slit(self, step_pos):
        if step_pos < 0 or step_pos > 1000:
            print('Movement out of bounds. Slits limit 0-1000 steps.')
            return False
        while self.motor_busy_check():
            pass
        steps_to_move = step_pos - self.entry_slit_pos
        s_instruction = 'k0,0,' + str(steps_to_move) + ' \x0d '
        b_instruction = bytes(s_instruction, 'utf-8')
        self.triax.write_raw(b_instruction)
        self.entry_slit_pos = step_pos
        if DEBUGMODE:
            print(self.wait_OK())
        return True

    def move_exit_slit(self, step_pos):
        if step_pos < 0 or step_pos > 1000:
            print('Movement out of bounds. Slits limit 0-1000 steps.')
            return False
        while self.motor_busy_check():
            pass
        steps_to_move = step_pos - self.exit_slit_pos
        s_instruction = 'k0,2,' + str(steps_to_move) + ' \x0d '
        b_instruction = bytes(s_instruction, 'utf-8')
        self.triax.write_raw(b_instruction)
        self.exit_slit_pos = step_pos
        if DEBUGMODE:
            print(self.wait_OK())
        return True

# Utilities
def nm_to_step(nm):
    steps = (nm - 556) * 7 + 4010
    return steps

def step_to_nm(steps):
    nm = (steps - 4010) / 7 + 556
    return nm

