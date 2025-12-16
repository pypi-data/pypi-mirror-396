import re
import argparse

#--------------------------------------

class GccMapParser:
    FORWARD_SLASH_QTY = 2
    RAW_SYMBOL_SECTION_POS = 0
    RAW_SYMBOL_ADDR_POS = 1
    RAW_SYMBOL_SIZE_POS = 2
    RAW_SYMBOL_PATH_POS = 3


    def __init__(self, map_file_path):
        if map_file_path.endswith('.elf') or map_file_path.endswith('.exe'):
            map_file_path = map_file_path[:-4]
        map_file_path = map_file_path + '.map'
        self.__map_file_path = map_file_path
        self.__symbols_list = []
        self.__fill_symbols_list()


    @staticmethod
    def __parse_raw_symbol(raw_symbol):
        module_name = raw_symbol[GccMapParser.RAW_SYMBOL_PATH_POS]
        for _ in range(GccMapParser.FORWARD_SLASH_QTY):
            module_name = module_name[module_name.find('/') + 1 : ]

        symbol_addr = int(raw_symbol[GccMapParser.RAW_SYMBOL_ADDR_POS], 16)
        symbol_size = int(raw_symbol[GccMapParser.RAW_SYMBOL_SIZE_POS], 16) if symbol_addr != 0 else 0

        symbol = {
            'name': raw_symbol[GccMapParser.RAW_SYMBOL_SECTION_POS],
            'module': module_name,
            'addr': symbol_addr,
            'size': symbol_size
        }
        return symbol


    def __fill_symbols_list(self):
        with open(self.__map_file_path) as f:
            map_buf = f.read()
        items_list = re.split(r'[\n\r\t ]', map_buf)
        items_list = [i for i in items_list if i != '']

        self.__symbols_list.clear()
        raw_symbol = []
        raw_symbols_list = []
        items_list_len = len(items_list)

        def is_hex(text : str):
            try:
                _ = int(text, 16)
                return True
            except:
                return False

        for ind in range(items_list_len):
            item = items_list[ind]
            if (bool(re.match(r'^\..', item)) or (ind == items_list_len - 1)) and len(raw_symbol) > 0:
                symbol_check_ok = True
                try:
                    #symbol_check_ok = symbol_check_ok and bool(re.match(r'^\.(.*)\.[^*]', raw_symbol[0]))
                    symbol_check_ok = symbol_check_ok and is_hex(raw_symbol[1])
                    symbol_check_ok = symbol_check_ok and is_hex(raw_symbol[2])
                    symbol_check_ok = symbol_check_ok and ('.o' in raw_symbol[3])
                    symbol_check_ok = symbol_check_ok and (len(raw_symbol) >= 4)
                    #symbol_check_ok = symbol_check_ok and ((len(raw_symbol) == 4) or (raw_symbol[5] == '(size') and raw_symbol[6] == 'before' and raw_symbol[7] == 'relaxing)')
                except:
                    symbol_check_ok = False

                if symbol_check_ok:
                    symbol = GccMapParser.__parse_raw_symbol(raw_symbol[:4])
                    self.__symbols_list.append(symbol)
                    raw_symbols_list.append(raw_symbol[:4])

                raw_symbol.clear()
            raw_symbol.append(item)


    def get_symbols_list(self, sort_by_size=True, no_zero_size=True, filters=None):
        if filters is None:
            start_catch_patterns = ['.isr_vector', '.init', '.fini', '.preinit_array', 'init_array', '.fini_array', '.text', '.data', '.sdata', '.rodata', '.rela']
        else:
            start_catch_patterns = filters

        symbols_list = []
        for symbol in self.__symbols_list:
            cmp_flag = False
            for ptn in start_catch_patterns:
                cmp_flag = cmp_flag or bool(re.match(rf'^{ptn}\..', symbol['name'])) or symbol['name'] == ptn
            if cmp_flag:
                symbols_list.append(symbol)

        if sort_by_size:
            symbols_list = sorted(symbols_list, reverse=False, key=lambda symbol: symbol['size'])
        if no_zero_size:
            symbols_list = [s for s in symbols_list if s['size'] != 0]
        return symbols_list


    def get_modules_list(self, sort_by_size=True, no_zero_size=True, filters=None):
        modules_list = []
        module = {
            'name': '',
            'list': [],
            'size': 0
        }
        symbols_list = self.get_symbols_list(sort_by_size, no_zero_size, filters)
        symbols_list = sorted(symbols_list, reverse=False, key=lambda symbol: symbol['module'])

        for symbol in symbols_list:
            cur_module_name = symbol['module']
            if module['name'] != cur_module_name:
                if len(module['list']) > 0:
                    if sort_by_size:
                        module['list'] = sorted(module['list'], reverse=True, key=lambda symbol: symbol['size'])
                    modules_list.append(module.copy())
                module['name'] = cur_module_name
                module['list'] = module['list'].copy()
                module['list'].clear()
                module['size'] = 0
            module['list'].append(symbol)
            module['size'] += symbol['size']

        if len(module['list']) != 0:
            if sort_by_size:
                module['list'] = sorted(module['list'], reverse=True, key=lambda symbol: symbol['size'])
            modules_list.append(module.copy())

        if sort_by_size:
            modules_list = sorted(modules_list, reverse=False, key=lambda module: module['size'])
        return modules_list


    @staticmethod
    def __symb_str(name, module, addr, size):
        try:
            return f"{name:48} {module:48}    {addr:08X}    {size}\n"
        except:
            return f"{name:48} {module:48}    {addr:8}    {size}\n"


    def get_symbols_str(self, sort_by_size=True, no_zero_size=True, filters=None):
        symbols_list = self.get_symbols_list(sort_by_size, no_zero_size, filters)
        out_str = self.__symb_str('Symbol name', 'Module name', 'Address', 'Size')
        total_size = 0
        for symbol in symbols_list:
            total_size = total_size + symbol['size']
            out_str += self.__symb_str(symbol['name'], symbol['module'], symbol['addr'], symbol['size'])
        out_str += f'\ntotal size: {total_size} ({hex(total_size)})'
        return out_str


    @staticmethod
    def __mod_str(module, size, qty):
        return f"{module:60}    {size:<16}    {qty:<16}\n"


    def get_modules_str(self, sort_by_size=True, no_zero_size=True, filters=None, only_modules=True):
        modules_list = self.get_modules_list(sort_by_size, no_zero_size, filters)
        out_str = self.__mod_str('Module name', 'Module size', 'Symbols qty')
        total_size = 0
        for module in modules_list:
            total_size = total_size + module['size']
            out_str += self.__mod_str(module['name'], module['size'], len(module['list']))
            if not only_modules:
                out_str += '    ' + self.__symb_str('Symbol name', 'Module name', 'Address', 'Size')
                for symbol in module['list']:
                    out_str += '    ' + self.__symb_str(symbol['name'], symbol['module'], symbol['addr'], symbol['size'])
                out_str += '\n'
        out_str += f'\ntotal size: {total_size}'
        return out_str


    def gcc_map_parser(self, log_file=None, modules=False, sort_by_size=True, no_zero_size=True, filters=None, only_modules=True):
        if modules:
            out_str = self.get_modules_str(sort_by_size, no_zero_size, filters, only_modules)
        else:
            out_str = self.get_symbols_str(sort_by_size, no_zero_size, filters)

        if log_file is None:
            print(out_str)
        else:
            with open(log_file, 'w+', encoding='utf-8') as f:
                f.write(out_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--file-path', help='Map file path for parsing filters and symbols', action='store', required=True)
    parser.add_argument('-l', '--log-file', help='Out file name with parse log', action='store', default=None)
    parser.add_argument('-m', '--modules', help='Combine symbols in modules', action='store_true')
    parser.add_argument('-s', '--sort-by-size', help='Sorting lists by items size', action='store_true')
    parser.add_argument('-z', '--no-zero-size', help='Exclude zero size symbols', action='store_true')
    parser.add_argument('-f', '--filters', help='Include only user spec filters', action='store', type=str, nargs='+')
    parser.add_argument('-o', '--only-modules', help='Include only modules info in out log', action='store_true')
    args = parser.parse_args()
    parser = GccMapParser(args.file_path)
    parser.gcc_map_parser(args.log_file, args.modules, args.sort_by_size, args.no_zero_size, args.filters, args.only_modules)
