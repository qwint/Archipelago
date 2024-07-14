class Patch:
    process = None
    base_address = 0
    current_address = 0
    name = 'Unnamed'
    byte_list = b''
    original_bytes = b''
    patch_applied = False
    def __init__(self, name, base_address, process=None):
        self.name = name
        self.base_address = base_address
        self.process = process

    def __str__(self):
        return f'Patch {self.name} from {hex(self.base_address)} to {hex(self.get_patch_end())} ({len(self)} bytes): {self.byte_list.hex(" ")}'

    def __len__(self):
        return len(self.byte_list)

    def get_patch_end(self):
        return self.base_address + len(self)

    def apply(self):
        if self.process == None:
            print(f'Failed to apply patch {self.name}. Process has not been specified!')
            return False

        if self.patch_applied:
            print(f'Failed to apply patch {self.name}. Patch already applied!')
            return False

        self.original_bytes = self.process.read_bytes(self.base_address, len(self.byte_list))
        self.process.write_bytes(self.base_address, self.byte_list, len(self.byte_list))

        if self.process.read_bytes(self.base_address, len(self.byte_list)) != self.byte_list:
            print(f'Failed to apply patch {self.name} ({len(self)} length) at {hex(self.base_address)}!')
            return False

        print(f'Patch {self.name} ({len(self)} length) applied at {hex(self.base_address)} successfully!')
        self.patch_applied = True
        return True

    def revert(self):
        if self.process == None:
            print(f'Failed to apply patch {self.name}, process has not been specified!')
            return False

        if not self.patch_applied:
            print(f'Failed to revert patch {self.name}, patch has not yet been applied!')
            return False

        if self.original_bytes == None or len(self.original_bytes) == 0:
            print(f'OriginalBytes array is blank. Cannot revert patch {self.name}!')
            return False

        self.process.write_bytes(self.base_address, self.original_bytes, len(self.original_bytes))

        if self.process.read_bytes(self.base_address, len(self.original_bytes)) != self.original_bytes:
            print(f'Failed to revert patch {self.name} ({len(self)} length) at {hex(self.base_address)}!')
            return False

        print(f'Patch {self.name} ({len(self)} length) at {hex(self.base_address)} reverted successfully!')
        self.patch_applied = False
        self.original_bytes = b''
        return True

    def add_bytes(self, bytes):
        self.byte_list += bytes
        return self

    def xor_ecx_ecx(self): #2 bytes
        self.add_bytes(b'\x31\xc9')
        return self

    def call_near(self, address): #5 bytes
        diff = address - (self.get_patch_end() + 5)
        print('diff: {} - {} = {}'.format(hex(address), hex(self.get_patch_end() + 5), hex(diff)))
        self.add_bytes(b'\xe8' + (diff).to_bytes(4, 'little', signed=True))
        return self

    def call_far(self, address): #16 bytes
        self.add_bytes(b'\xff\x15\x02\x00\x00\x00\xeb\x08' + address.to_bytes(8, 'little', signed=True))
        return self

    def call_rax(self): #2
        self.add_bytes(b'\xff\xd0')
        return self

    def jmp_near(self, address): #5 bytes
        diff = address - (self.get_patch_end() + 5)
        self.add_bytes(b'\xe9' + (diff).to_bytes(4, 'little', signed=True))
        return self

    def jmp_far(self, address): #14 bytes
        self.add_bytes(b'\xff\x25\x00\x00\x00\x00' + address.to_bytes(8, 'little', signed=True))
        return self

    def nop(self, count):
        self.add_bytes(b'\x90' * count)
        return self

    def mov_ecx(self, value): #5
        self.add_bytes(b'\xb9' + value.to_bytes(4, 'little'))
        return self

    def mov_edx(self, value): #5
        self.add_bytes(b'\xba' + value.to_bytes(4, 'little'))
        return self

    def lea_r8_value(self, value): #7
        self.add_bytes(b'\x4c\x8d\x05' + value.to_bytes(4, 'little'))
        return self

    def lea_eax_rdi_minus1(self): #3
        self.add_bytes(b'\x8d\x47\xff')
        return self

    def cmp_al1_byte(self, value): #2
        self.add_bytes(b'\x3c' + value.to_bytes(1, 'little'))
        return self

    def ja_near(self, address): #6
        start = self.get_patch_end() + 6
        diff = address - start
        print('diff: {} - {} = {}'.format(hex(address), hex(start), hex(diff)))
        self.add_bytes(b'\x0f\x87' + diff.to_bytes(4, 'little'))
        return self

    def mov_to_rax(self, value): #10
        self.add_bytes(b'\x48\xb8' + value.to_bytes(8, 'little'))
        return self

    def mov_rax_to_r8(self): #3
        self.add_bytes(b'\x4c\x8b\xc0')
        return self

    def jmp_rax(self): #2
        self.add_bytes(b'\xff\xe0')
        return self

    def add_rsp(self, value): #7
        self.add_bytes(b'\x48\x81\xc4' + value.to_bytes(4, 'little'))
        return self

    def pop_rbx(self): #1
        self.add_bytes(b'\x5b')
        return self

    def pop_rbp(self): #1
        self.add_bytes(b'\x5d')
        return self

    def pop_rdi(self): #1
        self.add_bytes(b'\x5f')
        return self

    def pop_rsi(self): #1
        self.add_bytes(b'\x5e')
        return self

    def pop_r12(self): #2
        self.add_bytes(b'\x41\x5c')
        return self

    def pop_r13(self): #2
        self.add_bytes(b'\x41\x5d')
        return self

    def pop_r14(self): #2
        self.add_bytes(b'\x41\x5e')
        return self

    def pop_r15(self): #2
        self.add_bytes(b'\x41\x5f')
        return self
