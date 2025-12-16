import re
import os
import datetime
import subprocess
import argparse
from pathlib import Path
from zlib import crc32
from hashlib import sha256
from ctypes import Structure, c_uint32, c_uint8, c_char, c_ubyte, sizeof

assert crc32(b'123456789') == 0xCBF43926
assert sha256(b'123456789').hexdigest() == '15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225'

#--------------------------------------

BIN_HEADER_BEGIN_MAGIC = 0xD72E5F1A
BIN_HEADER_END_MAGIC = 0x48EF7EC5
BIN_HEADER_NAMES_SIZE = 32
BIN_HEADER_SHA256_SIZE = 32

class BIN_HEADER_Version_s(Structure):
    _pack_ = 4
    _fields_ = [
        ('major', c_uint8),
        ('minor', c_uint8),
        ('patch', c_uint8),
        ('RES0', (c_uint8 * 1)),
    ]

assert BIN_HEADER_Version_s.major.offset        == 0x00
assert BIN_HEADER_Version_s.minor.offset        == 0x01
assert BIN_HEADER_Version_s.patch.offset        == 0x02
assert BIN_HEADER_Version_s.RES0.offset         == 0x03
assert sizeof(BIN_HEADER_Version_s)             == 0x04

class BIN_HEADER_FwInfo_s(Structure):
    _pack_ = 4
    _fields_ = [
        ('loadAddr', c_uint32),
        ('bootAddr', c_uint32),
        ('size', c_uint32),
        ('RES0', (c_uint8 * 16)),
        ('hash', c_uint8 * BIN_HEADER_SHA256_SIZE),
        ('crc', c_uint32),
    ]

assert BIN_HEADER_FwInfo_s.loadAddr.offset      == 0x00
assert BIN_HEADER_FwInfo_s.bootAddr.offset      == 0x04
assert BIN_HEADER_FwInfo_s.size.offset          == 0x08
assert BIN_HEADER_FwInfo_s.RES0.offset          == 0x0C
assert BIN_HEADER_FwInfo_s.hash.offset          == 0x1C
assert BIN_HEADER_FwInfo_s.crc.offset           == 0x3C
assert sizeof(BIN_HEADER_FwInfo_s)              == 0x40

class BIN_HEADER_GitInfo_s(Structure):
    _pack_ = 4
    _fields_ = [
        ('rev', c_char * 16),
        ('date', c_char * BIN_HEADER_NAMES_SIZE),
        ('hash', c_uint8 * 20),
    ]

assert BIN_HEADER_GitInfo_s.rev.offset          == 0x00
assert BIN_HEADER_GitInfo_s.date.offset         == 0x10
assert BIN_HEADER_GitInfo_s.hash.offset         == 0x30
assert sizeof(BIN_HEADER_GitInfo_s)             == 0x44

class BIN_HEADER_s(Structure):
    _pack_ = 4
    _fields_ = [
        ('beginMagic', c_uint32),
        ('hdrVer', BIN_HEADER_Version_s),
        ('fwVer', BIN_HEADER_Version_s),
        ('RES1', c_uint8 * 4),
        ('prjName', c_char * BIN_HEADER_NAMES_SIZE),
        ('bcName', c_char * BIN_HEADER_NAMES_SIZE),
        ('fwInfo', BIN_HEADER_FwInfo_s),
        ('RES2', c_uint8 * 16),
        ('gitInfo', BIN_HEADER_GitInfo_s),
        ('RES3', c_uint8 * 20),
        ('endMagic', c_uint32),
        ('crc', c_uint32),
    ]

assert BIN_HEADER_s.beginMagic.offset           == 0x0000
assert BIN_HEADER_s.hdrVer.offset               == 0x0004
assert BIN_HEADER_s.fwVer.offset                == 0x0008
assert BIN_HEADER_s.prjName.offset              == 0x0010
assert BIN_HEADER_s.bcName.offset               == 0x0030
assert BIN_HEADER_s.fwInfo.offset               == 0x0050
assert BIN_HEADER_s.gitInfo.offset              == 0x00A0
assert BIN_HEADER_s.endMagic.offset             == 0x00F8
assert BIN_HEADER_s.crc.offset                  == 0x00FC
assert sizeof(BIN_HEADER_s)                     == 0x0100


