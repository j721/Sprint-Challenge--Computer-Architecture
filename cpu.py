"""CPU functionality."""

import sys

SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        #initialize 
        self.ram = [0] * 256        #256 bytes of memory
        self.reg = [0] * 8      # 8 registers to store data
        self.pc = 0     #program counter acts as a pointer
        self.reg[SP] = 0xF4
        self.flags = 0b00000000

    
    def ram_read(self, MAR):    # (MAR) Memory Address Register holds memory address/position we're reading from 
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):      
        self.ram[MAR] = MDR # (MDR) Memory Data Register is the data getting written into the MAR. LS8-spec.md file

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#",1)[0]
                        line = int(line, 2)  # int() is base 10 by default
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):       
        """ALU operations.  
        Arithmetic logic unit- responsible for math"""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "MUL": #multiply instruction
            self.reg[reg_a] *= self.reg[reg_b]
        
        #CMP instruction handled by the ALU, compares the values in two registers
        # FL bits: 00000LGE
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags = 0b00000001  #Equal (E) flag 

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags =  0b00000010 # Greater than (G) Flag

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flags = 0b00000100 # Less (L) flag     
            
            # else:
            #     self.flags = 0b00000100 # Less (L) flag 


        elif op == "AND":
            pass

        elif op == "OR":
            pass

        elif op == "XOR":
            pass

        elif op == "NOT":
            pass    

        elif op == "SHL":
            pass   

        elif op == "SHR":
            pass 

        elif op == "MOD":
            pass 

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        instructions ={
             0b10000010: 'LDI',
             0b01000111: 'PRN',
             0b00000001: 'HLT',
             0b10100010: 'MUL',
             0b01000110: 'POP',
             0b01000101: 'PUSH',
             0b01010000: 'CALL',
             0b00010001: 'RET' ,
             0b10100000: 'ADD',
             0b10100111: 'CMP',
             0b01010100: 'JMP',
             0b01010101: 'JEQ',
             0b01010110: 'JNE',
             0b10101000: 'AND',
             0b10101010: 'OR',
             0b10101011: 'XOR',
             0b01101001: 'NOT',
             0b10101100: 'SHL',
             0b10101101: 'SHR',
             0b10100100: 'MOD'
        }

        while running: 
            i = self.ram[self.pc]       #single instruction that pc is pointing to in the ram(memory). Pc is pointing to the current instruction

            if instructions[i] == 'LDI':
                #set up register
                reg_num = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                #save value to register
                self.reg[reg_num] = value

                self.pc +=3
            
            elif instructions[i] == 'PRN':
                #print the register
                reg_num = self.ram[self.pc +1]
                print(self.reg[reg_num])

                self.pc +=2
            
            elif instructions[i] == 'HLT':
                #halt 
                running = False
            
            elif instructions[i] == 'MUL':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('MUL', reg_a, reg_b)

                self.pc +=3
            
            elif instructions[i] == 'ADD':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('ADD', reg_a, reg_b)

                self.pc +=3
            
            elif instructions[i] == 'POP':
                address_to_pop_from = self.reg[SP]
                value = self.ram[address_to_pop_from]

                reg_num = self.ram[self.pc + 1]
                self.reg[reg_num] = value

                self.reg[SP] += 1

                self.pc += 2
            
            elif instructions[i] == 'PUSH':
                self.reg[SP] -= 1
                self.reg[SP] &= 0xff

                reg_num = self.ram[self.pc + 1]
                value = self.reg[reg_num]

                address_to_push_from = self.reg[SP]
            
                self.ram[address_to_push_from] = value

                self.pc += 2
            
            elif instructions[i] == 'CALL':
                # Get address of the next instruction
                return_addr = self.pc + 2 
                # Push that on the stack
                self.reg[SP] -= 1
                address_to_push_to = self.reg[SP]
                self.ram[address_to_push_to] = return_addr

                # Set the PC to the subroutine address
                reg_num = self.ram[self.pc + 1]
                subroutine_addr = self.reg[reg_num]

                self.pc = subroutine_addr

            elif instructions[i] == 'RET':
                # Get return address from the top of the stack
                address_to_pop_from = self.reg[SP]
                return_addr = self.ram[address_to_pop_from]
                self.reg[SP] += 1

                # Set the PC to the return address
                self.pc = return_addr
            
            elif instructions[i] == 'CMP':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('CMP', reg_a, reg_b)
                self.pc +=3

            #Jump to the address stored in the given register.
            elif instructions[i] == 'JMP':
                #get the register a value
                reg_a = self.ram[self.pc + 1]
            # Set the PC to the address stored in the given register.
                self.pc = self.reg[reg_a]
                return True

            #JEQ register
            elif instructions[i] == 'JEQ':
                #get the register a value
                reg_a = self.ram[self.pc + 1]
            # If equal flag is set (true), jump to the address stored in the given register.
                if (self.flags & 0b00000001) == 1: 
                    self.pc = self.reg[reg_a]
                else:
                    self.pc +=2

            # JNE register
            elif instructions[i] == 'JNE':
                 #get the register a value
                reg_a = self.ram[self.pc + 1]  
            # If E flag is clear (false, 0), jump to the address stored in the given register.
                if (self.flags & 0b00000001) == 0: 
                    self.pc = self.reg[reg_a]
                else:
                    self.pc +=2

            else: 
                print(f"Unknown instruction {i}")



# testCPU = CPU()
# testCPU.load()
# testCPU.run()