class ModifyHeader:
    HEADER_SECTION = '.header'
    def __print_bin(data : bytes):
        for i in range(0, len(data), 16):
            chunk = data[i : i + 16]
            hex_bytes = ' '.join(f'{b:02X}' for b in chunk)
            ascii_bytes = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            print(f'{i:08X}  {hex_bytes:<47}  {ascii_bytes}')


    def __section_fetch(self, section : str = None) -> bytearray:
        res = None
        temp_file_path = Path(self.__bc_path) / Path('temp.bin')
        command = [self.__objcopy, '-O', 'binary']
        if section:
            command.append('--only-section=' + section)
        command.append(self.__elf_file_path)
        command.append(temp_file_path)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            with open(temp_file_path, 'rb') as f:
                res = bytearray(f.read())
            os.remove(temp_file_path)
        return res


    def __section_dump(self, section : str, data : bytearray) -> bool:
        temp_file_path = Path(self.__bc_path) / Path('temp.bin')
        with open(temp_file_path, 'wb') as f:
            f.write(data)
        command = [self.__objcopy, '--update-section', section + '=' + str(temp_file_path), self.__elf_file_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        os.remove(temp_file_path)
        return result.returncode == 0


    def __section_location(self, section : str) -> tuple[int, int]:
        command = [self.__objdump, '-h', self.__elf_file_path]
        sections = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
        for s in sections.split('\n'):
            params = s.split()
            if len(params) > 0 and params[0] == '0':
                file_offset = int(params[4], 16)
            if len(params) > 1 and section == params[1]:
                return (int(params[4], 16) - file_offset, int(params[2], 16))


    def __init__(self, file_path : str, objdump : str, objcopy : str):
        self.__bc_path = Path(file_path).parent
        self.__objdump = objdump
        self.__objcopy = objcopy

        file_path = file_path.rsplit('.', 1)[0]
        extensions = ['.elf', '.exe', '']

        for ext in extensions:
            temp_path = Path(file_path + ext)
            if temp_path.exists():
                self.__elf_file_path = temp_path

        self.__header_image = self.__section_fetch(ModifyHeader.HEADER_SECTION)
        self.__git_exist = False

        if self.__header_image:
            print(f'"Modify: {self.__elf_file_path}"')
            self.__header_struct = BIN_HEADER_s.from_buffer_copy(self.__header_image)
            if self.__header_struct.beginMagic != BIN_HEADER_BEGIN_MAGIC:
                raise Exception('Invalid begin magic value')
            if self.__header_struct.endMagic != BIN_HEADER_END_MAGIC:
                raise Exception('Invalid end magic value')
            header_offset, header_size = self.__section_location(ModifyHeader.HEADER_SECTION)
            if header_size != sizeof(BIN_HEADER_s):
                raise Exception('Invalid header size')
            self.__image_headless = self.__section_fetch()
            self.__image_headless[header_offset : header_offset + header_size] = b'\x00' * header_size

            try:
                status = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
                self.__git_exist = not ('not a git repository' in status.stderr)
                self.__dirty_flag = 'Changes not staged for commit:' in status.stdout
            except:
                print('Git not found')


    def insert_git_revision(self):
        if self.__header_image and self.__git_exist:
            revision = subprocess.run(['git', 'describe', '--tags', '--dirty=-x', '--always'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
            revision = revision.replace('\n', '')
            revision = revision.replace('\r', '')
            revision = revision[:BIN_HEADER_GitInfo_s.rev.size - 1]
            self.__header_struct.gitInfo.rev = revision.encode(encoding='utf-8')
            if re.match(r'\d+\.\d+\.\d+', revision):
                ver_list = re.split('[.|-]', revision)
                if not self.__dirty_flag and len(ver_list) == 3:
                    self.__header_struct.fwVer.major = int(ver_list[0])
                    self.__header_struct.fwVer.minor = int(ver_list[1])
                    self.__header_struct.fwVer.patch = int(ver_list[2])


    def insert_git_time(self):
        if self.__header_image and self.__git_exist:
            if self.__dirty_flag:
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' (dirty)'
            else:
                date = subprocess.run(['git', 'show', '-s', '--format=%ci'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
            date = date.replace('\n', '')
            date = date.replace('\r', '')
            self.__header_struct.gitInfo.date = date.encode(encoding='utf-8')


    def insert_git_hash(self):
        if self.__header_image and self.__git_exist:
            hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
            hash = hash.replace('\n', '')
            hash = hash.replace('\r', '')
            hash = bytearray.fromhex(hash)
            self.__header_struct.gitInfo.hash = type(self.__header_struct.gitInfo.hash).from_buffer_copy(hash)


    def insert_sha256_hash(self):
        if self.__header_image:
            hash = sha256(self.__image_headless).hexdigest()
            hash = bytearray.fromhex(hash)
            self.__header_struct.fwInfo.hash = type(self.__header_struct.fwInfo.hash).from_buffer_copy(hash)


    def insert_firmware_crc(self):
        if self.__header_image:
            self.__header_struct.fwInfo.crc = crc32(self.__image_headless)


    def dump(self):
        if self.__header_image:
            self.__header_struct.crc = 0x00000000
            self.__header_struct.crc = crc32(self.__header_struct)
            self.__header_image = bytearray(self.__header_struct)
            self.__section_dump(ModifyHeader.HEADER_SECTION, self.__header_image)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--file-path', help='Path to executable file', action='store', required=True)
    parser.add_argument('-d', '--objdump', help='Path to objdump', action='store', required=True)
    parser.add_argument('-c', '--objcopy', help='Path to objcopy', action='store', required=True)
    args = parser.parse_args()

    mh = ModifyHeader(args.file_path, args.objdump, args.objcopy)
    mh.insert_git_revision()
    mh.insert_git_time()
    mh.insert_git_hash()
    mh.insert_sha256_hash()
    mh.insert_firmware_crc()
    mh.dump()
